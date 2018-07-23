"""Utilities for working with signals.

Examples:

  @signals.REQUEST_START.connect
  def Log(unused_sender):
    print 'New request started.'

  @signals.MODEL_POST_PUT.connect_via('MyModel')
  def Process(sender, model=None, entity=None, ctx_options=None):
    if ctx_options.get('process', False):
      # Do something with entity here.

See Blinker documentation for more details: http://pythonhosted.org/blinker/
"""

import functools
import threading

import blinker

from google.appengine.ext import ndb


INSTANCE_WARMUP = blinker.Signal(
    doc="""Fired when a frontend warmup or module start request is made.

    This signal is not guaranteed to fire for all instances.

    Args:
      sender: None.
    """)


REQUEST_START = blinker.Signal(
    doc="""Fired at the beginning of a request.

    Args:
      sender: None.
    """)


REQUEST_END = blinker.Signal(
    doc="""Fired at the end of a request, possibly multiple times.

    If any connected receiver returns a truthy value, the signal will be fired
    again, up to a maximum of 10 times.

    RECEIVERS MUST BE IDEMPOTENT!

    Otherwise, to restrict a receiver to only running once, connect via
    sender=0.

    Args:
      sender: int, the iteration counter.
    """)


MODEL_PRE_DELETE = blinker.Signal(
    doc="""Fired before Key.delete().

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      key: object, ndb.Key instance to be deleted.
    """)


MODEL_POST_DELETE = blinker.Signal(
    doc="""Fired after Key.delete().

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      key: object, ndb.Key instance that was deleted.
    """)


MODEL_PRE_GET = blinker.Signal(
    doc="""Fired before Key.get().

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      key: object, ndb.Key instance to be retrieved.
    """)


MODEL_POST_GET = blinker.Signal(
    doc="""Fired after Key.get().

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      entity: object, ndb.Model subclass instance that was retrieved.
    """)


MODEL_PRE_PUT = blinker.Signal(
    doc="""Fired before entity.put(). Receivers for this signal can be tasklets.

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      entity: object, ndb.Model subclass instance to be saved.
      ctx_options: dict, additional context options passed to put().
    """)


MODEL_POST_PUT = blinker.Signal(
    doc="""Fired after entity.put(). Receivers for this signal can be tasklets.

    Args:
      sender: str, kind name.
      model: type, ndb.Model subclass.
      entity: object, ndb.Model subclass instance that was saved.
      ctx_options: dict, additional context options passed to put().
    """)


class Error(Exception):
  """Base signals error."""
  pass


class RequestMaxIterations(Error):
  """REQUEST_END maximum iterations reached."""
  pass


_MAX_REQUEST_END_ITERATIONS = 10


class TopLevel(object):
  """Decorator/middleware for request signals."""

  def __init__(self, wrapped):
    """Initializes the decorator."""
    try:
      functools.update_wrapper(self, wrapped)
    except AttributeError:
      pass
    self._wrapped = wrapped

  def __get__(self, instance, unused_owner):
    """Makes the decorator work on class methods."""
    return functools.partial(self, instance)

  def __call__(self, *args, **kwargs):
    """Runs the wrapped function."""
    REQUEST_START.send()
    try:
      return self._wrapped(*args, **kwargs)
    finally:
      counter = 0
      # Always fire signal even if there's an exception.
      while any(result for _, result in REQUEST_END.send(counter)):
        counter += 1
        if counter >= _MAX_REQUEST_END_ITERATIONS:
          raise RequestMaxIterations(RequestMaxIterations.__doc__)


# Valid NDB context options. All others will be filtered out.
# pylint: disable=protected-access
_NDB_CONTEXT_OPTIONS = set(ndb.ContextOptions._options.iterkeys())
# pylint: enable=protected-access


class SignalMixin(object):
  """Model mixin for signals.

  Note: pre and post get hooks are not fired for queries.
  """
  # TODO(davbennett): The delete and get signals all have issues with
  # asynchronous code (max recursion errors). They need to be refactored to
  # work like the put signals.

  @classmethod
  def _pre_delete_hook(cls, key):  # pylint: disable=invalid-name
    """Hook that runs before Key.delete()."""
    super(SignalMixin, cls)._pre_delete_hook(key)
    kind = cls._get_kind()
    if MODEL_PRE_DELETE.has_receivers_for(kind):
      MODEL_PRE_DELETE.send(kind, model=cls, key=key)

  @classmethod
  def _post_delete_hook(cls, key, future):  # pylint: disable=invalid-name
    """Hook that runs after Key.delete()."""
    super(SignalMixin, cls)._post_delete_hook(key, future)
    kind = cls._get_kind()
    if MODEL_POST_DELETE.has_receivers_for(kind):
      MODEL_POST_DELETE.send(kind, model=cls, key=key)

  @classmethod
  def _pre_get_hook(cls, key):  # pylint: disable=invalid-name
    """Hook that runs before Key.get() when getting an entity of this model."""
    super(SignalMixin, cls)._pre_get_hook(key)
    kind = cls._get_kind()
    if MODEL_PRE_GET.has_receivers_for(kind):
      MODEL_PRE_GET.send(kind, model=cls, key=key)

  @classmethod
  def _post_get_hook(cls, key, future):  # pylint: disable=invalid-name
    """Hook that runs after Key.get() when getting an entity of this model."""
    # TODO(davbennett): Look into using _from_pb for post-get signal instead.
    super(SignalMixin, cls)._post_get_hook(key, future)
    kind = cls._get_kind()
    if MODEL_POST_GET.has_receivers_for(kind):
      MODEL_POST_GET.send(kind, model=cls, entity=future.get_result())

  @ndb.tasklet
  def _put_async(self, **ctx_options):  # pylint: disable=invalid-name
    """Writes the entity's data to the Datastore. Returns the entity's Key."""
    kind = self._get_kind()
    if MODEL_PRE_PUT.has_receivers_for(kind):
      yield SendAsync(MODEL_PRE_PUT, kind, model=self.__class__, entity=self,
                      ctx_options=ctx_options)
    # Filter out options that don't apply to NDB to prevent exceptions.
    ndb_ctx_options = {k: v for k, v in ctx_options.iteritems()
                       if k in _NDB_CONTEXT_OPTIONS}
    key = yield super(SignalMixin, self)._put_async(**ndb_ctx_options)
    if MODEL_POST_PUT.has_receivers_for(kind):
      yield SendAsync(MODEL_POST_PUT, kind, model=self.__class__, entity=self,
                      ctx_options=ctx_options)
    raise ndb.Return(key)
  put_async = _put_async


@ndb.tasklet
def SendAsync(signal, sender, **kwargs):  # pylint: disable=invalid-name
  """A wrapper for sending signals asynchronously.

  Args:
    signal: blinker.Signal, the signal to send.
    sender: *, the signal sender.
    **kwargs: keyword parameters sent to receivers.

  Yields:
    The original results with all futures resolved.
  """
  results = signal.send(sender, **kwargs)
  futures = []
  for unused_receiver, result in results:
    if isinstance(result, ndb.Future):
      futures.append(result)
  if futures:
    yield futures
  raise ndb.Return(results)


def RunOnce(func):  # pylint: disable=invalid-name
  """Function decorator that prevents multiple calls with same positional args.

  Args:
    func: the function to be wrapped.

  Returns:
    The wrapped function.

  Raises:
    RuntimeError: if the wrapped function is called more than once.
  """
  call_lock = threading.Lock()
  called = set()
  func_name = '.'.join([func.__module__, func.__name__])

  @functools.wraps(func)
  def Wrapper(*args, **kwargs):  # pylint: disable=invalid-name
    key = tuple(args)
    with call_lock:
      if key in called:
        raise RuntimeError('%r already called with args: %r' % (func_name, key))
      called.add(key)
    return func(*args, **kwargs)

  return Wrapper


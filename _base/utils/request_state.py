"""Utility functions for maintaining thread-local request state.

GetRequestState returns a dictionary which can be updated by the user.

GetRequestVar and SetRequestVar are used to manage individual values of any
kind.
"""

import os
import threading


_REQUEST_STATE_KEY = '__REQUEST_STATE__'
_VARIABLES = '*VARIABLES*'

_state = threading.local()


def GetRequestState(name):
  """Returns the named request state dict.

  A new instance is created for each new HTTP request.  We determine
  that we're in a new request by inspecting os.environ, which is reset
  at the start of each request.  Also, each thread gets its own dict.

  Args:
    name: str, a valid Python identifier.

  Returns:
    dict, thread-local request state.
  """
  rs = getattr(_state, name, None)
  if not os.getenv(_REQUEST_STATE_KEY) and rs is not None:
    rs.clear()
    setattr(_state, name, None)
    rs = None
  if rs is None:
    rs = {}
    setattr(_state, name, rs)
    os.environ[_REQUEST_STATE_KEY] = '1'
  return rs


def GetRequestVar(name, default=None):
  """Return a value from the request state.

  Args:
    name: str, the name of the value.
    default: value to return if there is no value set.

  Returns:
    any type, the value last stored under name.
  """
  rs = GetRequestState(_VARIABLES)
  return rs.get(name, default)


def SetRequestVar(name, val):
  """Set a value in the request state.

  Args:
    name: str, the name of the value.
    val: any, the value to set.
  """
  rs = GetRequestState(_VARIABLES)
  rs[name] = val

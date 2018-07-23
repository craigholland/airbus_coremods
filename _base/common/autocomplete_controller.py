"""Autocomplete Controller Methods."""

import logging

from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.errors import error_msg


def GetAutoComplete(model, error_collector, keyword='', limit=10):
  """Get suggestions for auto-complete.

  Args:
    model: class, the model to search.
    error_collector: error_collector.Errors(), the error collector.
    keyword: string, search keyword.
    limit: int, max number of results.

  Returns:
    Two-tuple, first item is List<two-tuple>: (id, field), second item is bool,
    True if there are more results than returned.
  """
  if not model:
    error_collector.Add(None, error_msg.MODEL_NOT_FOUND)
    return [], False
  if hasattr(model, 'fk_display'):
    keyword_filter_field = model.fk_display
    searched_field = 'fk_display'
  elif hasattr(model, 'name'):
    keyword_filter_field = model.name
    searched_field = 'name'
  else:
    return _GetAutoCompleteKeyName(model, keyword, limit)
  if not keyword:
    query = model.query(projection=[searched_field], distinct=True)
    results = query.fetch(limit)
  else:
    for keyw in (keyword, keyword.upper(), keyword.lower(), keyword.title()):
      query = model.query(projection=[searched_field], distinct=True)
      query = query.filter(keyword_filter_field >= keyw,
                           keyword_filter_field < keyw + '~')
      results = query.fetch(limit)
      if results:
        break
  more = query.count(limit=limit + 1) > limit
  results = [(r.key.id(), getattr(r, searched_field))
             for r in results]
  logging.info('Autocomplete, kind: %s, keyword: %s, #results: %d',
               model, keyword, len(results))
  return results, more


def _GetAutoCompleteKeyName(model, keyword='', limit=10):
  """Get suggestions for auto-complete by searching key_name.

  Args:
    model: class, the model to search.
    keyword: string, search keyword.
    limit: int, max number of results.

  Returns:
    Two-tuple, first item is List<two-tuple>: (id, field), second item is bool,
    True if there are more results than returned.
  """
  if not hasattr(model, 'key_name'):
    return [], False

  if not keyword:
    query = model.query()
    results = query.fetch(limit, keys_only=True)
  else:
    kind = model._get_kind()  # pylint: disable=protected-access
    qstr = 'SELECT __key__ FROM %s WHERE __key__ >= :1 AND __key__ < :2' % kind
    unfiltered_query = ndb.gql(qstr)
    for keyw in (keyword, keyword.upper(), keyword.lower()):
      query = unfiltered_query.bind(ndb.Key(kind, keyw),
                                    ndb.Key(kind, keyw + '~'))
      results = query.fetch(limit)
      if results:
        break
  more = query.count(limit=limit + 1) > limit
  results = [(key.id(),) * 2 for key in results]
  logging.info('Autocomplete, kind: %s, keyword: %s, #results: %d',
               model, keyword, len(results))
  return results, more

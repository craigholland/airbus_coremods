"""Utilities for working with user info."""

import logging
import os

# from apiclient import discovery
# import httplib2
# from oauth2client_1_4_12_plus import appengine as oauth2_appengine
#
# from google.appengine.api import app_identity
# from google.appengine.api import memcache
from google.appengine.api import users

# from google3.apphosting.api import stubby
# from google3.corp.accounts.orgstore import client
# from _base.utils import memoize
#
# from google3.ops.netdeploy.netdesign.server.utils import authz
# from _base.utils import constants

#
# _GROUPER_CONNECTION = 'gslb:orgstoregrouper'  # Constant for orgstore client.
# _GDOMAIN_SUFFIX = '@google.com'
# _CACHE_TIMEOUT = 600  # 10 minutes.
_UNKNOWN = 'UNKNOWN'
#
#
# class GrouperConnectionError(Exception):
#   """Class to represent RPC errors to grouper."""
#   pass
#
#
# def IsCurrentUserServiceAccount():
#   """Check if the current user is a service account user.
#
#   Returns:
#     bool, True if user is service account user otherwise False.
#   """
#   # TODO(rupalig): Find out an service account API to detect if user is SA user.
#   return constants.SA_ACCOUNT_SUFFIX in GetCurrentUserLdap()


def GetCurrentUserLdap():
  """Get the current user ldap.

  Returns:
    str, the current user ldap.
  """
  user = users.get_current_user()
  return user.nickname() if user else _UNKNOWN

#
# def GetCurrentUserEmail():
#   """Get the current user's email.
#
#   Returns:
#     str, the current user's email id.
#   """
#   user = users.get_current_user()
#   return user.email() if user else None
#
#
# def GetCurrentUserGroups(strip=False):
#   """Get the current user's groups.
#
#   Args:
#     strip: bool, strip the prepended %.
#
#   Returns:
#     list<str>, the current user's groups.
#   """
#   return authz.GetGroups(method=GetAuthMethod(), strip=strip)
#
#
# def GetUserContext():
#   """Returns dictionary to generate user context."""
#   return {f: os.environ.get(f) for f in constants.USER_CONTEXT_FIELDS}
#
#
# def SetUserContext(context):
#   """Sets appropriate environment variables for user context."""
#   for field in constants.USER_CONTEXT_FIELDS:
#     os.environ[field] = context.get(field) or ''
#
#
# def GetAuthMethod():
#   """Gets the current auth method based on HTTP header override."""
#   # TODO(raulg): This method should default to constants.AUTH_METHOD_COOKIE.
#   # The code will be reverted back, when the failure to store all required
#   # user groups in the cookie has been fixed.
#   return os.environ.get(
#       constants.AUTH_METHOD_HEADER, constants.AUTH_METHOD_REST)
#
#
# def SetAuthMethod(method):
#   """Sets HTTP header for overriding auth method."""
#   os.environ[constants.AUTH_METHOD_HEADER] = method
#
#
# def IsCurrentUserInGroup(group):
#   """Returns True if the user is in the supplied group."""
#   strip = group and group[0] != '%'
#   return group in GetCurrentUserGroups(strip=strip)
#
#
# def IsCurrentUserInAnyGroup(*groups):
#   """Returns True if the user is in any of the supplied groups."""
#   return any(IsCurrentUserInGroup(g) for g in groups)
#
#
# def IsUserAdmin():
#   """Checks if the current user is admin user.
#
#   Returns:
#     True|Flase based on if user is ADMIN or not.
#   """
#   return IsCurrentUserInGroup(constants.DH_ADMIN_GROUP)
#
#
# def IsCurrentUserIn(*usernames):
#   """Determines if the current user is in the list of usernames.
#
#   Does fuzzy matching, so the usernames can be LDAPs or full email addresses.
#
#   Args:
#     *usernames: zero or more strings representing usernames.
#
#   Returns:
#     True, of the current user is in the list of usernames, False otherwise.
#   """
#   current_username = GetCurrentUserEmail()
#   if current_username:
#     for username in usernames:
#       if username and FuzzyUserMatch(username, current_username):
#         return True
#   return False
#
#
# def FuzzyUserMatch(username1, username2):
#   """Returns True if the user nickname, email or ldaps are equal.
#
#   Args:
#     username1: str, user nickname, ldap or email.
#     username2: str, user nickname, ldap or email.
#
#   Returns:
#     bool, returns True if the usernames are equal.
#   """
#   if username1 and username2:
#     return username1.split('@')[0] == username2.split('@')[0]
#   return False
#
#
# @memoize.Memoize(warn_on_error=False, timeout=_CACHE_TIMEOUT)
# def GetGrouperClient(connection):
#   """Reuse grouper client."""
#   return client.Client(connection)
#
#
# @memoize.Memoize(warn_on_error=False, timeout=_CACHE_TIMEOUT)
# def IsUser(ldap):
#   """Ensures the given value is a valid LDAP.
#
#   Args:
#     ldap: str, LDAP to test.
#
#   Returns:
#     boolean, True if the ldap is valid else False.
#
#   Raises:
#     GrouperConnectionError, for stubby or apiproxy errors.
#   """
#   if app_identity.get_application_id() == constants.APP_IDENTITY_DEVAPPSERVER:
#     return True
#
#   if ldap and ldap.endswith(_GDOMAIN_SUFFIX):
#     ldap = ldap.split('@')[0]
#   grouper_client = GetGrouperClient(_GROUPER_CONNECTION)
#   try:
#     grouper_client.UserInfo(ldap)
#   except stubby.RPCApplicationError as e:
#     if e.error_code is 2:  # 2 is UNKNOWN_USER
#       return False
#     else:
#       logging.exception(e.message)
#       raise GrouperConnectionError(e.message)
#   return True
#
#
# @memoize.Memoize(memoize_parallel_calls=True)
# def GetService(api_name, api_version, scope, discovery_url):
#   """Builds a service for accessing an external API.
#
#   Args:
#     api_name: str, the API name.
#     api_version: str, the API version.
#     scope: str, the API scope.
#     discovery_url: str, a URI Template that points to the location of
#       the discovery service. It should have two parameters {api} and
#       {apiVersion} that when filled in produce an absolute URI to the discovery
#       document for that service.
#
#   Returns:
#     api_client.discovery.Resource, a Resource object with methods for
#     interacting with the service.
#   """
#   # Create app credentials with the proper scope.
#   credentials = oauth2_appengine.AppAssertionCredentials(scope)
#
#   # Authorize HTTP traffic with an OAuth2 token.
#   http = credentials.authorize(httplib2.Http(cache=memcache))
#
#   # Load the Service.
#   service = discovery.build(
#       api_name, api_version, http=http, discoveryServiceUrl=discovery_url)
#
#   return service

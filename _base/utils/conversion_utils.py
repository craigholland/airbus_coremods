"""Functions for converting one data type to another."""

import calendar
import collections
import datetime
import decimal
import functools
import re

import dateutil.parser

from google.appengine.api import datastore_errors
from google.appengine.api import users
from google.appengine.ext import ndb
from google.net.proto import ProtocolBuffer

from google3.pyglib import datelib

from google3.ops.netdeploy.netdesign.server.utils import constants


_DEFAULT = object()  # sentinel object to detect default.
_EPOCH = datetime.datetime.utcfromtimestamp(0)  # Zero POSIX timestamp.
_TIME_PATTERN = r'\d{2}:\d{2}:\d{2}(\.\d{1,6})?[Zz]?'
_DATE_PATTERN = r'\d{4}-\d{2}-\d{2}'
_TIME_RE = re.compile('^%s$' % _TIME_PATTERN)
_DATE_RE = re.compile('^%s$' % _DATE_PATTERN)
_DATETIME_RE = re.compile('^%s[Tt ]%s$' % (_DATE_PATTERN, _TIME_PATTERN))
_DECIMAL_PRECISION = decimal.Decimal('0.01')


class ConversionError(Exception):
  """Error converting types."""


def IsDateStr(s):
  """Determines if a string is a RFC3339 date format."""
  return isinstance(s, basestring) and _DATE_RE.match(s)


def IsTimeStr(s):
  """Determines if a string is a RFC3339 time format (no offset)."""
  return isinstance(s, basestring) and _TIME_RE.match(s)


def IsDateTimeStr(s):
  """Determines if a string is a RFC3339 datetime format (no offset)."""
  return isinstance(s, basestring) and _DATETIME_RE.match(s)


class _UTC(datetime.tzinfo):
  """UTC timezone."""

  def utcoffset(self, unused_dt):
    return datetime.timedelta(0)

  def tzname(self, unused_dt):
    return 'UTC'

  def dst(self, unused_dt):
    return datetime.timedelta(0)


def _TimeToStr(t):
  if t.utcoffset():
    d = datetime.datetime.combine(datetime.date.today(), t)
    d = d.astimezone(_UTC()).replace(tzinfo=None)
    t = d.time()
  return t.isoformat() + 'Z'


def _DateToStr(d):
  return d.isoformat()


def _DateTimeToStr(dt):
  if dt.utcoffset():
    dt = dt.astimezone(_UTC()).replace(tzinfo=None)
  return dt.isoformat() + 'Z'


def DateObjToStr(obj):
  """Converts a date, time or datetime to an RFC 3339 string.

  Args:
    obj: datetime.date, datetime.time, datetime.datetime instance.

  Returns:
    str, RFC 3339 formatted string.

  Raises:
    TypeError: if obj isn't the correct type.
  """
  if isinstance(obj, datetime.datetime):
    return _DateTimeToStr(obj)
  if isinstance(obj, datetime.date):
    return _DateToStr(obj)
  if isinstance(obj, datetime.time):
    return _TimeToStr(obj)
  raise TypeError('Invalid type for obj: %r' % type(obj))


def DateStrToTimeStamp(datestr):
  """Converts an RFC3339 string to corresponding Unix timestamp value."""
  return calendar.timegm(
      datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S').utctimetuple())


def NoOp(*types):
  """Decorator for conversion functions to no-op proper data types.

  If the conversion function receives an object of one of the given types, it
  returns it immediately, unaltered. Otherwise, it attempts the conversion.

  Args:
    *types: tuple of Python types the conversion function returns.

  Returns:
    The conversion function decorated to return instances of the types
    unaltered.
  """
  def Decorator(conversion_func):
    @functools.wraps(conversion_func)
    def Convert(value, default=_DEFAULT, *args, **kwargs):
      if type(value) in types:
        return value
      return conversion_func(value, default, *args, **kwargs)
    return Convert
  return Decorator


@NoOp(unicode)
def ToUnicode(value, default=_DEFAULT):
  """Return a value converted to a string, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: unicode, the default value to return.

  Returns:
    The converted value or default unicode.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    if isinstance(value, basestring):
      return unicode(value, 'utf-8')
    else:
      return unicode(value)
  except (UnicodeDecodeError, ValueError):
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to unicode' % value)
    return default


@NoOp(int, long)
def ToInt(value, default=_DEFAULT):
  """Return a value converted to an integer, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: integer, the default value to return.

  Returns:
    The converted value or default integer.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  if isinstance(value, (datetime.date, datetime.time)):
    dt = ToDateTime(value) - _EPOCH
    return dt.microseconds + 1000000 * (dt.seconds + 24 * 3600 * dt.days)
  try:
    return int(str(value))
  except ValueError:
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to int' % value)
    return default


@NoOp(decimal.Decimal)
def ToDecimal(value, default=_DEFAULT):
  """Return a value converted to a decimal, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: decimal, the default value to return.

  Returns:
    The converted value or default decimal.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    return decimal.Decimal(str(value))
  except (ValueError, decimal.InvalidOperation):
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to decimal' % value)
    return default


@NoOp(float)
def ToFloat(value, default=_DEFAULT):
  """Return a value converted to a float, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: float, the default value to return.

  Returns:
    The converted value or default float.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    return float(str(value))
  except ValueError:
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to float' % value)
    return default


@NoOp(int)
def SafeInt(value, default=_DEFAULT):
  """Strips non-integer characters before casting to integer."""
  if default is _DEFAULT:
    default = 0
  return ToInt(re.sub(r'[^0-9]+', '', str(value)), default)


@NoOp(float)
def SafeFloat(value, default=_DEFAULT):
  """Strips non-float characters before casting to float."""
  if default is _DEFAULT: default = 0.0
  return ToFloat(re.sub(r'[^0-9.]+', '', str(value)), default)


@NoOp(decimal.Decimal)
def SafeDecimal(value, default=_DEFAULT):
  """Strips non-decimal characters before casting to decimal."""
  if default is _DEFAULT: default = decimal.Decimal('0.00')
  return ToDecimal(re.sub(r'[^0-9.\-]+', '', str(value)), default)


def SafeUnicode(value, default=_DEFAULT):
  """Strips space at left and right end of a str before casting to Unicode."""
  default = '' if default is _DEFAULT else default
  return ToUnicode(value.strip(), default)


def ToCurrency(value, default=_DEFAULT, precision=_DECIMAL_PRECISION,
               rounding=decimal.ROUND_HALF_UP):
  """Strips non-decimal characters before converting and casting to string.

  Args:
    value: *, the value to convert.
    default: decimal, the default value to return.
    precision: decimal, the default decimal precision.
    rounding: the rounding rule for the decimal.

  Returns:
    The converted value or default string.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  currency = SafeDecimal(value, default)
  if isinstance(currency, decimal.Decimal):
    currency = currency.quantize(precision, rounding)
  return currency if currency is None else unicode(currency)


@NoOp(bool)
def ToBool(value, default=_DEFAULT):
  """Return a value converted to a boolean, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: boolean, the default value to return.

  Returns:
    The converted value or default boolean.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  value = str(value).lower()
  if value in constants.TRUE_VALUES:
    return True
  if value in constants.FALSE_VALUES:
    return False
  if default is _DEFAULT:
    raise ConversionError('Cannot convert %r to bool' % value)
  return default


@NoOp(datetime.date)
def ToDate(value, default=_DEFAULT):
  """Return a value converted to a date, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: date, the default value to return.

  Returns:
    The converted value or default date.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    result = ToDateTime(value, default)
  except ConversionError:
    raise ConversionError('Cannot convert %r to date' % value)
  if result is default:
    return result
  return result.date()


@NoOp(datetime.time)
def ToTime(value, default=_DEFAULT):
  """Return a value converted to a time, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: time, the default value to return.

  Returns:
    The converted value or default time.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    result = ToDateTime(value, default)
  except ConversionError:
    raise ConversionError('Cannot convert %r to time' % value)
  if result is default:
    return result
  return result.time()


@NoOp(datetime.datetime)
def ToDateTime(value, default=_DEFAULT):
  """Return a value converted to a datetime, or a default if conversion fails.

  Time values will converted relative to UTC epoch.

  Args:
    value: *, the value to convert.
    default: datetime, the default value to return.

  Returns:
    The converted value or default datetime.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    if isinstance(value, datetime.date):
      return datetime.datetime(value.year, value.month, value.day)
    elif isinstance(value, datetime.time):
      return datelib.ReplaceTimezone(_EPOCH.replace(
          hour=value.hour, minute=value.minute, second=value.second,
          microsecond=value.microsecond), value.tzinfo)
    elif isinstance(value, (int, long)):
      return _EPOCH + datetime.timedelta(microseconds=value)
    elif not str(value):
      # dateutil parses empty strings as current datetime which we don't want.
      raise ValueError
    return dateutil.parser.parse(str(value), ignoretz=True, default=_EPOCH)
  except ValueError:
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to datetime' % value)
    return default


@NoOp(ndb.Key)
def ToKey(value, default=_DEFAULT):
  """Return a value converted to a Key, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: ndb.Key, the default value to return.

  Returns:
    The converted value or default Key.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    return ndb.Key(urlsafe=str(value))
  except (TypeError, ProtocolBuffer.ProtocolBufferDecodeError):
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to ndb.Key' % value)
    return default


@NoOp(ndb.GeoPt)
def ToGeoPt(value, default=_DEFAULT):
  """Return a value converted to a Key, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: ndb.Key, the default value to return.

  Returns:
    The converted value or default Key.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  try:
    if (isinstance(value, collections.Iterable) and not
        isinstance(value, basestring)):
      return ndb.GeoPt(*value)
    else:
      return ndb.GeoPt(str(value))
  except (TypeError, datastore_errors.BadValueError):
    if default is _DEFAULT:
      raise ConversionError('Cannot convert %r to ndb.GeoPt' % value)
    return default


@NoOp(users.User)
def ToUser(value, default=_DEFAULT):
  """Return a value converted to a User, or a default if conversion fails.

  Args:
    value: *, the value to convert.
    default: google.appengine.api.users.User, the default value to return.

  Returns:
    The converted value or default User.

  Raises:
    ConversionError: if type conversion fails and no default is given.
  """
  if isinstance(value, basestring):
    value = value.strip()
    if value:
      if '@' not in value:
        value += '@google.com'
      return users.User(value)
  if default is _DEFAULT:
    raise ConversionError('Cannot convert %r to User' % value)
  return default

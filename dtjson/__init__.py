# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

import collections
import datetime
import json
import logging
import pytz
import warnings

__author__ = 'Ignacio Rossi'
__email__ = 'rossi.ignacio@gmail.com '
__version__ = '0.0.1-dev'

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DT_NAME = '__dtjson_name__'
DT_DATA = '__dtjson_data__'

Serializer = collections.namedtuple('Serializer', ['clz', 'name', 'from_json',
                                                   'to_json'])


def _warn_missing_tz(tzinfo, message):
    warnings.warn("The tzinfo {!r} {}. Encoding with UTC timezone.".format(
        tzinfo, message))


def _date_to_json(date):
    return [date.year, date.month, date.day, ]


def _date_from_json(json_obj):
    return datetime.date(*json_obj)


def _datetime_to_json(dtime):
    def _dt_values(date):
        return [date.year, date.month, date.day, date.hour, date.minute,
                date.second, date.microsecond]

    if dtime.utcoffset() is not None:
        # Aware
        try:
            timezone = dtime.tzinfo.zone
        except AttributeError:
            timezone = None
        if timezone is None:
            _warn_missing_tz(dtime.tzinfo, "has no timezone name")
            timezone = pytz.utc.zone
        elif timezone not in pytz.all_timezones_set:
            _warn_missing_tz(
                dtime.tzinfo,
                "has an invalid timezone name: '{}'".format(timezone))
            timezone = pytz.utc.zone

        as_utc = pytz.utc.normalize(dtime)
        utc_values = _dt_values(as_utc)
    else:
        # Naive
        timezone = None
        utc_values = _dt_values(dtime)
    return {'timezone': timezone, 'utc_values': utc_values, }


def _datetime_from_json(json_obj):
    timezone = json_obj['timezone']
    naive = datetime.datetime(*json_obj['utc_values'])
    if timezone is None:
        return naive
    else:
        return pytz.timezone(timezone).normalize(pytz.utc.localize(naive))

# First match serializes
_SERIALIZERS = (
    Serializer(clz=datetime.datetime,
               name='__datetime__',
               from_json=_datetime_from_json,
               to_json=_datetime_to_json),
    Serializer(clz=datetime.date,
               name='__date__',
               from_json=_date_from_json,
               to_json=_date_to_json),
)  # yapf: disable


_SERIALIZER_FROM_NAME = {s.name: s for s in _SERIALIZERS}


def dtjson_default(obj):
    for serializer in _SERIALIZERS:
        if isinstance(obj, serializer.clz):
            return {DT_NAME: serializer.name, DT_DATA: serializer.to_json(obj)}
    raise TypeError


def dtjson_object_hook(obj):
    if DT_NAME in obj and DT_DATA in obj:
        try:
            serializer = _SERIALIZER_FROM_NAME[obj[DT_NAME]]
            return serializer.from_json(obj[DT_DATA])
        except Exception:  # pylint: disable=broad-except
            # Fall through
            pass
    return obj


def dtjson_encode(obj, **kwargs):
    return json.dumps(obj, default=dtjson_default, **kwargs)


def dtjson_decode(obj, **kwargs):
    return json.loads(obj, object_hook=dtjson_object_hook, **kwargs)

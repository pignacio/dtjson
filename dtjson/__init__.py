# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

import collections
import datetime
import json
import logging
import pytz

__author__ = 'Ignacio Rossi'
__email__ = 'rossi.ignacio@gmail.com '
__version__ = '0.0.1'

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DT_NAME = '__dtjson_name__'
DT_DATA = '__dtjson_data__'

Serializer = collections.namedtuple('Serializer', ['clz', 'name', 'from_json',
                                                   'to_json'])


def _date_to_json(date):
    return [date.year, date.month, date.day, ]


def _date_from_json(json_obj):
    return datetime.date(*json_obj)


def _datetime_to_json(dtime):
    if dtime.tzinfo:
        timezone = dtime.tzinfo.zone
        as_utc = pytz.utc.normalize(dtime)
        timestamp = float(as_utc.strftime("%s.%f"))
    else:
        timezone = None
        timestamp = float(dtime.strftime("%s.%f"))
    return {'timezone': timezone, 'timestamp': timestamp, }


def _datetime_from_json(json_obj):
    timezone = json_obj['timezone']
    naive = datetime.datetime.fromtimestamp(json_obj['timestamp'])
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
        serializer = _SERIALIZER_FROM_NAME[obj[DT_NAME]]
        return serializer.from_json(obj[DT_DATA])
    return obj


def dtjson_encode(obj):
    return json.dumps(obj, default=dtjson_default)


def dtjson_decode(obj):
    return json.loads(obj, object_hook=dtjson_object_hook)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,invalid-name
"""
test_dtjson
----------------------------------

Tests for `dtjson` package.
"""

import datetime
import json
import unittest
import pytz
import warnings
from mock import patch, sentinel

from dtjson import (dtjson_default, dtjson_object_hook, DT_DATA, DT_NAME,
                    dtjson_encode, dtjson_decode)


class JsonTestMixin(object):  # pylint: disable=too-few-public-methods
    def _test_json(self, obj):
        self.assertEqual(obj, self._encode_decode(obj))

    def _test_json_datetime(self, obj):
        decoded = self._encode_decode(obj)
        self.assertEqual(obj, decoded)
        self.assertEqual(obj.tzinfo, decoded.tzinfo)

    @staticmethod
    def _encode_decode(obj):
        return json.loads(json.dumps(obj,
                                     default=dtjson_default),
                          object_hook=dtjson_object_hook)


class DateTests(JsonTestMixin, unittest.TestCase):
    def test_date(self):
        self._test_json(datetime.date(2015, 1, 2))


class DatetimeTests(JsonTestMixin, unittest.TestCase):
    def setUp(self):
        self.datetime = datetime.datetime(2015, 1, 2, 3, 4, 5)

    def test_naive(self):
        self._test_json_datetime(self.datetime)

    def test_utc(self):
        self._test_json_datetime(pytz.utc.localize(self.datetime))

    def test_timezone(self):
        timezone = pytz.timezone("America/Buenos_Aires")
        self._test_json_datetime(timezone.localize(self.datetime))

    def test_naive_microseconds(self):
        self._test_json_datetime(
            self.datetime + datetime.timedelta(microseconds=12345))

    def test_aware_microseconds(self):
        self._test_json_datetime(pytz.utc.localize(
            self.datetime + datetime.timedelta(microseconds=12345)))


class JsonDataTypesTests(JsonTestMixin, unittest.TestCase):
    def test_null(self):
        self._test_json(None)

    def test_integer(self):
        self._test_json(12345)

    def test_float(self):
        self._test_json(12345.6789)
        self._test_json(1.2e34)
        self._test_json(1.2e-34)

    def test_string(self):
        self._test_json("")
        self._test_json("abc")

    def test_naughty_strings(self):
        self._test_json(DT_DATA)
        self._test_json(DT_NAME)
        self._test_json(DT_NAME + DT_DATA)

    def test_bool(self):
        self._test_json(True)
        self._test_json(False)

    def test_array(self):
        self._test_json([])
        self._test_json([1, "a", None])

    def test_dict(self):
        self._test_json({})
        self._test_json({"a": 1, "b": "x", "c": None})

    def test_naughty_dicts(self):
        self._test_json({DT_NAME: 1, DT_DATA: 2})
        self._test_json({DT_NAME: "__date__", DT_DATA: 2})
        self._test_json({DT_NAME: "__datetime__", DT_DATA: 2})

    def test_invalid(self):
        self.assertRaises(TypeError, self._test_json, object())


class EncodingTest(unittest.TestCase):
    def test_encode(self):
        with patch('dtjson.json.dumps', autospec=True) as mock_dumps:
            mock_dumps.return_value = sentinel.encoded
            encoded = dtjson_encode(sentinel.object)
            mock_dumps.assert_called_once_with(sentinel.object,
                                               default=dtjson_default)
            self.assertEqual(encoded, sentinel.encoded)

    def test_decode(self):
        with patch('dtjson.json.loads', autospec=True) as mock_loads:
            mock_loads.return_value = sentinel.decoded
            decoded = dtjson_decode(sentinel.object)
            mock_loads.assert_called_once_with(sentinel.object,
                                               object_hook=dtjson_object_hook)
            self.assertEqual(decoded, sentinel.decoded)


class InvalidTimezonesTest(JsonTestMixin, unittest.TestCase):
    def setUp(self):
        timezone = pytz.timezone("America/Buenos_Aires")
        self.datetime = timezone.localize(datetime.datetime(2015, 1, 2, 3, 4,
                                                            5, 6))

    def _test_is_moved_to_utc(self, dtime):
        decoded = self._encode_decode(dtime)
        self.assertEqual(dtime, decoded)
        self.assertEqual(pytz.utc, decoded.tzinfo)

    def test_missing_zone_name(self):
        class BrokenTZ(datetime.tzinfo):
            def utcoffset(self, _dtime):
                return datetime.timedelta(minutes=123)

        with warnings.catch_warnings(record=True) as warns:
            self._test_is_moved_to_utc(self.datetime.replace(tzinfo=BrokenTZ()))

        self.assertIn("has no timezone name", str(warns[0].message))

    def test_none_zone_name(self):
        self.datetime.tzinfo.zone = None
        with warnings.catch_warnings(record=True) as warns:
            self._test_is_moved_to_utc(self.datetime)

            self.assertIn("has no timezone name", str(warns[0].message))

    def test_invalid_zone_name(self):
        self.datetime.tzinfo.zone = "Clearly/InvalidTimezone"
        with warnings.catch_warnings(record=True) as warns:
            self._test_is_moved_to_utc(self.datetime)

            self.assertIn("has an invalid timezone name",
                          str(warns[0].message))


if __name__ == '__main__':
    unittest.main()

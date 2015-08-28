======
DTJson
======

.. image:: https://pypip.in/version/dtjson/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/dtjson/
    :alt: Latest version

.. image:: https://pypip.in/py_versions/dtjson/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/dtjson/
    :alt: Supported Python versions

.. image:: https://travis-ci.org/pignacio/dtjson.svg?branch=master
    :target: https://travis-ci.org/pignacio/dtjson

.. image:: https://coveralls.io/repos/pignacio/dtjson/badge.svg?branch=master
    :target: https://coveralls.io/r/pignacio/dtjson?branch=master

.. image:: https://pypip.in/license/dtjson/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/dtjson/
    :alt: License


JSON Serialization for dates and datetimes

* Free software: LGPLv2.1 license

Features
========

Are you tired of seeing the following when dealing with JSON + dates?

.. code-block:: python

  >>> import json, datetime
  >>> json.dumps(datetime.date.today())
  Traceback (most recent call last):
    [...]
  TypeError: datetime.date(2015, 8, 27) is not JSON serializable
  >>> json.dumps(datetime.datetime.now())
  Traceback (most recent call last):
    [...]
  TypeError: datetime.datetime(2015, 8, 27, 21, 24, 48, 937130) is not JSON serializable

This package aims to add ``date`` and ``datetime`` serializaton to and from
JSON.

.. code-block:: python

  >>> import json,datetime
  >>> from dtjson  import dtjson_encode, dtjson_object_hook

  >>> today = datetime.date.today()
  >>> json_today = json.dumps(today, default=dtjson_default)
  >>> print json_today
  {"__dtjson_name__": "__date__", "__dtjson_data__": [2015, 8, 27]}
  >>> today == json.loads(json_today, object_hook=dtjson_object_hook)
  True

  >>> now = datetime.datetime.now()
  >>> json_now = json.dumps(now, default=dtjson_default)
  >>> now == json.loads(json_now, object_hook=dtjson_object_hook)
  True

It even handles the timezone on aware datetimes!

.. code-block:: python

  >>> import pytz
  >>> now_aware = pytz.utc.localize(now)
  >>> json_now_aware = json.dumps(now_aware, default=dtjson_default)
  >>> now_aware == json.loads(json_now_aware, object_hook=dtjson_object_hook)
  True


Special use case: Celery and Django!
====================================

If you serialize your tasks via JSON, and have date arguments on a task, you
have to convert those arguments to something JSON-serializable on every
``delay`` or ``apply_async``,  and convert that value to the original date
inside the task, so that the seralization does not break.

You can avoid that using ``dtjson``, adding this to your settings:

.. code-block:: python

  from dtjson import dtjson_encode, dtjson_decode

  register('dtjson', dtjson_encode, dtjson_decode,
           content_type="application/x-dtjson",
           content_encoding='utf-8')

  CELERY_TASK_SERIALIZER = 'dtjson'
  CELERY_RESULT_SERIALIZER = 'dtjson' # If you use results
  CELERY_ACCEPT_CONTENT = ['dtjson']


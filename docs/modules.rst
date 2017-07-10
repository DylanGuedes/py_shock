===================
SHOCK modules docs
===================


shock.core docs
====================
.. autoclass:: shock.core.Shock
  :members:

  .. automethod:: shock.core.Shock.__init__

.. autofunction:: shock.core.getAction


shock.handlers docs
===================
.. autoclass:: shock.handlers.Handler
  :members:
.. autoclass:: shock.handlers.InterSCity
  :members:


shock.streams docs
==================
.. autoclass:: shock.streams.Stream


shock.sinks docs
================
.. autofunction:: shock.sinks.getRequiredParam
.. autofunction:: shock.sinks.consoleSink
.. autofunction:: shock.sinks.parquetSink
.. autofunction:: shock.sinks.jsonSink
.. autofunction:: shock.sinks.memorySink


shock.ingestion docs
====================
.. autofunction:: shock.ingestion.socketIngestion
.. autofunction:: shock.ingestion.kafkaIngestion
.. autofunction:: shock.ingestion.parquetValueIngestion


shock.analyze docs
=====================
.. autofunction:: shock.analyze.mean
.. autofunction:: shock.analyze.streamFilter
.. autofunction:: shock.analyze.interscitySchema


shock.setup docs
=====================
.. autofunction:: shock.setup.kafkaCast


shock.flushes docs
=====================
.. autofunction:: shock.flushes.queryAndServeWebsockets
.. autofunction:: shock.flushes.readAndServeWebsockets


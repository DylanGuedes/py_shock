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
.. autofunction:: shock.sinks.genericSink
.. autofunction:: shock.sinks.consoleSink
.. autofunction:: shock.sinks.parquetSink
.. autofunction:: shock.sinks.jsonSink
.. autofunction:: shock.sinks.flushAndServeWebsockets


shock.ingestion docs
====================
.. autofunction:: shock.ingestion.socketIngestion
.. autofunction:: shock.ingestion.kafkaIngestion


shock.processing docs
=====================
.. autofunction:: shock.processing.castentity
.. autofunction:: shock.processing.streamFilter
.. autofunction:: shock.processing.interscitySchema

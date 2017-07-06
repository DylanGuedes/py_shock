from heapq import heappush
from abc import ABCMeta, abstractmethod
from kafka import KafkaConsumer, KafkaProducer
import json
import os
from collections import deque

from pyspark import SparkContext, SparkConf
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from shock.core import getAction
from shock.streams import Stream
from shock.sinks import getRequiredParam
import warnings


class Handler(metaclass=ABCMeta):
    """Handler that will be used to take care of new Kafka messages.

    The handler needs to override the `handle` method.
    """
    def __init__(self, opts: dict, environment="default") -> None:
        self.sources = {}
        self.opts = opts
        self.environment = environment
        self.setup()

    def registerSource(self, sourceName: str, source) -> None:
        """
        Register a source type (can be a string).

        Args:
            sourceName (str): Name of the source that will be added.
            source (class): Instance of the source that will be added.
                Can be a Stream.

        Returns:
            no return
        """
        self.sources[sourceName] = source

    def setup(self):
        """
        Setups the handler.
        
        It will be called in the instantiation, and should be overridden when
        needed.

        Args:
            no arguments.

        Returns:
            no return.
        """
        pass

    @abstractmethod
    def handle(self, actionName: str, args: dict) -> None:
        """Hook that handles a given Kafka's message.

        Args:
            actionName (str): Name of the action called.
            args (dict): Arguments that the action are using.

        Returns:
            no return.
        """
        pass

    def newActionSignal(self):
        """ Hook that will be executed when new Kafka's message arrive.
        """
        pass


class InterSCity(Handler):
    def __init__(self, opts: dict, environment="default") -> None:
        warnings.warn('this module will be deprecated!', DeprecationWarning)
        super().__init__(opts)

    def setup(self):
        self.sc = SparkContext(appName="interscity")
        self.spark = SparkSession(self.sc)
        self.consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
        self.consumer.subscribe(['new_pipeline_instruction'])

    def handle(self, actionName, args):
        print("Handling action ", actionName)
        if (actionName == 'ingestion'):
            self.__handleIngestion(args)
        elif (actionName == 'setup'):
            self.__handleSetup(args)
        elif (actionName == 'analyze'):
            self.__handleAnalyze(args)
        elif (actionName == 'publish'):
            self.__handlePublish(args)
        elif (actionName == 'newStream'):
            self.__newStream(args)
        elif (actionName == 'flush'):
            self.__flush(args)
        elif (actionName == 'start'):
            self.__startStream(args)

    def __newStream(self, args):
        """Creates new Shock stream.

        The stream will be registered in the sources dict.

        Args:
            args (dict): Arguments used for the registration.

        Returns:
            no return.
        """
        name = getRequiredParam(args, 'stream')
        st = Stream(name)
        self.registerSource(name, st)

    def __handleIngestion(self, args):
        """Handle the new ingestion method of a stream.

        Args:
            args (dict): Arguments used for the ingestion.

        Returns:
            no return.
        """
        streamName = getRequiredParam(args, 'stream')
        stream = self.sources.get(streamName)
        shockAction = getRequiredParam(args, 'shock_action')
        if (stream):
            args["spark"] = self.spark
            fn = getAction("ingestion", shockAction)
            stream.ingestAction = fn
            stream.ingestArgs = args
        else:
            raise Exception('Stream not found!')


    def __handleSetup(self, args):
        warnings.warn('deprecated', DeprecationWarning)
        streamName = getRequiredParam(args, 'stream')
        shockAction = getRequiredParam(args, 'shock_action')
        stream = self.sources.get(streamName)
        if (stream):
            fn = getAction('setup', shockAction)
            stream.setupAction = fn
            stream.setupArgs = args
        else:
            raise Exception('Stream not found!')

    def __handleAnalyze(self, args):
        """Handle the new process method of a stream.

        Args:
            args (dict): Arguments used for the processing.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        shockAction = getRequiredParam(args, 'shock_action')
        if (stream):
            fn = getAction('analyze', shockAction)
            stream.analyzeAction = fn
            stream.analyzeArgs = args
        else:
            raise Exception('Stream not found!')

    def __handlePublish(self, args):
        """Handle the new publish method of a stream.

        Args:
            args (dict): Arguments used for the publish.

        Returns:
            no return.
        """
        streamName = getRequiredParam(args, 'stream')
        stream = self.sources.get(streamName)
        shockAction = getRequiredParam(args, 'shock_action')
        if (stream):
            fn = getAction('sinks', shockAction)
            stream.publishAction = fn
            stream.publishArgs = args
        else:
            raise Exception('Stream not found!')

    def __flush(self, args):
        """Flushs pending actions. Used for sending websockets.

        Args:
            no arguments.

        Returns:
            no return.
        """
        warnings.warn('deprecated', DeprecationWarning)
        args["spark"] = self.spark
        strategy = getRequiredParam(args, 'strategy')
        try:
            fn = getAction('flushes', strategy)
        except:
            raise('Invalid flush strategy!')

        fn(args)

    def __startStream(self, args):
        """Starts a stream.

        Args:
            args (dict): Arguments used to start the stream.

        Returns:
            no return.
        """
        streamName = getRequiredParam(args, 'stream')
        stream = self.sources.get(streamName)
        if (stream):
            stream.start()
        else:
            raise Exception('Stream not found!')

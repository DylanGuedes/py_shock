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
from shock.sinks import flushAndServeWebsockets
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
        super().__init__()

    def setup(self):
        self.sc = SparkContext(appName="interscity")
        self.spark = SparkSession(self.sc)
        self.consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
        self.consumer.subscribe(['new_pipeline_instruction'])

    def handle(self, actionName, args):
        print("Handling action ", actionName)
        if (actionName == "ingestion"):
            self.__handleIngestion(args)
        elif (actionName == "store"):
            self.__handleStore(args)
        elif (actionName == "process"):
            self.__handleProcess(args)
        elif (actionName == "publish"):
            self.__handlePublish(args)
        elif (actionName == "newStream"):
            self.__newStream(args)
        elif (actionName == "flush"):
            self.__flush(args)
        elif (actionName == "start"):
            self.__startStream(args)

    def __newStream(self, args):
        """Creates new Shock stream.

        The stream will be registered in the sources dict.

        Args:
            args (dict): Arguments used for the registration.

        Returns:
            no return.
        """
        name = args["stream"]
        st = Stream(name)
        self.registerSource(args["stream"], st)

    def __handleIngestion(self, args):
        """Handle the new ingestion method of a stream.

        Args:
            args (dict): Arguments used for the ingestion.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        if (stream):
            args["spark"] = self.spark
            fn = getAction("ingestion", args["shock_action"])
            stream.ingestAction = fn
            stream.ingestArgs = args
        else:
            raise Exception('Stream not found!')


    def __handleStore(self, args):
        warnings.warn('deprecated', DeprecationWarning)
        stream = self.sources.get(args["stream"])
        if (stream):
            fn = getAction("processing", args["shock_action"])
            stream.storeAction = fn
            stream.storeArgs = args
        else:
            raise Exception('Stream not found!')

    def __handleProcess(self, args):
        """Handle the new process method of a stream.

        Args:
            args (dict): Arguments used for the processing.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        if (stream):
            fn = getAction("processing", args["shock_action"])
            stream.processAction = fn
            stream.processArgs = args
        else:
            raise Exception('Stream not found!')

    def __handlePublish(self, args):
        """Handle the new publish method of a stream.

        Args:
            args (dict): Arguments used for the publish.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        if (stream):
            fn = getAction("sinks", args["shock_action"])
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
        strategy = args.get("strategy")
        if (not strategy):
            strategy = "flushAndServeWebsockets"
        try:
            fn = getAction("sinks", strategy)
        except:
            raise('Invalid flush strategy!')

        try:
            fn(args)
        except:
            print("Incorrect flush...")

    def __startStream(self, args):
        """Starts a stream.

        Args:
            args (dict): Arguments used to start the stream.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        if (stream):
            stream.start()
        else:
            raise Exception('Stream not found!')

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
    def setup(self):
        self.sc = SparkContext(appName="interscity")
        self.spark = SparkSession(self.sc)
        self.consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
        self.consumer.subscribe(['new_pipeline_instruction'])

    def handle(self, actionName, args):
        print("Handling action ", actionName)
        if (actionName == "ingestion"):
            self.handleIngestion(args)
        elif (actionName == "store"):
            self.handleStore(args)
        elif (actionName == "process"):
            self.handleProcess(args)
        elif (actionName == "publish"):
            self.handlePublish(args)
        elif (actionName == "newStream"):
            self.newStream(args)
        elif (actionName == "flush"):
            self.flush()
        elif (actionName == "start"):
            self.startStream(args)

    def newStream(self, args):
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

    def handleIngestion(self, args):
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


    def handleStore(self, args):
        warnings.warn('deprecated', DeprecationWarning)
        stream = self.sources.get(args["stream"])
        if (stream):
            fn = getAction("processing", args["shock_action"])
            stream.storeAction = fn
            stream.storeArgs = args
        else:
            raise Exception('Stream not found!')

    def handleProcess(self, args):
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

    def handlePublish(self, args):
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

    def flush(self):
        """Flushs pending actions. Used for sending websockets.

        Args:
            no arguments.

        Returns:
            no return.
        """
        warnings.warn('deprecated', DeprecationWarning)
        flushAndServeWebsockets(self.spark)

    def startStream(self, args):
        """Starts a stream.

        Args:
            args (dict): Arguments used to start the stream.

        Returns:
            no return.
        """
        stream = self.sources.get(args["stream"])
        if (stream):
            stream.ingest()
        else:
            raise Exception('Stream not found!')

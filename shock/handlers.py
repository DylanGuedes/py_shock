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


def default_broker_host():
    kafka_host = os.environ.get('KAFKA_HOST')
    kafka_port = os.environ.get('KAFKA_PORT')
    if (kafka_host and kafka_port):
        return kafka_host + ":" + kafka_port
    else:
        raise Exception('No kafka host or port configured!')


def default_zk_host():
    zk_host = os.environ.get('ZK_HOST')
    zk_port = os.environ.get('ZK_PORT')
    if (zk_host and zk_port):
        return zk_host + ":" + zk_port
    else:
        raise Exception('No zookeeper host and/or port configured!')


class Handler(metaclass=ABCMeta):
    def __init__(self, opts, environment="default"):
        self.sources = {}
        self.opts = opts
        self.environment = environment
        self.setup()


    def registerSource(self, sourceName, source):
        self.sources[sourceName] = source


    def setup(self):
        pass


    @abstractmethod
    def handle(self, actionName, args):
        pass


    def newActionSignal(self):
        pass


class InterSCity(Handler):
    def setup(self):
        """
        ws://localhost:4000/socket/websocket
        """
        self.sc = SparkContext(appName="interscity")
        self.spark = SparkSession(self.sc)
        self.consumer = KafkaConsumer(bootstrap_servers=default_broker_host())
        self.consumer.subscribe(['new_pipeline_instruction'])


    def requiredArgs(self):
        return ["topic", "brokers", "name", "file", "ingest"]


    def handle(self, actionName, args):
        if (actionName == "newstream"):
            self.newStream(args)
        elif (actionName == "updatestream"):
            self.updateStream(args)
        elif (actionName == "flush"):
            self.flush()


    def newStream(self, args):
        for u in self.requiredArgs():
            if args.get(u) is None:
                raise Exception('Missing parameter: ', u)

        ingestAction = getAction(args["file"], args["ingest"])
        ingestArgs = {"spark": self.spark,
                      "topic": args["topic"],
                      "brokers": args["brokers"]}

        if (args.get("publish")):
            args["publish"] = getAction(args["file"], args["publish"])

        if (args.get("store")):
            args["store"] = getAction(args["file"], args["store"])

        st = Stream(ingestAction, ingestArgs, args)
        self.registerSource(args["name"], st)


    def updateStream(self, args):
        stream = self.sources.get(args["stream"])
        if (stream):
            if (args.get("publish")):
                stream.publishAction = getAction(args["file"], args["publish"])
                stream.publish()
            elif (args.get("transform")):
                fn = getAction(args["file"], args["transform"])
                stream.pipelineAppend(fn)
            elif (args.get("store")):
                fn = getAction(args["file"], args["store"])
                stream.storeAction = fn
                stream.store()
        else:
            raise Exception('Source not found!')


    def flush(self):
        flushAndServeWebsockets(self.spark)

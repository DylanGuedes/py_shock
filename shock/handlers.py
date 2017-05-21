from heapq import heappush
from abc import ABCMeta, abstractmethod
from kafka import KafkaConsumer, KafkaProducer
import json
import os

from pyspark import SparkContext, SparkConf
from pyspark.streaming.kafka import KafkaUtils
from pyspark.streaming import StreamingContext

class Handler(metaclass=ABCMeta):
    def __init__(self, opts, environment="default"):
        self.opts = opts
        self.actions = []
        self.environment = environment
        self.ingest()
        self.store()
        self.analyze()
        self.publish()

    @abstractmethod
    def ingest(self):
        """
        =============================================
        | **ingest** => store => analyze => publish |
        =============================================
        """
        pass

    @abstractmethod
    def store(self):
        """
        =============================================
        | ingest => **store** => analyze => publish |
        =============================================
        """
        pass

    @abstractmethod
    def analyze(self):
        """
        =============================================
        | ingest => store => **analyze** => publish |
        =============================================
        """
        pass

    @abstractmethod
    def publish(self):
        """
        =============================================
        | ingest => store => analyze => **publish** |
        =============================================
        """
        pass

    @abstractmethod
    def digest(self):
        pass

    def register_action(self, priority, fn):
        heappush(self.actions, (priority, fn))

    @abstractmethod
    def stop(self):
        pass


class InterSCity(Handler):
    def ingest(self):
        self.consumer = KafkaConsumer(bootstrap_servers=self.opts.get('kafka'))
        self.consumer.subscribe(['new_pipeline_instruction'])
        self.spk_sc = SparkContext(appName="interscity")
        microbatchwindow = int(os.environ.get('BATCH_TIME') or 10)
        self.spk_ssc = StreamingContext(self.spk_sc, microbatchwindow)
        broker_conf = {"metadata.broker.list": self.opts.get('kafka')}
        self.stream = KafkaUtils.createStream(self.spk_ssc, \
                self.opts.get('zk'), "spark-streaming-consumer", {'interscity': 1})
        self.master_stream = self.stream

    def store(self):
        pass

    def analyze(self):
        for priority, op in self.actions:
            self.stream = op(self.stream)

    def publish(self, stream):
        self.producer = KafkaProducer(bootstrap_servers=self.opts.get('kafka'))
        stream.foreachRDD(lambda rdd: self.__publish_array(rdd.collect()))
        return stream

    def digest(self):
        self.spk_ssc.start()

    def __publish_array(self, arr):
        for u in arr:
            self.producer.send('new_results', json.dumps(u).encode('utf-8'))

    def stop(self):
        self.spk_scc.stop()

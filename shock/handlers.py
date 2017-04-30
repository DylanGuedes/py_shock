from heapq import heappush
from abc import ABCMeta, abstractmethod
from kafka import KafkaConsumer, KafkaProducer
import json

class BigDataArchitecture(metaclass=ABCMeta):
    def __init__(self, brokers):
        self.brokers = brokers
        self.actions = []
        self.register_action(0xffff, self.publish_results)
        self.register_action(0xffffff, self.drop_results)

    def register_action(self, priority, fn):
        heappush(self.actions, (priority, fn))

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def publish_results(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def drop_results(self):
        pass

class LambdaArchitecture(BigDataArchitecture):
    def start(self):
        pass

    def publish_results(self):
        pass

    def drop_results(self):
        pass

    def prepare(self):
        pass

class KappaArchitecture(BigDataArchitecture):
    def publish_array(self, arr):
        for u in arr:
            self.producer.send('new_results', json.dumps(u).encode('utf-8'))

    def publish_results(self, stream):
        stream.foreachRDD(lambda rdd: self.publish_array(rdd.collect()))
        return stream

    def drop_results(self, stream):
        # do nothing
        return stream

    def prepare(self):
        self.producer = KafkaProducer(bootstrap_servers=self.brokers)

    def start(self):
        self.prepare()
        for priority, op in self.actions:
            self.stream = op(self.stream)
        self.spk_ssc.start()
        self.spk_ssc.awaitTermination()

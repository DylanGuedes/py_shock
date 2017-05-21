from pyspark import SparkContext, SparkConf
from pyspark.streaming.kafka import KafkaUtils
from pyspark.streaming import StreamingContext
from kafka import KafkaConsumer
import os
from shock.entities import Bus

def default_broker_host():
    kafka_host = os.environ.get('KAFKA_HOST')
    kafka_port = os.environ.get('KAFKA_PORT')
    if (kafka_host and kafka_port):
        return kafka_host + ":" + kafka_port
    else:
        raise Exception('No kafka host or port configured!')

class Shock():
    """This class serves as an abstraction for the communication between Spark
    and Kafka

    Usage:
        >>> shock = Shock(KappaArchitecture)
    """

    def __init__(self, architecture, environment="default"):
        self.broker_address = default_broker_host()
        self.handler = architecture(self.broker_address, environment)
        self.consumer = KafkaConsumer(bootstrap_servers=self.broker_address)
        self.consumer.subscribe(['new_pipeline_instruction'])
        self.start()
        self.kafka_consume()

    def register_action(self, priority, fn):
        self.handler.register_action(priority, fn)

    def start(self):
        """Starts processing.
        """
        self.handler.spk_sc = SparkContext(appName="interscity")
        self.handler.spk_ssc = StreamingContext(self.handler.spk_sc, 10) # TODO: use os.environ
        broker_conf = {"metadata.broker.list": self.handler.brokers}
        self.handler.stream = KafkaUtils.createStream(self.handler.spk_ssc, "kafka:2181", "spark-streaming-consumer", {'interscity': 1})
        self.handler.start()

    def kafka_consume(self):
        idx = 4
        for pkg in self.consumer:
            self.stop()
            msg = pkg.value.decode('ascii')
            fileName, actionName = msg.split(";")
            fileName = fileName.strip()
            actionName = actionName.strip()
            moduleFullPath = "shock."+fileName
            module = __import__(moduleFullPath)
            action = getattr(module, fileName)
            action = getattr(action, actionName)
            self.register_action(idx, action)
            idx+=1
            self.start()

    def stop(self):
        self.handler.spk_ssc.stop()


from pyspark import SparkContext, SparkConf
from pyspark.streaming.kafka import KafkaUtils
from pyspark.streaming import StreamingContext

class Shock():
    """This class serves as an abstraction for the communication between Spark
    and Kafka

    Usage:
        >>> shock = Shock(brokers="kafka:9092", KappaArchitecture)
        >>> shock.register_action(2, myfunc1)
        >>> shock.register_action(3, myfunc1)
        >>> shock.register_action(4, myfunc1)
        >>> shock.start()
    """

    def __init__(self, brokers, architecture, environment="default"):
        self.handler = architecture(brokers, environment)

    def register_action(self, priority, fn):
        self.handler.register_action(priority, fn)

    def start(self):
        """Starts processing.
        """
        self.handler.spk_conf = SparkConf().set("spark.python.profile", "true")
        self.handler.spk_sc = SparkContext()
        self.handler.spk_ssc = StreamingContext(self.handler.spk_sc, 50) # TODO: use os.environ
        broker_conf = {"metadata.broker.list": self.handler.brokers}
        self.handler.stream = KafkaUtils.createDirectStream(self.handler.spk_ssc, ["interscity"], broker_conf)
        self.handler.start()

    def stop(self):
        self.handler.spk_ssc.stop()

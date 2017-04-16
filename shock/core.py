import pika
import os
from pyspark import SparkContext, SparkConf

class Shock():
    """This class serves as an abstraction for the communication between Spark
    and RabbitMQ

    Usage:
        >>> sck = Shock()
        >>> sck.start()
        >>> sck.subscribe('resource_create')
        >>> sck.digest()
        >>> sck.close()
    """

    def start(self):
        """Starts RabbitMQ connection.
        """
        params = pika.ConnectionParameters(str(os.environ['RABBITMQ_HOST']))
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.spk_conf = SparkConf().set("spark.python.profile", "true")
        self.spk_sc = SparkContext(conf=self.spk_conf)
        self.data = self.spk_sc.emptyRDD()

    def subscribe(self, topic, queue):
        """Subscribes for a specific topic.
        """
        self.channel.exchange_declare(exchange=topic, type='topic')
        res = self.channel.queue_declare(queue=queue)
        self.channel.queue_bind(exchange=topic, queue=res.method.queue, routing_key='#')
        self.channel.basic_consume(self.receive, queue=res.method.queue, no_ack=True)
        self.entities = set()

    def prepare_exchange(self, exch, typ):
        """Guarantees that given exchange exist
        """

    def digest(self):
        """Digest topic marked as basic_consume
        """
        self.channel.start_consuming()

    def close(self):
        """Closes RabbitMQ connection
        """
        self.connection.close()

    def prepare_queue(self, queue):
        """Checks and creates RabbitMQ topic
        """
        self.channel.queue_declare(queue=queue)

    def receive(self, ch, method, properties, body):
        """Callback executed by stream after receiving notifications for
        subscribed topic
        """
        print(" [x] Received %r" % body)
        self.add_entity(body['bus_id'])
        process_item = self.spk_sc.parallelize(body)
        self.append_item(process_item)
        self.check_anomaly()

    def add_entity(self, entity_id):
        self.entities.add(entity_id)

    def append_item(self, item):
        """Append item rdd to `data` rdd
        """
        self.data = self.data.union(item)

    def check_anomaly(self):
        if (self.data.count() > 100):
            for u in self.entities:
                result = self.data.filter(lambda a: u==a['bus_id'])

import pika
import os

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

    def subscribe(self, topic, queue):
        """Subscribes for a specific topic.
        """
        self.channel.exchange_declare(exchange=topic, type='topic')
        res = self.channel.queue_declare(queue=queue)
        self.channel.queue_bind(exchange=topic, queue=res.method.queue, routing_key='#')
        self.channel.basic_consume(self.receive, queue=res.method.queue, no_ack=True)

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


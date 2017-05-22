import os
from shock.entities import Bus

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

class Shock():
    """This class serves as an abstraction for the communication between Spark
    and Kafka

    Usage:
        >>> shock = Shock(KappaArchitecture)
    """

    def __init__(self, handler, environment="default"):
        opts = {'kafka': default_broker_host(), 'zk': default_zk_host()}
        self.handler = handler(opts, environment)
        self.handler.digest()
        self.kafka_consume()

    def __register_action(self, fn):
        self.handler.register_action(fn)

    def kafka_consume(self):
        """Consume Kafka's msg
        ===>     "file   ;  action"
        """
        for pkg in self.handler.consumer:
            self.stop()
            msg = pkg.value.decode('ascii')
            filename, actionname = msg.split(";")
            filename = filename.strip()
            actionname = actionname.strip()
            action = self.resolve_actions(filename, actionname)
            self.__register_action(action)

            self.handler.ingest()
            self.handler.store()
            self.handler.analyze()
            self.handler.publish()
            self.handler.digest()

    def resolve_actions(self, filename, actionname):
        """Load action from file inside shock folder
        """
        modulefullpath = "shock."+filename
        module = __import__(modulefullpath)
        action = getattr(module, filename)
        return getattr(action, actionname)

    def stop(self):
        self.handler.stop()


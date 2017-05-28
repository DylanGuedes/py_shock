import os
import json

def getAction(fileName, actionName):
    """Load action from file inside shock folder
    """
    modulefullpath = "shock."+fileName
    module = __import__(modulefullpath)
    action = getattr(module, fileName)
    return getattr(action, actionName)

class Shock():
    """This class serves as an abstraction for the communication between Spark
    and Kafka

    Usage:
        >>> shock = Shock(InterSCity)

    Kafka new stream (from kafka console):
        >>> newstream;{"file": "processing","ingest": "kafkasubscribe","topic": "interscity","brokers": "kafka:9092","name":"mystream"}
        >>> updatestream;{"file": "processing", "stream": "mystream", "store": "castentity"}
        >>> updatestream;{"file": "processing", "stream": "mystream", "transform": "detectBadValues"}
        >>> updatestream;{"file": "processing", "stream": "mystream", "publish": "outputstream"}
    """

    def __init__(self, handler, environment="default"):
        self.handler = handler(environment)
        self.waitForActions()

    def waitForActions(self):
        """Consume Kafka's msg
        ===>     "actionname ;  {"key1": "val1", "key2": "val2", "keyn": "valn"}"
        """
        for pkg in self.handler.consumer:
            self.newActionSignal()
            msg = pkg.value.decode('ascii')
            self.handleNewKafkaMsg(msg)

    def handleNewKafkaMsg(self, msg):
        splittedMsg = msg.split(";")
        actionName = splittedMsg[0].strip()
        args = json.loads(splittedMsg[1])
        self.handler.handle(actionName, args)

    def newActionSignal(self):
        self.handler.newActionSignal()


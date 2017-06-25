from collections import deque
from shock.core import getAction


class Stream():
    """
    Example:
        >>> actions = {'publish': publishAction, 'store': storeAction}
        >>> st = Stream(ingest, {'broker': 'kafka:9092'}, actions)
        >>> st.ingest()

    """
    def __init__(self, name):
        self.name = name
        self.finalStream = None
        self.ingestAction = None
        self.ingestArgs = None
        self.storeAction = None
        self.storeArgs = None
        self.publishAction = None
        self.publishArgs = None
        self.processAction = None
        self.processArgs = None
        self.state = None

    def start(self):
        self.__ingest()

    def __ingest(self):
        print("ingesting...")
        self.state = self.ingestAction(self.ingestArgs)
        self.__store()

    def __store(self):
        print("storing...")
        if (self.storeAction):
            self.state = self.storeAction(self.state, self.storeArgs)
        self.__analyze()

    def __analyze(self):
        print("analyzing...")
        if (self.processAction):
            self.state = self.processAction(self.state, self.processArgs)
        self.__publish()

    def __publish(self):
        print("publishing...")
        if (self.publishAction):
            self.state = self.publishAction(self.state, self.publishArgs)
            self.finalStream = self.state

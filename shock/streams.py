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
        self.setupAction = None
        self.setupArgs = None
        self.publishAction = None
        self.publishArgs = None
        self.analyzeAction = None
        self.analyzeArgs = None
        self.state = None

    def start(self):
        self.__ingest()

    def __ingest(self):
        if (self.ingestAction):
            self.state = self.ingestAction(self.ingestArgs)
        self.__setup()

    def __setup(self):
        if (self.setupAction):
            self.state = self.setupAction(self.state, self.setupArgs)
        self.__analyze()

    def __analyze(self):
        if (self.analyzeAction):
            self.state = self.analyzeAction(self.state, self.analyzeArgs)
        self.__publish()

    def __publish(self):
        if (self.publishAction):
            self.state = self.publishAction(self.state, self.publishArgs)
            self.finalStream = self.state

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
        """
        =============================================
        | **ingest** => store => analyze => publish |
        =============================================
        """
        print("ingesting...")
        self.state = self.ingestAction(self.ingestArgs)
        self.initialState = self.state
        self.store()

    def __store(self):
        """
        =============================================
        | ingest => **store** => analyze => publish |
        =============================================
        """
        print("storing...")
        if (self.storeAction):
            self.state = self.storeAction(self.state, self.storeArgs)
        self.analyze()

    def __analyze(self):
        """
        =============================================
        | ingest => store => **analyze** => publish |
        =============================================
        """
        print("analyzing...")
        if (self.processArgs):
            self.processAction(self.state, self.processArgs)
        self.publish()

    def __publish(self):
        """
        =============================================
        | ingest => store => analyze => **publish** |
        =============================================
        """
        print("publishing...")
        if (self.publishAction):
            self.state = self.publishAction(self.state, self.publishArgs)
            self.finalStream = self.state

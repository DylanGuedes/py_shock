from collections import deque
from shock.core import getAction
import time


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

    def ingest(self):
        """
        =============================================
        | **ingest** => store => analyze => publish |
        =============================================
        """
        print("ingesting...")
        self.state = self.ingestAction(self.ingestArgs)
        self.initialState = self.state
        self.store()

    def store(self):
        """
        =============================================
        | ingest => **store** => analyze => publish |
        =============================================
        """
        print("storing...")
        if (self.storeAction):
            self.state = self.storeAction(self.state, self.storeArgs)
        self.analyze()

    def analyze(self):
        """
        =============================================
        | ingest => store => **analyze** => publish |
        =============================================
        """
        print("analyzing...")
        if (self.processArgs):
            self.processAction(self.state, self.processArgs)
        self.publish()

    def publish(self):
        """
        =============================================
        | ingest => store => analyze => **publish** |
        =============================================
        """
        print("publishing...")
        if (self.publishAction):
            self.state = self.publishAction(self.state, self.publishArgs)
            self.finalStream = self.state

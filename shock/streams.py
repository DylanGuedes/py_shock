from collections import deque
from shock.core import getAction


class Stream():
    """
    Usage:
    >>> actions = {'publish': publishAction, 'store': storeAction}
    >>> st = Stream(ingest, {'broker': 'kafka:9092'}, actions)
    >>> st.ingest()

    """
    def __init__(self, ingest, ingestArgs, args):
        self.ingestAction = ingest
        self.ingestArgs = ingestArgs
        self.actions = deque()
        self.finalStream = None

        if (args.get("publish")):
            self.publishAction(optionalActions["publish"])
        else:
            self.publishAction = None

        if (args.get("store")):
            self.storeAction(optionalActions["store"])
        else:
            self.storeAction = None
        self.ingest()

    def pipelineAppend(self, fn):
        self.actions.append(fn)
        if (self.finalStream):
            self.finalStream.stop()
        self.analyze()

    def ingest(self):
        """
        =============================================
        | **ingest** => store => analyze => publish |
        =============================================
        """
        self.state = self.ingestAction(self.ingestArgs)
        self.initialState = self.state
        self.store()

    def store(self):
        """
        =============================================
        | ingest => **store** => analyze => publish |
        =============================================
        """
        if (self.storeAction):
            self.state = self.storeAction(self.state)
        self.analyze()

    def analyze(self):
        """
        =============================================
        | ingest => store => **analyze** => publish |
        =============================================
        """
        for op in self.actions:
            self.state = op(self.state)
        self.publish()

    def publish(self):
        """
        =============================================
        | ingest => store => analyze => **publish** |
        =============================================
        """
        if (self.publishAction):
            self.finalStream = self.publishAction(self.state)

    def newAnalyzeFn(self, fn):
        if (self.publishAction):
            self.state.stop()
        self.actions.appendleft(fn)
        self.state = self.initialState
        self.analyze()

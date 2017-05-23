from shock.handlers import Handler

class FakeKafkaPkg(object):
    def __init__(self, s):
        self.value = s


class TestHandler(Handler):
    def ingest(self):
        self.consumer = [FakeKafkaPkg(b"processing;countwords")]

    def analyze(self):
        pass

    def publish(self):
        pass

    def store(self):
        pass

    def digest(self):
        pass

    def stop(self):
        pass


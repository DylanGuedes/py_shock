from shock.handlers import Handler

class FakeKafkaPkg(object):
    def __init__(self, s):
        self.value = s


class TestHandler(Handler):
    def setup(self):
        self.consumer = [FakeKafkaPkg(b"newstream;{}")]

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

    def handle(self, actionName, args):
        pass

import unittest
import sys, os
from kafka import KafkaConsumer, KafkaProducer

sys.path.append(os.path.abspath('/shock'))

from shock.core import Shock
from shock.handlers import KappaArchitecture

class ShockTests(unittest.TestCase):
    def setUp(self):
        self.shock = Shock("kafka:9092", KappaArchitecture, "test")
        self.consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
        self.producer = KafkaProducer(bootstrap_servers="kafka:9092")

    def tearDown(self):
        print("DONE!!")

    def test_check_do_nothing(self):
        print("STARTING TEST!!")
        self.consumer.subscribe(['integration-test'])
        self.producer.send('integration-test', b'InterSCity test')
        self.shock.start()
        print("SHOCK STARTED!!")

        for msg in self.consumer:
            self.assertEqual("InterSCity test", msg)
            break

if __name__ == "__main__":
    unittest.main()

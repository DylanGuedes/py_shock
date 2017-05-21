import unittest
import sys, os
from kafka import KafkaConsumer, KafkaProducer

sys.path.append(os.path.abspath('/shock'))

from shock.core import Shock
from shock.handlers import default_broker_host

class ShockTests(unittest.TestCase):
    def setUp(self):
        self.shock = Shock("kafka:9092", KappaArchitecture, "test")
        self.consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
        self.producer = KafkaProducer(bootstrap_servers="kafka:9092")

    def tearDown(self):
        pass

    def test_default_broker_host_construction(self):
        self.assertEqual(default_broker_host(), "kafka:9092")

if __name__ == "__main__":
    unittest.main()

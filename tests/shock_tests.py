import unittest
from unittest import TestCase
from shock.core import Shock

class ShockTests(TestCase):
    def setUp(self):
        self.sck = Shock()
        self.sck.start()

    def tearDown(self):
        self.sck.close()

    def test_rabbitmq_connection(self):
        self.sck.join_queue('data_stream')
        self.sck.publish('hello friends', 'data_stream')

if __name__ == '__main__':
        unittest.main()

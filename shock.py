from shock.handlers import KappaArchitecture
from shock.core import Shock
from kafka import KafkaConsumer
import importlib
import sys

def split_words(stream):
    return stream.map(lambda x: x[1]).flatMap(lambda line: line.split(" "))

def reduce_words(stream):
    return stream.map(lambda word: (word, 1)).reduceByKey(lambda a, b: a+b)

def print_results(stream):
    # stream.pprint()
    return stream

sck = Shock("kafka:9092", KappaArchitecture)

# shock.register_action(1, split_words)
# shock.register_action(2, reduce_words)
sck.register_action(0xfff, print_results)

sck.start()

consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
consumer.subscribe(['new_pipeline_instruction'])
idx = 4

default_operations = {
    "map": lambda k: (lambda v: k.map(v))
}

for action in consumer:
    sck.stop()
    msg = action.value.decode('ascii')
    comm = msg.split(";")
    sck.register_action(idx, default_operations[comm[0]])
    idx+=1
    sck.start()


from shock.handlers import KappaArchitecture
from shock.core import Shock

def split_words(stream):
    return stream.map(lambda x: x[1]).flatMap(lambda line: line.split(" "))

def reduce_words(stream):
    return stream.map(lambda word: (word, 1)).reduceByKey(lambda a, b: a+b)

def print_results(stream):
    stream.pprint()
    return stream

shock = Shock("kafka:9092", KappaArchitecture)

shock.register_action(1, split_words)
shock.register_action(2, reduce_words)
shock.register_action(3, print_results)

shock.start()

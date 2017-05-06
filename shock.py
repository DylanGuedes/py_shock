from shock.handlers import KappaArchitecture
from shock.core import Shock
from kafka import KafkaConsumer
import importlib
import sys

sck = Shock("kafka:9092", KappaArchitecture)

sck.start()

consumer = KafkaConsumer(bootstrap_servers="kafka:9092")
consumer.subscribe(['new_pipeline_instruction'])
idx = 4

for pkg in consumer:
    sck.stop()
    msg = pkg.value.decode('ascii')
    fileName, actionName = msg.split(";")
    fileName = fileName.strip()
    actionName = actionName.strip()
    moduleFullPath = "shock."+fileName
    module = __import__(moduleFullPath)
    action = getattr(module, fileName)
    action = getattr(action, actionName)
    sck.register_action(idx, action)
    idx+=1
    sck.start()


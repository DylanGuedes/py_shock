from pyspark.sql.types import *
from pyspark.sql.functions import *

import asyncio
import websockets
import json


def kafkasubscribe(args):
    spark = args["spark"]
    topic = args["topic"]
    brokers = args["brokers"]
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", brokers) \
        .option("subscribe", topic).load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")


def outputstream(stream):
    return stream.writeStream.format("console").start()


def castentity(stream):
    """
    Return a new dataframe with normalized attrs from `value`
    # Params
    stream => KafkaStream or Dataframe
    entity => Entity with attributes

    """
    json_objects = []
    for u in ["uuid", "capability", "timestamp", "value"]:
        json_objects.append(get_json_object(stream.value, '$.'+u).alias(u))
    return stream.select(json_objects)


def detectBadValues(stream):
    return stream.where("capability == 'air_quality'").where("value != 'boa'")


def detectGoodValues(stream):
    return stream.where("capability == 'air_quality'").where("value == 'boa'")


def parquetOutput(stream):
    return stream.writeStream.format("parquet") \
            .option("checkpointLocation", "/shock_checkpoints") \
            .option("path", "/shock_results/") \
            .start()


def jsonOutput(stream):
    return stream.writeStream.format("parquet") \
            .option("checkpointLocation", "/checkpoits") \
            .option("path", "/analysis") \
            .start()


def readJsonAndServeWebsockets(spark):
    interscitySchema = StructType() \
            .add("uuid", "string") \
            .add("capability", "string") \
            .add("timestamp", "string") \
            .add("value", "string")
    df = spark.read.parquet("/analysis")
    rdd = df.rdd.collect()

    @asyncio.coroutine
    def sendPayload():
        websocket = yield from websockets.connect('ws://172.17.0.1:4545/socket/websocket')
        data = dict(topic="alerts:lobby", event="phx_join", payload={}, ref=None)
        yield from websocket.send(json.dumps(data))
        for entry in rdd:
            payload = {
                'uuid': entry.uuid,
                'capability': entry.capability,
                'timestamp': entry.timestamp,
                'value': entry.value
            }
            msg = dict(topic="alerts:lobby", event="new_report", payload=payload, ref=None)
            yield from websocket.send(json.dumps(msg))
    asyncio.get_event_loop().run_until_complete(sendPayload())

from pyspark.sql.types import *
from pyspark.sql.functions import *


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

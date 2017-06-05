from pyspark.sql.types import *
from pyspark.sql.functions import *

import asyncio
import websockets
import json


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


def interscitySchema():
    return StructType() \
            .add("uuid", "string") \
            .add("capability", "string") \
            .add("timestamp", "string") \
            .add("value", "string")

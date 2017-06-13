from pyspark.sql.types import StructType as SparkStructType
from pyspark.sql.functions import *
from pyspark.sql.streaming import DataStreamWriter, DataStreamReader
from pyspark.sql import DataFrame as SparkDataFrame

import asyncio
import websockets
import json
from typing import TypeVar

def castentity(stream: DataStreamReader, args: dict) -> DataStreamReader:
    """Return a new dataframe with normalized attrs from `value`

    Args:
        stream (Stream): processed stream.

    Returns:
        Stream: casted stream.

    """
    json_objects = []
    for u in ["uuid", "capability", "timestamp", "value"]:
        json_objects.append(get_json_object(stream.value, '$.'+u).alias(u))
    return stream.select(json_objects)


def streamFilter(stream: SparkDataFrame, args: dict) -> SparkDataFrame:
    """Filter stream.

    Args:
        stream (SparkDataFrame): processed stream.
        args (dict): options to be used in the filter.

    Returns:
        SparkDataFrame: filtered stream.
    """
    query = args["query"]
    return stream.where(query)


def interscitySchema() -> SparkStructType:
    """Capabilities schema used in InterSCity.

    Args:
        nope

    Returns:
        SparkStructType: the schema used in InterSCity capabilities system.
    """
    return SparkStructType() \
            .add("uuid", "string") \
            .add("capability", "string") \
            .add("timestamp", "string") \
            .add("value", "string")

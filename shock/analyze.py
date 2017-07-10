try:
    import pyspark
except:
    import findspark
    findspark.init()
from pyspark.sql.types import StructType as SparkStructType
from pyspark.sql.functions import *
from pyspark.sql.streaming import DataStreamWriter, DataStreamReader
from pyspark.sql import DataFrame as SparkDataFrame

import asyncio
import websockets
import json
from typing import TypeVar
from pyspark.sql.functions import *
from pyspark.sql.types import *
from shock.sinks import getRequiredParam


def streamFilter(stream: SparkDataFrame, args: dict) -> SparkDataFrame:
    """Filter stream.

    Args:
        stream (SparkDataFrame): processed stream.
        args (dict): options to be used in the filter.

    Returns:
        SparkDataFrame: filtered stream.
    """
    query = getRequiredParam(args, 'query')
    return stream.where(query)


def mean(stream: SparkDataFrame, args: dict) -> SparkDataFrame:
    """Calculates mean of a column.

    Args:
        stream (SparkDataFrame): processed stream.
        args (dict): options to be used in the filter.

    Returns:
        SparkDataFrame: filtered stream.
    """
    df1 = stream.selectExpr('cast(value as double) value')
    df2 = df1.select(avg("value"))
    return df2


def interscitySchema(valueType="string") -> SparkStructType:
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
            .add("value", valueType)

from pyspark.sql.types import StructType as SparkStructType
from pyspark.sql.streaming import DataStreamWriter, DataStreamReader
from pyspark.sql import DataFrame as SparkDataFrame
import json
from typing import TypeVar
from pyspark.sql.functions import get_json_object

def kafkaCast(stream: DataStreamReader, args: dict) -> DataStreamReader:
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


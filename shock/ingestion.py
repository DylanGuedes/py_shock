from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.types import StructType
from shock.sinks import getRequiredParam


def socketIngestion(args: dict) -> SparkDataFrame:
    """Return a socket ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: socket ingestion dataframe ready to be used.
    """
    spark = getRequiredParam(args, 'spark')
    host = getRequiredParam(args, 'host')
    port = getRequiredParam(args, 'port')
    return spark.readStream.format("socket") \
            .option("host", host) \
            .option("port", port) \
            .load()


def parquetValueIngestion(args: dict) -> SparkDataFrame:
    spark = getRequiredParam(args, 'spark')
    path = getRequiredParam(args, 'path')

    mySchema = StructType() \
            .add("value", "string") \
            .add("uuid", "string") \
            .add("timestamp", "string") \
            .add("capability", "string")

    return spark.readStream \
        .format('parquet') \
        .schema(mySchema) \
        .option('path', path) \
        .load()


def kafkaIngestion(args: dict) -> SparkDataFrame:
    """Return a kafka ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: kafka ingestion dataframe ready to be used.
    """
    spark = getRequiredParam(args, 'spark')
    topic = getRequiredParam(args, 'topic')
    brokers = getRequiredParam(args, 'brokers')
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", brokers) \
        .option("subscribe", topic) \
        .load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

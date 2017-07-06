from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.types import StructType


def socketIngestion(args: dict) -> SparkDataFrame:
    """Return a socket ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: socket ingestion dataframe ready to be used.
    """
    spark = args["spark"]
    host = args["host"]
    port = args["port"]
    return spark.readStream.format("socket") \
            .option("host", host) \
            .option("port", port) \
            .load()


def parquetValueIngestion(args: dict) -> SparkDataFrame:
    spark = args.get("spark")
    if spark:
        path = args.get("path")

        mySchema = StructType() \
                .add("value", "string") \
                .add("uuid", "string") \
                .add("timestamp", "string") \
                .add("capability", "string")

        if path:
            stream = spark.readStream \
                .format("parquet") \
                .schema(mySchema) \
                .option("path", path) \
                .load()
            return stream
        else:
            raise("You should pass a path to be readed!")
    else:
        raise("You should pass a spark session instance!")


def parquetIngestion(args: dict) -> SparkDataFrame:
    """Return a Parquet File ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: Parquet ingestion dataframe ready to be used.
    """
    spark = args.get("spark")
    if spark:
        path = args.get("path")
        if path:
            return spark.readStream.format("parquet") \
                .option("path", path) \
                .load() \
                .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        else:
            raise("You should pass a path to be readed!")
    else:
        raise("You should pass a spark session instance!")


def kafkaIngestion(args: dict) -> SparkDataFrame:
    """Return a kafka ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: kafka ingestion dataframe ready to be used.
    """
    spark = args["spark"] # TODO: raise exception if no param
    topic = args["topic"] # TODO: raise exception if no param
    brokers = args["brokers"] # TODO: raise exception if no param
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", brokers) \
        .option("subscribe", topic) \
        .load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

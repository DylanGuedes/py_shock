from pyspark.sql import DataFrame as SparkDataFrame

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


def kafkaIngestion(args: dict) -> SparkDataFrame:
    """Return a kafka ingestion stream ready to be used.

    Args:
        args (dict): dict with options used to mount the stream.

    Returns:
        SparkDataFrame: socket ingestion dataframe ready to be used.
    """
    spark = args["spark"]
    topic = args["topic"]
    brokers = args["brokers"]
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", brokers) \
        .option("subscribe", topic) \
        .load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

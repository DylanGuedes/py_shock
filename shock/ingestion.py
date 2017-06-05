def socketIngestion(args):
    spark = args["spark"]
    host = args["host"]
    port = args["port"]
    return spark.readStream.format("socket") \
            .option("host", host) \
            .option("port", port) \
            .load()


def kafkaIngestion(args):
    spark = args["spark"]
    topic = args["topic"]
    brokers = args["brokers"]
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", brokers) \
        .option("subscribe", topic).load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

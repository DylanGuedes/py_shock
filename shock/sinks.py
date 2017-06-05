def genericSink(stream, sinkName):
    return stream.writeStream.format(sinkName) \
            .option("checkpointLocation", "/checkpoints") \
            .option("path", "/analysis") \
            .start()


def consoleSink(stream):
    return genericSink(stream, "console")


def parquetSink(stream):
    return genericSink(stream, "parquet")


def jsonSink(stream):
    return genericSink(stream, "json")


def flushAndServeWebsockets(spark):
    sch = interscitySchema
    try:
        df = spark.read.parquet("/analysis")
    except:
        df = spark.createDataFrame([], sch) # empty df
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

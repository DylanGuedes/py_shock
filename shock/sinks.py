from typing import TypeVar
from pyspark.sql import SparkSession
import time
from shock.processing import interscitySchema
import asyncio
import websockets
import json

StructuredStream = TypeVar('StructuredStream')
OutputStream = TypeVar('OutputStream')

def genericSink(stream: StructuredStream, sinkName: str, args: dict) -> OutputStream:
    """Return a output stream from a generic sink type.

    Args:
        stream (StructuredStream): processed stream.
        sinkName (str): Sink type.

    Returns:
        OutputStream: Stream output
    """
    time.sleep(1)
    streamName = args["stream"]
    path = args["path"] or "/analysis"
    return stream.writeStream \
            .outputMode('append') \
            .format(sinkName) \
            .option("checkpointLocation", "/checkpoints/"+streamName) \
            .option("path", path) \
            .start()


def consoleSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Prints stream output to terminal.

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    time.sleep(1)
    streamName = args["stream"]
    return stream.writeStream \
            .outputMode('append') \
            .format('console') \
            .start()


def parquetSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to Parquet files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return genericSink(stream, "parquet", args)


def parquetCompleteSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write to ParquetSink using the complete output. The :path arg will be checked.

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    streamName = args.get("stream")
    path = args.get("path") or "/analysis"
    return stream.writeStream \
            .outputMode('complete') \
            .format('memory') \
            .queryName('analysis') \
            .start()


def memorySink(stream: StructuredStream, args: dict) -> OutputStream:
    table = args.get('table')
    if not table:
        table = 'analysis'
    stream.writeStream\
            .outputMode('complete')\
            .format('memory')\
            .queryName(table)\
            .start()


def jsonSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to json files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return genericSink(stream, "json", args)


def flushAndServeWebsockets(args: dict) -> None:
    """Publish parquet results written in /analysis via websocket

    Args:
        spark (SparkSession): processed stream.

    Returns:
        None
    """
    spark = args.get("spark")
    if (not spark):
        raise('Spark Session should be passed!')

    path = args.get("path")
    if (not path):
        path = "/analysis"

    event = args.get("event")
    if (not event):
        event = "new_report"

    sch = interscitySchema()
    try:
        df = spark.read.parquet(path)
    except:
        df = spark.createDataFrame([], sch) # empty df
    rdd = df.rdd.collect()

    @asyncio.coroutine
    def sendPayload():
        print('sending data...')
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
            msg = dict(topic="alerts:lobby", event=event, payload=payload, ref=None)
            yield from websocket.send(json.dumps(msg))
    asyncio.get_event_loop().run_until_complete(sendPayload())


def queryAndServeWebsockets(args: dict) -> None:
    spark = args.get("spark")
    if (not spark):
        raise('Spark Session should be passed!')

    query = args.get("query")
    if (not query):
        raise('query should be passed!')

    event = args.get("event")
    if (not event):
        event = "new_report"

    try:
        df = spark.sql(query)
    except:
        print("Wrong query...")
        return

    rdd = df.rdd.collect()

    @asyncio.coroutine
    def sendPayload():
        print('sending data...')
        websocket = yield from websockets.connect('ws://172.17.0.1:4545/socket/websocket')
        data = dict(topic="alerts:lobby", event="phx_join", payload={}, ref=None)
        yield from websocket.send(json.dumps(data))
        for entry in rdd:
            payload = {
                'value': entry
            }
            msg = dict(topic="alerts:lobby", event=event, payload=payload, ref=None)
            yield from websocket.send(json.dumps(msg))
    asyncio.get_event_loop().run_until_complete(sendPayload())

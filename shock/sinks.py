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
    return stream.writeStream \
            .outputMode('append') \
            .format(sinkName) \
            .option("checkpointLocation", "/"+streamName) \
            .option("path", "/analysis") \
            .start()


def consoleSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Prints stream output to terminal.

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return genericSink(stream, "console", args)


def parquetSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to Parquet files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return genericSink(stream, "parquet", args)


def jsonSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to json files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return genericSink(stream, "json", args)


def flushAndServeWebsockets(spark: SparkSession) -> None:
    """Publish parquet results written in /analysis via websocket

    Args:
        spark (SparkSession): processed stream.

    Returns:
        None
    """
    sch = interscitySchema()
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

from shock.sinks import getRequiredParam
from shock.analyze import interscitySchema
import asyncio
import websockets
import json


def queryAndServeWebsockets(args: dict) -> None:
    """Query SparkSession tables and returns via WebSocket.

    Args:
        args (dict): Args used to query.

    Returns:
        None
    """
    spark = getRequiredParam(args, 'spark')
    query = getRequiredParam(args, 'query')
    event = args.get("event") or "new_report"

    try:
        df = spark.sql(query)
    except:
        raise('Invalid sql query %s', query)
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


def readAndServeWebsockets(args: dict) -> None:
    """Publish parquet results written in /analysis via websocket

    Args:
        spark (SparkSession): processed stream.

    Returns:
        None
    """
    spark = getRequiredParam(args, 'spark')

    path = args.get("path") or "/analysis"
    event = args.get("event") or "new_report"

    sch = interscitySchema()
    try:
        df = spark.read.parquet(path)
    except:
        df = spark.createDataFrame([], sch) # empty df
        return
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
            msg = dict(topic="alerts:lobby", event=event, payload=payload, ref=None)
            yield from websocket.send(json.dumps(msg))
    asyncio.get_event_loop().run_until_complete(sendPayload())

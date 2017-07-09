from typing import TypeVar, Iterable, Any
from pyspark.sql import SparkSession
import time
from shock.analyze import interscitySchema
import asyncio
import websockets
import json
from abc import ABCMeta, abstractmethod
from pyspark.sql.streaming import DataStreamWriter

StructuredStream = TypeVar('StructuredStream')
OutputStream = TypeVar('OutputStream')


class Sink(metaclass=ABCMeta):
    def __init__(self, opts: dict) -> None:
        self.options = []
        for u, v in opts:
            self.options.append((u, v))

    @abstractmethod
    def requiredParams(self) -> Iterable:
        pass

    def __adjust(self) -> None:
        if (not self.outputMode):
            self.outputMode = 'append'
        if (not self.format):
            self.format = 'console'

    def inject(self, stream: StructuredStream) -> OutputStream:
        self.__adjust()
        stream = stream.writeStream
        stream = self.__outputMode(stream)
        stream = self.__format(stream)
        stream = self.__inject_options(stream)
        stream = self.__start(stream)

    def add_option(self, stream: StructuredStream, optionName: str,
            optionValue: str) -> None:
        self.options.append((optionName, optionValue))

    def __outputMode(self, stream: StructuredStream) -> StructuredStream:
        return stream.outputMode(self.outputMode)

    def __format(self, stream: StructuredStream) -> StructuredStream:
        return stream.format(self.format)

    def __start(self, stream: StructuredStream) -> OutputStream:
        return stream.start()

    def __inject_options(self, stream: StructuredStream) -> StructuredStream:
        for op in self.options:
            stream = stream.option(op[0], op[1])
        return stream


class ConsoleSink(Sink):
    def __init__(self, opts: dict) -> None:
        pass


class RequiredParamMissing(Exception):
    def __init__(self, param):
        self.param = param

    def __str__(self):
        return 'Missing required param %s.' % self.param


def getRequiredParam(args: dict, paramName: str) -> Any:
    param = args.get(paramName)
    if (param):
        return param
    else:
        raise RequiredParamMissing(paramName)


def consoleSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Prints stream output to terminal.

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return stream.writeStream \
            .outputMode('append') \
            .format('console') \
            .start()


def _fileSink(sinkName: str, stream: StructuredStream, args: dict) -> OutputStream:
    streamName = getRequiredParam(args, 'stream')
    path = args.get('path') or 'analysis'
    outputMode = args.get('outputMode') or 'append'
    return stream.writeStream \
            .format(sinkName) \
            .outputMode(outputMode) \
            .option('checkpointLocation', 'checkpoints/'+streamName) \
            .option('path', path) \
            .start()


def parquetSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to Parquet files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return _fileSink('parquet', stream, args)


def jsonSink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to json files. The content will be saved at /analysis

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    return _fileSink('json', stream, args)


def memorySink(stream: StructuredStream, args: dict) -> OutputStream:
    """Write stream output to SparkSession instance. The content can receive
    queries via spark instance.

    Args:
        stream (StructuredStream): processed stream.

    Returns:
        OutputStream: Stream output
    """
    table = getRequiredParam(args, 'table')
    return stream.writeStream\
            .outputMode('complete')\
            .format('memory')\
            .queryName(table)\
            .start()

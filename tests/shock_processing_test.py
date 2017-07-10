import pytest
import findspark
findspark.init()
import pyspark
import pyspark.sql
from shock.core import Shock
from tests.helpers import TestHandler
from pyspark.sql.types import Row


@pytest.fixture
def sc():
    return pyspark.SparkContext.getOrCreate()


@pytest.fixture
def shock():
    return Shock(TestHandler)


@pytest.fixture
def spark(sc):
    return pyspark.sql.SparkSession(sc)


@pytest.fixture
def sqlcontext():
    sc = pyspark.SparkContext.getOrCreate()
    return (pyspark.SQLContext(sc), sc)


def testFilter(sc, spark):
    from shock.analyze import streamFilter
    from shock.setup import kafkaCast
    jsonString1 = '{"uuid": "aaaa", "capability": "temperature",\
                   "timestamp": "today", "value": 15}'
    jsonString2 = '{"uuid": "bbbb", "capability": "temperature",\
                   "timestamp": "today", "value": 15}'
    jsonString3 = '{"uuid": "cccc", "capability": "temperature",\
                   "timestamp": "today", "value": 15}'
    jsonString4 = '{"uuid": "aaaa", "capability": "temperature",\
                   "timestamp": "today", "value": 15}'
    df = sc.parallelize([
        {'value': jsonString1},
        {'value': jsonString2},
        {'value': jsonString3},
        {'value': jsonString4}
    ]).toDF()
    df1 = kafkaCast(df, dict())

    args = {'query': "uuid == 'aaaa'"}
    rdd = streamFilter(df1, args).rdd
    arr = rdd.collect()
    assert len(arr) == 2
    assert arr[0].uuid == 'aaaa'
    assert arr[1].uuid == 'aaaa'


def testCastEntities(sc, spark):
    from shock.setup import kafkaCast
    jsonString = '{"uuid": "abcdef", "capability": "temperature",\
                   "timestamp": "today", "value": 15}'
    df = sc.parallelize([{'value': jsonString}]).toDF()
    df1 = kafkaCast(df, dict())
    df1.show()
    row = Row(capability='temperature', timestamp='today', uuid='abcdef', value='15')
    row2 = df1.rdd.collect()[0]
    assert row.capability == row2.capability
    assert row.timestamp == row2.timestamp

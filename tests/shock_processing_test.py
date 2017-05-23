import pytest

import findspark
findspark.init()
import pyspark
import pyspark.sql

from shock.core import Shock
from tests.helpers import TestHandler

from shock.processing import splitwords

@pytest.fixture
def sc():
    return pyspark.SparkContext.getOrCreate()

@pytest.fixture
def shock():
    return Shock(TestHandler)

@pytest.fixture
def sqlcontext():
    sc = pyspark.SparkContext.getOrCreate()
    return (pyspark.SQLContext(sc), sc)

def test_splitwords(sc):
    rdd = sc.parallelize("my awesome word")
    assert ["my","awesome","word"], splitwords(rdd).collect()

def test_filterbus(shock, sc):
    from shock.processing import filterbus
    rdd = sc.parallelize(["bus 0001", "bus 0002", "car 001", "car 002"])
    assert filterbus(rdd).collect() == ["bus 0001", "bus 0002"]

def test_invalidtemperatures(sqlcontext):
    sc = sqlcontext[1]
    from shock.processing import todf, invalidtemperature, temperatures, onlyvalues
    rdd = sc.parallelize([
        pyspark.sql.Row(entity='bus', value=7839),
        pyspark.sql.Row(entity='temperature', value=313),
        pyspark.sql.Row(entity='temperature', value=123),
        pyspark.sql.Row(entity='temperature', value=400)
    ])
    df = todf(rdd)
    df2 = temperatures(df)
    df3 = invalidtemperature(df2)
    df4 = onlyvalues(df3)
    df4.show()
    assert df4.collect() == [pyspark.Row(value=313), pyspark.Row(value=400)]


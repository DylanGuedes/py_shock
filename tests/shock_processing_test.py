import pytest

import findspark
findspark.init()
import pyspark
import pyspark.sql

from shock.core import Shock
from tests.helpers import TestHandler

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

def testSchema(sc, spark):
    from shock.processing import castentity
    jsonString = '{"uuid": "abcdef", "capability": "temperature", "timestamp": "today", "value": 15 }'
    df = sc.parallelize([{'value': jsonString}]).toDF()
    df1 = castentity(df)
    df1.show()

    assert df1 == 2
    assert df1.show() == 3
    assert 1==1


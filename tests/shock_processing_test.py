import pytest

import findspark
findspark.init()
import pyspark

from shock.processing import splitwords

@pytest.fixture
def sc():
    return pyspark.SparkContext.getOrCreate()

def test_splitwords(sc):
    rdd = sc.parallelize("my awesome word")
    assert ["my","awesome","word"], splitwords(rdd).collect()


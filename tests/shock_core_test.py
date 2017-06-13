import pytest
import findspark
findspark.init()
from shock.core import Shock
from tests.helpers import TestHandler
import pyspark


@pytest.fixture
def shock():
    return Shock(TestHandler)

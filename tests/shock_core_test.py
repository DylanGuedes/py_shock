import pytest

import findspark
findspark.init()
import pyspark

from shock.core import Shock
from tests.helpers import TestHandler

@pytest.fixture
def shock():
    return Shock(TestHandler)


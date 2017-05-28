import pytest
import findspark
findspark.init()

from shock.core import Shock  # nopep8
from tests.helpers import TestHandler  # nopep8

import pyspark  # nopep8


@pytest.fixture
def shock():
    return Shock(TestHandler)

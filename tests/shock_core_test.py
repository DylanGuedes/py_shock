import pytest
import findspark
findspark.init()
import shock.core
from tests.helpers import TestHandler
from unittest.mock import patch
import pyspark
import tests


def test_get_action():
    from shock.core import getAction
    fn = getAction
    fn2 = getAction("core", "getAction")
    assert fn==fn2


@patch('shock.core.Shock.waitForActions')
def test_wait_for_actions_called(WaitForActionsMock):
    assert WaitForActionsMock is shock.core.Shock.waitForActions
    sck = shock.core.Shock(TestHandler)
    assert WaitForActionsMock.called


@patch('tests.helpers.TestHandler.handle')
def test_handle_messages_called_with_correct_args(THHandleMock):
    sck = shock.core.Shock(TestHandler)
    THHandleMock.assert_called_with('newstream', {})


def test_get_module():
    from shock.core import getClass
    mod = getClass('shock.core', 'Shock')
    assert mod == shock.core.Shock

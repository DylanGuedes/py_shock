import os
import json

from typing import Callable, TypeVar

AnyFunction = Callable
Handler = TypeVar('Handler')


def getAction(fileName: str, actionName: str) -> AnyFunction:
    """Load action from file inside shock folder

    Args:
        fileName (str): file that has the action.
        actionName (str): action that will be extracted from file.

    Returns:
        action: the call result.
    """
    modulefullpath = "shock."+fileName
    module = __import__(modulefullpath)
    action = getattr(module, fileName)
    return getattr(action, actionName)


class Shock():
    """This class serves as an abstraction for the communication between Spark
    and Kafka

    Examples (py):
        >>> shock = Shock(InterSCity)

    Examples (kafka-consumer):
        >>> newStream;{"stream": "mynicestream"}
        >>> ingestion;{"stream": "mynicestream", "shock_action": "bestaction"}
        >>> store;{"stream": "mynicestream", "shock_action": "castentity"}
        >>> publish;{"stream": "mynicestream", "shock_action": "parquetSink"}
    """

    def __init__(self, handler: Handler, environment="default") -> None:
        """Shock constructor.

        Args:
            handler (Handler): A Shock handler to be used.

        Examples:
            >>> sck = Shock(InterSCity)
        """
        self.handler = handler(environment)
        self.waitForActions()

    def waitForActions(self) -> None:
        """Consume Kafka's msg

        Expected Data:
            "actionname ;  {"key1": "val1", "key2": "val2", "keyn": "valn"}"
        """
        for pkg in self.handler.consumer:
            self.newActionSignal()
            msg = pkg.value.decode('ascii')
            self.handleNewKafkaMsg(msg)

    def handleNewKafkaMsg(self, msg: str) -> None:
        """Normalize Kafka message and send to be handled by the handler

        Args:
            msg (str): msg received, with at least one `;` char

        Returns:
            no return
        """
        try:
            splittedMsg = msg.split(";")
            actionName = splittedMsg[0].strip()
            args = json.loads(splittedMsg[1])
        except:
            raise('Invalid action requested!')
        self.handler.handle(actionName, args)


    def newActionSignal(self) -> None:
        """Alert handler about new action arrived.

        Args:
            no arguments

        Returns:
            no return
        """
        self.handler.newActionSignal()

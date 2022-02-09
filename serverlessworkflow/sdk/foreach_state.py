from enum import Enum
from typing import Union

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.foreach_state_timeout import ForEachStateTimeOut
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class ForEachStateMode(Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class ForEachState:
    id: str = None
    name: str = None
    type: str = None
    end: Union[bool, End] = None
    inputCollection: str = None
    outputCollection: str = None
    iterationParam: str = None
    batchSize: Union[int, str] = None
    actions: [Action] = None
    timeouts: ForEachStateTimeOut = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: Union[str, Transition] = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    mode: ForEachStateMode = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 end: Union[bool, End] = None,
                 inputCollection: str = None,
                 outputCollection: str = None,
                 iterationParam: str = None,
                 batchSize: Union[int, str] = None,
                 actions: [Action] = None,
                 timeouts: ForEachStateTimeOut = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: Union[str, Transition] = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 mode: ForEachStateMode = None,
                 metadata: Metadata = None,
                 **kwargs):

        # duplicated
        for local in list(locals()):
            if local in ["self", "kwargs"]:
                continue
            value = locals().get(local)
            if not value:
                continue
            if value == "true":
                value = True
            # duplicated

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            self.__setattr__(k.replace("_", ""), value)
            # duplicated

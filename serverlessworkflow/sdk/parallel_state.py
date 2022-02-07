from enum import Enum
from typing import Union

from serverlessworkflow.sdk.branch import Branch
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.parallel_state_timeout import ParallelStateTimeOut
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class ParallelStateCompletionType(Enum):
    allOf = "allOf"
    atLeast = "atLeast"


class ParallelState:
    id: str = None
    name: str = None
    type: str = None
    end: Union[bool, End] = None
    stateDataFilter: StateDataFilter = None
    timeouts: ParallelStateTimeOut = None
    branches: [Branch] = None
    completionType: ParallelStateCompletionType = None
    numCompleted: Union[int, str] = None
    onErrors: [Error] = None
    transition: Union[str, Transition] = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 end: Union[bool, End] = None,
                 stateDataFilter: StateDataFilter = None,
                 timeouts: ParallelStateTimeOut = None,
                 branches: [Branch] = None,
                 completionType: ParallelStateCompletionType = None,
                 numCompleted: Union[int, str] = None,
                 onErrors: [Error] = None,
                 transition: Union[str, Transition] = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
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

from typing import Union, Dict

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.inject_state_timeout import InjectStateTimeOut
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class InjectState:
    id: str = None
    name: str = None
    type: 'inject' = None
    end: Union[bool, End] = None
    data: Union[str, Dict[str, Dict]] = None
    timeouts: InjectStateTimeOut = None
    stateDataFilter: StateDataFilter = None
    transition: Union[str, Transition] = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: 'inject' = None,
                 end: Union[bool, End] = None,
                 data: Union[str, Dict[str, Dict]] = None,
                 timeouts: InjectStateTimeOut = None,
                 stateDataFilter: StateDataFilter = None,
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

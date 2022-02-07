from typing import Union

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.callback_state_timeout import CallbackStateTimeOut
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_data_filter import EventDataFilter
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class CallbackState:
    id: str = None
    name: str = None
    type: 'callback' = None
    action: Action = None
    eventRef: str = None
    timeouts: CallbackStateTimeOut = None
    eventDataFilter: EventDataFilter = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: Union[str, Transition] = None
    end: Union[bool, End] = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: 'callback' = None,
                 action: Action = None,
                 eventRef: str = None,
                 timeouts: CallbackStateTimeOut = None,
                 eventDataFilter: EventDataFilter = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: Union[str, Transition] = None,
                 end: Union[bool, End] = None,
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

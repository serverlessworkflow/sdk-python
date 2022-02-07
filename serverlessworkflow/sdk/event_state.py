from typing import Union

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_state_timeout import EventStateTimeOut
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.on_events import OnEvents
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class EventState:
    id: str = None
    name: str = None
    type: 'event' = None
    exclusive: bool = None
    onEvents: [OnEvents] = None
    timeouts: EventStateTimeOut = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: Union[str, Transition] = None
    end: Union[bool, End] = None
    compensatedBy: str = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: 'event' = None,
                 exclusive: bool = None,
                 onEvents: [OnEvents] = None,
                 timeouts: EventStateTimeOut = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: Union[str, Transition] = None,
                 end: Union[bool, End] = None,
                 compensatedBy: str = None,
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

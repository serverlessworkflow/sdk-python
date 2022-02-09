from typing import Union

from serverlessworkflow.sdk.default_condition_def import DefaultConditionDef
from serverlessworkflow.sdk.end_event_condition import EndEventCondition
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_based_switch_state_timeout import EventBasedSwitchStateTimeOut
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition_event_condition import TransitionEventCondition


class EventBasedSwitchState:
    id: str = None
    name: str = None
    type: str = None
    stateDataFilter: StateDataFilter = None
    timeouts: EventBasedSwitchStateTimeOut = None
    eventConditions: Union[TransitionEventCondition, EndEventCondition] = None  # Eventcondition
    onErrors: [Error] = None
    defaultCondition: DefaultConditionDef = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: 'switch' = None,
                 stateDataFilter: StateDataFilter = None,
                 timeouts: EventBasedSwitchStateTimeOut = None,
                 eventConditions: Union[TransitionEventCondition, EndEventCondition] = None,  # Eventcondition
                 onErrors: [Error] = None,
                 defaultCondition: DefaultConditionDef = None,
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

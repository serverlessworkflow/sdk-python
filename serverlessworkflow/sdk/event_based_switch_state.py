from __future__ import annotations

import copy

from serverlessworkflow.sdk.default_condition_def import DefaultConditionDef
from serverlessworkflow.sdk.end_event_condition import EndEventCondition
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_based_switch_state_timeout import EventBasedSwitchStateTimeOut
from serverlessworkflow.sdk.hydration import HydratableParameter, ComplexTypeOf, UnionTypeOf, ArrayTypeOf, \
    Fields
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition_event_condition import TransitionEventCondition


class EventBasedSwitchState(State):
    id: str = None
    name: str = None
    type: str = None
    stateDataFilter: StateDataFilter = None
    timeouts: EventBasedSwitchStateTimeOut = None
    eventConditions: ([TransitionEventCondition] | [EndEventCondition]) = None  # Eventcondition
    onErrors: [Error] = None
    defaultCondition: DefaultConditionDef = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 stateDataFilter: StateDataFilter = None,
                 timeouts: EventBasedSwitchStateTimeOut = None,
                 eventConditions: ([TransitionEventCondition] | [EndEventCondition]) = None,  # Eventcondition
                 onErrors: [Error] = None,
                 defaultCondition: DefaultConditionDef = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 **kwargs):
        Fields(locals(), kwargs, EventBasedSwitchState.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventBasedSwitchStateTimeOut))

        if p_key == 'eventConditions':
            return [EventBasedSwitchState.hydrate_state(v) if type(v) is not (TransitionEventCondition or EndEventCondition) else v for v in p_value]

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'defaultCondition':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(DefaultConditionDef))

        return copy.deepcopy(p_value)

    @staticmethod
    def hydrate_state(event):

        state = State(**event)
        if hasattr(state, "transition"):
            return TransitionEventCondition(**event)
        if hasattr(state, "end"):
            return EndEventCondition(**event)
        raise Exception(f"Unexpected EventBasedSwitchState value: {event}")

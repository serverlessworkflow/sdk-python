from __future__ import annotations

import copy

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_state_timeout import EventStateTimeOut
from serverlessworkflow.sdk.hydration import ArrayTypeOf, HydratableParameter, ComplexTypeOf, UnionTypeOf, \
    SimpleTypeOf, Fields
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.on_events import OnEvents
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.transition import Transition


class EventState(State):
    id: str = None
    name: str = None
    type: str = None
    exclusive: bool = None
    onEvents: [OnEvents] = None
    timeouts: EventStateTimeOut = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: (str | Transition) = None
    end: (bool | End) = None
    compensatedBy: str = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 exclusive: bool = None,
                 onEvents: [OnEvents] = None,
                 timeouts: EventStateTimeOut = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 end: (bool | End) = None,
                 compensatedBy: str = None,
                 metadata: Metadata = None,
                 **kwargs):

        Fields(locals(), kwargs, EventState.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'onEvents':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(OnEvents))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventStateTimeOut))

        if p_key == 'stateDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateDataFilter))

        if p_key == 'onErrors':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Error))

        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        if p_key == 'end':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(bool),
                                                                             ComplexTypeOf(End)]))

        return copy.deepcopy(p_value)

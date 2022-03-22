from __future__ import annotations

import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.callback_state_timeout import CallbackStateTimeOut
from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.error import Error
from serverlessworkflow.sdk.event_data_filter import EventDataFilter
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.state import State
from serverlessworkflow.sdk.state_data_filter import StateDataFilter
from serverlessworkflow.sdk.swf_base import ComplexTypeOf, ArrayTypeOf, HydratableParameter, SimpleTypeOf, \
    UnionTypeOf, SwfBase
from serverlessworkflow.sdk.transition import Transition


class CallbackState(State, SwfBase):
    id: str = None
    name: str = None
    type: str = None
    action: Action = None
    eventRef: str = None
    timeouts: CallbackStateTimeOut = None
    eventDataFilter: EventDataFilter = None
    stateDataFilter: StateDataFilter = None
    onErrors: [Error] = None
    transition: (str | Transition) = None
    end: (bool | End) = None
    compensatedBy: str = None
    usedForCompensation: bool = None
    metadata: Metadata = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 action: Action = None,
                 eventRef: str = None,
                 timeouts: CallbackStateTimeOut = None,
                 eventDataFilter: EventDataFilter = None,
                 stateDataFilter: StateDataFilter = None,
                 onErrors: [Error] = None,
                 transition: (str | Transition) = None,
                 end: (bool | End) = None,
                 compensatedBy: str = None,
                 usedForCompensation: bool = None,
                 metadata: Metadata = None,
                 **kwargs):

        _default_values = {'type': 'callback', 'usedForCompensation': False, }
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration, _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'action':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(Action))

        if p_key == 'timeouts':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(CallbackStateTimeOut))

        if p_key == 'eventDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventDataFilter))

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

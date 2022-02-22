from __future__ import annotations

import copy

from serverlessworkflow.sdk.event_data_filter import EventDataFilter
from serverlessworkflow.sdk.hydration import HydratableParameter, UnionTypeOf, SimpleTypeOf, ComplexTypeOf, \
    Fields
from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.transition import Transition


class TransitionEventCondition:
    name: str = None
    eventRef: str = None
    transition: (str | Transition) = None
    eventDataFilter: EventDataFilter = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 eventRef: str = None,
                 transition: (str | Transition) = None,
                 eventDataFilter: EventDataFilter = None,
                 metadata: Metadata = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'transition':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(Transition)]))

        if p_key == 'eventDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventDataFilter))

        return copy.deepcopy(p_value)

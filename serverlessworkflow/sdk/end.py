from __future__ import annotations

import copy

from serverlessworkflow.sdk.continue_as_def import ContinueAsDef
from serverlessworkflow.sdk.hydration import HydratableParameter, ArrayTypeOf, UnionTypeOf, SimpleTypeOf, \
    ComplexTypeOf, Fields
from serverlessworkflow.sdk.produce_event_def import ProduceEventDef


class End:
    terminate: bool = None
    produceEvents: [ProduceEventDef] = None
    compensate: bool = None
    continueAs: (str | ContinueAsDef) = None

    def __init__(self,
                 terminate: bool = None,
                 produceEvents: [ProduceEventDef] = None,
                 compensate: bool = None,
                 continueAs: (str | ContinueAsDef) = None,
                 **kwargs):
        Fields(locals(), kwargs, End.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'produceEvents':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(ProduceEventDef))

        if p_key == 'continueAs':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(ContinueAsDef)]))

        return copy.deepcopy(p_value)

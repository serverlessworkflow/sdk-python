import copy

from serverlessworkflow.sdk.produce_event_def import ProduceEventDef
from serverlessworkflow.sdk.swf_base import ArrayTypeOf, HydratableParameter, SwfBase


class Transition(SwfBase):
    nextState: str = None
    produceEvents: [ProduceEventDef] = None
    compensate: bool = None

    def __init__(self,
                 nextState: str = None,
                 produceEvents: [ProduceEventDef] = None,
                 compensate: bool = None,
                 **kwargs):
        _default_values = {'compensate': False}
        SwfBase.__init__(self, locals(), kwargs, Transition.f_hydration,
                         _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'produceEvents':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(ProduceEventDef))

        return copy.deepcopy(p_value)

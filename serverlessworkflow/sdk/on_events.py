import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.event_data_filter import EventDataFilter
from serverlessworkflow.sdk.swf_base import HydratableParameter, ArrayTypeOf, ComplexTypeOf, SwfBase


class OnEvents(SwfBase):
    eventRefs: [str] = None
    actionMode: str = None
    actions: [Action] = None
    eventDataFilter: EventDataFilter = None

    def __init__(self,
                 eventRefs: [str] = None,
                 actionMode: str = None,
                 actions: [Action] = None,
                 eventDataFilter: EventDataFilter = None,
                 **kwargs):

        _default_values = {'actionMode': 'sequential'}
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration, _default_values)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'actions':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Action))

        if p_key == 'eventDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventDataFilter))

        return copy.deepcopy(p_value)

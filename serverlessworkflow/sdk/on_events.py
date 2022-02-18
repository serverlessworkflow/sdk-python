import copy

from serverlessworkflow.sdk.action import Action
from serverlessworkflow.sdk.event_data_filter import EventDataFilter
from serverlessworkflow.sdk.hydration import HydratableParameter, ArrayTypeOf, ComplexTypeOf, Fields


class OnEvents:
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
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'actions':
            return HydratableParameter(value=p_value).hydrateAs(ArrayTypeOf(Action))

        if p_key == 'eventDataFilter':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(EventDataFilter))

        return copy.deepcopy(p_value)

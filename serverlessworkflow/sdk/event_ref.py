from __future__ import annotations

import copy

from serverlessworkflow.sdk.hydration import HydratableParameter, ComplexTypeOf, UnionTypeOf, SimpleTypeOf, \
    Fields


class EventRef:
    triggerEventRef: str = None
    resultEventRef: str = None
    resultEventTimeOut: str = None
    data: (str | dict) = None
    contextAttributes: dict[str, str] = None
    invoke: str = None

    def __init__(self,
                 triggerEventRef: str = None,
                 resultEventRef: str = None,
                 data: (str | dict) = None,
                 contextAttributes: dict[str, str] = None,
                 invoke: str = None,
                 **kwargs):

        Fields(locals(), kwargs, EventRef.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):

        if p_key == 'data':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str), ComplexTypeOf(dict)]))

        if p_key == 'contextAttributes':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(dict))

        return copy.deepcopy(p_value)

from __future__ import annotations

import copy

from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, SimpleTypeOf, UnionTypeOf, SwfBase


class ProduceEventDef(SwfBase):
    eventRef: str = None
    data: (str | dict) = None
    contextAttributes: dict[str, str] = None

    def __init__(self,
                 eventRef: str = None,
                 data: (str | dict) = None,
                 contextAttributes: dict[str, str] = None,
                 **kwargs):

        SwfBase.__init__(self, locals(), kwargs, ProduceEventDef.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'data':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(dict)]))

        if p_key == 'contextAttributes':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(dict))

        return copy.deepcopy(p_value)

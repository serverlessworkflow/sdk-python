from __future__ import annotations

import copy

from serverlessworkflow.sdk.schedule import Schedule
from serverlessworkflow.sdk.swf_base import SimpleTypeOf, ComplexTypeOf, UnionTypeOf, HydratableParameter, SwfBase


class StartDef(SwfBase):
    stateName: str = None
    schedule: (str | Schedule) = None

    def __init__(self,
                 stateName: str = None,
                 schedule: (str | Schedule) = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, StartDef.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'schedule':
            return HydratableParameter(value=p_value).hydrateAs(
                UnionTypeOf([SimpleTypeOf(str), ComplexTypeOf(Schedule)]))

        return copy.deepcopy(p_value)

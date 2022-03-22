from __future__ import annotations

import copy

from serverlessworkflow.sdk.cron_def import CronDef
from serverlessworkflow.sdk.swf_base import HydratableParameter, SimpleTypeOf, ComplexTypeOf, UnionTypeOf, SwfBase


class Schedule(SwfBase):
    interval: str = None
    cron: (str | CronDef) = None
    timezone: str = None

    def __init__(self,
                 interval: str = None,
                 cron: (str | CronDef) = None,
                 timezone: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, Schedule.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'cron':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(CronDef)]))

        return copy.deepcopy(p_value)

from __future__ import annotations

import copy

from serverlessworkflow.sdk.cron_def import CronDef
from serverlessworkflow.sdk.hydration import HydratableParameter, SimpleTypeOf, ComplexTypeOf, UnionTypeOf, \
    Fields


class Schedule:
    interval: str = None
    cron: (str | CronDef) = None
    timezone: str = None

    def __init__(self,
                 interval: str = None,
                 cron: (str | CronDef) = None,
                 timezone: str = None,
                 **kwargs):
        Fields(locals(), kwargs, Schedule.f_hydration).set_to_object(self)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'cron':
            return HydratableParameter(value=p_value).hydrateAs(UnionTypeOf([SimpleTypeOf(str),
                                                                             ComplexTypeOf(CronDef)]))

        return copy.deepcopy(p_value)

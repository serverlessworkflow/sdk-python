import copy

from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut
from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, SwfBase


class EventStateTimeOut(SwfBase):
    stateExecTimeOut: StateExecTimeOut = None
    actionExecTimeOut: str = None  # ActionExecTimeOut
    eventTimeOut: str = None  # EventTimeOut

    def __init__(self,
                 stateExecTimeOut: StateExecTimeOut = None,
                 actionExecTimeOut: str = None,
                 eventTimeOut: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, EventStateTimeOut.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

        return copy.deepcopy(p_value)

from serverlessworkflow.sdk.state_exec_timeout import StateExecTimeOut
from serverlessworkflow.sdk.swf_base import HydratableParameter, ComplexTypeOf, SwfBase


class SleepStateTimeOut(SwfBase):
    stateExecTimeOut: StateExecTimeOut = None

    def __init__(self,
                 stateExecTimeOut: StateExecTimeOut = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SleepStateTimeOut.f_hydration)

    @staticmethod
    def f_hydration(p_key, p_value):
        if p_key == 'stateExecTimeOut':
            return HydratableParameter(value=p_value).hydrateAs(ComplexTypeOf(StateExecTimeOut))

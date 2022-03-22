from serverlessworkflow.sdk.swf_base import SwfBase


class WorkflowExecTimeOut(SwfBase):
    duration: str = None
    interrupt: bool = None
    runBefore: str = None

    def __init__(self,
                 duration: str = None,
                 interrupt: bool = None,
                 runBefore: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

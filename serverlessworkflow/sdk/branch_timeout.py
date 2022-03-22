from serverlessworkflow.sdk.swf_base import SwfBase


class BranchTimeOut(SwfBase):
    actionExecTimeOut: str = None  # ActionExecTimeOut
    branchExecTimeOut: str = None  # BranchExecTimeOut

    def __init__(self,
                 actionExecTimeOut: str = None,
                 branchExecTimeOut: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

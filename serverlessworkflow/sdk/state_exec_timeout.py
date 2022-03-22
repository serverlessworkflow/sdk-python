from serverlessworkflow.sdk.swf_base import SwfBase


class StateExecTimeOut(SwfBase):
    single: str = None
    total: str = None

    def __init__(self,
                 single: str = None,
                 total: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

from serverlessworkflow.sdk.swf_base import SwfBase


class StateDataFilter(SwfBase):
    input: str = None
    output: str = None

    def __init__(self,
                 input: str = None,
                 output: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

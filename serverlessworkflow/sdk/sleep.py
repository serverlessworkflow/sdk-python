from serverlessworkflow.sdk.swf_base import SwfBase


class Sleep(SwfBase):
    before: str = None
    after: str = None

    def __init__(self,
                 before: str = None,
                 after: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

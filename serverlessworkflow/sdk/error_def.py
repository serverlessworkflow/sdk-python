from serverlessworkflow.sdk.swf_base import SwfBase


class ErrorDef(SwfBase):
    name: str = None
    code: str = None
    description: str = None

    def __init__(self,
                 name: str = None,
                 code: str = None,
                 description: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

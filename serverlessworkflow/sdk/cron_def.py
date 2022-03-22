from serverlessworkflow.sdk.swf_base import SwfBase


class CronDef(SwfBase):
    expression: str = None
    validUntil: str = None

    def __init__(self,
                 expression: str = None,
                 validUntil: str = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

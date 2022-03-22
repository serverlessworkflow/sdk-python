from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import SwfBase


class BearerPropsDef(SwfBase):
    token: str = None
    metadata: Metadata = None

    def __init__(self,
                 token: str = None,
                 metadata: Metadata = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

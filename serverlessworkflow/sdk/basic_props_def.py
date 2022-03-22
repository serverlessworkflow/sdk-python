from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import SwfBase


class BasicPropsDef(SwfBase):
    username: str = None
    password: str = None
    metadata: Metadata = None

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 metadata: Metadata = None,
                 **kwargs):
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration)

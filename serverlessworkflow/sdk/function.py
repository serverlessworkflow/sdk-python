from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.swf_base import SwfBase


class Function(SwfBase):
    name: str = None
    operation: str = None
    type: str = None
    authRef: str = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 operation: str = None,
                 type: str = None,
                 authRef: str = None,
                 metadata: Metadata = None,
                 **kwargs):
        _default_values = {'type': 'rest'}
        SwfBase.__init__(self, locals(), kwargs, SwfBase.default_hydration,
                         _default_values)

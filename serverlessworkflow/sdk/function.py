from serverlessworkflow.sdk.hydration import Fields
from serverlessworkflow.sdk.metadata import Metadata


class Function:
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
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)

from serverlessworkflow.sdk.hydration import Fields
from serverlessworkflow.sdk.metadata import Metadata


class BasicPropsDef:
    username: str = None
    password: str = None
    metadata: Metadata = None

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 metadata: Metadata = None,
                 **kwargs):
        Fields(locals(), kwargs, Fields.default_hydration).set_to_object(self)

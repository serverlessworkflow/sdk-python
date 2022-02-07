from enum import Enum
from typing import Union, List

from serverlessworkflow.sdk.correlation_def import CorrelationDef
from serverlessworkflow.sdk.metadata import Metadata


class Kind(Enum):
    CONSUMED = "consumed"
    PRODUCED = "produced"


class EventDef:
    name: str = None
    source: str = None
    type: str = None
    kind: Kind = None
    correlation: Union[CorrelationDef, List[CorrelationDef]] = None
    dataOnly: bool = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 source: str = None,
                 type: str = None,
                 kind: Kind = None,
                 correlation: Union[CorrelationDef, List[CorrelationDef]] = None,  # CorrelationDefs
                 dataOnly: bool = None,
                 metadata: Metadata = None,
                 **kwargs):

        # duplicated
        for local in list(locals()):
            if local in ["self", "kwargs"]:
                continue
            value = locals().get(local)
            if not value:
                continue
            if value == "true":
                value = True
            # duplicated

            self.__setattr__(local.replace("_", ""), value)

        # duplicated
        for k in kwargs.keys():
            value = kwargs[k]
            if value == "true":
                value = True

            self.__setattr__(k.replace("_", ""), value)
            # duplicated

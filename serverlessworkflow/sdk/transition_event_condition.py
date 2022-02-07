from typing import Union

from serverlessworkflow.sdk.metadata import Metadata
from serverlessworkflow.sdk.transition import Transition


class TransitionEventCondition:
    name: str = None
    eventRef: str = None
    transition: Union[str, Transition] = None
    eventDataFilter = None
    metadata: Metadata = None

    def __init__(self,
                 name: str = None,
                 eventRef: str = None,
                 transition: Union[str, Transition] = None,
                 eventDataFilter=None,
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

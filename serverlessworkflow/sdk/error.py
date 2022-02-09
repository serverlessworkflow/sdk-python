from typing import Union

from serverlessworkflow.sdk.end import End
from serverlessworkflow.sdk.transition import Transition


class Error:
    errorRef: str = None
    errorRefs: [str] = None
    transition: Union[str, Transition] = None
    end: Union[bool, End] = None

    def __init__(self,
                 errorRef: str = None,
                 errorRefs: [str] = None,
                 transition: Union[str, Transition] = None,
                 end: Union[bool, End] = None,
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

from typing import Union

from serverlessworkflow.sdk.schedule import Schedule


class StartDef:
    stateName: str = None
    schedule: Union[str, Schedule] = None

    def __init__(self,
                 stateName: str = None,
                 schedule: Union[str, Schedule] = None,
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

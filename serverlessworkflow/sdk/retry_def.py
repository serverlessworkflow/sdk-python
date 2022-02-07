from typing import Union


class RetryDef:
    name: str = None
    delay: str = None
    maxDelay: str = None
    increment: str = None
    multiplier: Union[int, str] = None
    maxAttempts: Union[int, str] = None
    jitter: Union[int, str] = None

    def __init__(self,
                 name: str = None,
                 delay: str = None,
                 maxDelay: str = None,
                 increment: str = None,
                 multiplier: Union[int, str] = None,
                 maxAttempts: Union[int, str] = None,
                 jitter: Union[int, str] = None,
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

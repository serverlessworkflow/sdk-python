class ActionDataFilter:
    fromStateData: str = None
    useResults: bool = None
    results: str = None
    toStateData: str = None

    def __init__(self,
                 fromStateData: str = None,
                 useResults: bool = None,
                 results: str = None,
                 toStateData: str = None,
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

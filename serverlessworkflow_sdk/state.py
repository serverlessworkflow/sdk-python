__author__ = "Serverless Workflow Specification"
__copyright__ = "Copyright 2020-Present The Serverless Workflow Specification Authors"
__license__ = "Apache License, Version 2.0"
class State:
    type: str

    def __init__(self, data: dict = None,
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

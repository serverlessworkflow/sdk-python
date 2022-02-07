from enum import Enum

from serverlessworkflow.sdk.metadata import Metadata


class Oauth2PropsDefGrantType(Enum):
    password = "password"
    clientCredentials = "clientCredentials"
    tokenExchange = "tokenExchange"


class Oauth2PropsDef:
    authority: str = None
    grantType: Oauth2PropsDefGrantType = None
    clientId: str = None
    clientSecret: str = None
    scopes: [str] = None
    username: str = None
    password: str = None
    audiences: [str] = None
    subjectToken: str = None
    requestedSubject: str = None
    requestedIssuer: str = None
    metadata: Metadata = None

    def __init__(self,
                 authority: str = None,
                 grantType: Oauth2PropsDefGrantType = None,
                 clientId: str = None,
                 clientSecret: str = None,
                 scopes: [str] = None,
                 username: str = None,
                 password: str = None,
                 audiences: [str] = None,
                 subjectToken: str = None,
                 requestedSubject: str = None,
                 requestedIssuer: str = None,
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

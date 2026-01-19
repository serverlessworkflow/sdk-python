"""Authentication policy classes for Serverless Workflow SDK v1."""

from dataclasses import dataclass

from serverlessworkflow.sdk.base import UriTemplate


@dataclass
class OAuth2Token:
    """Represents an OAuth2 token."""

    token: str
    type: str


@dataclass
class OAuth2Client:
    """Definition of an OAuth2 client."""

    id: str
    secret: str | None = None
    assertion: str | None = None
    authentication: str = "client_secret_post"


@dataclass
class OAuth2TokenRequest:
    """Configuration of an OAuth2 token request."""

    encoding: str = "application/x-www-form-urlencoded"


@dataclass
class OAuth2Endpoints:
    """Endpoint configurations for OAuth2."""

    token: str = "/oauth2/token"
    revocation: str = "/oauth2/revoke"
    introspection: str = "/oauth2/introspect"


@dataclass
class BasicAuthenticationConfiguration:
    """Configuration for basic authentication."""

    username: str | None = None
    password: str | None = None
    use: str | None = None

    def __post_init__(self):
        """Validate basic authentication configuration."""
        has_inline = self.username is not None and self.password is not None
        has_secret = self.use is not None
        if not (has_inline or has_secret):
            raise ValueError("Either username/password or use must be specified")
        if has_inline and has_secret:
            raise ValueError("Cannot specify both inline credentials and secret reference")


@dataclass
class BasicAuthenticationPolicy:
    """Basic authentication policy."""

    basic: BasicAuthenticationConfiguration


@dataclass
class BearerAuthenticationConfiguration:
    """Configuration for bearer authentication."""

    token: str | None = None
    use: str | None = None

    def __post_init__(self):
        """Validate bearer authentication configuration."""
        has_inline = self.token is not None
        has_secret = self.use is not None
        if not (has_inline or has_secret):
            raise ValueError("Either token or use must be specified")
        if has_inline and has_secret:
            raise ValueError("Cannot specify both inline token and secret reference")


@dataclass
class BearerAuthenticationPolicy:
    """Bearer authentication policy."""

    bearer: BearerAuthenticationConfiguration


@dataclass
class DigestAuthenticationConfiguration:
    """Configuration for digest authentication."""

    username: str | None = None
    password: str | None = None
    use: str | None = None

    def __post_init__(self):
        """Validate digest authentication configuration."""
        has_inline = self.username is not None and self.password is not None
        has_secret = self.use is not None
        if not (has_inline or has_secret):
            raise ValueError("Either username/password or use must be specified")
        if has_inline and has_secret:
            raise ValueError("Cannot specify both inline credentials and secret reference")


@dataclass
class DigestAuthenticationPolicy:
    """Digest authentication policy."""

    digest: DigestAuthenticationConfiguration


@dataclass
class OAuth2AuthenticationConfiguration:
    """Configuration for OAuth2 authentication."""

    authority: UriTemplate | None = None
    grant: str | None = None
    client: OAuth2Client | None = None
    request: OAuth2TokenRequest | None = None
    issuers: list[str] | None = None
    scopes: list[str] | None = None
    audiences: list[str] | None = None
    username: str | None = None
    password: str | None = None
    subject: OAuth2Token | None = None
    actor: OAuth2Token | None = None
    endpoints: OAuth2Endpoints | None = None
    use: str | None = None


@dataclass
class OAuth2AuthenticationPolicy:
    """OAuth2 authentication policy."""

    oauth2: OAuth2AuthenticationConfiguration


@dataclass
class OpenIdConnectAuthenticationPolicy:
    """OpenID Connect authentication policy."""

    oidc: OAuth2AuthenticationConfiguration


@dataclass
class ReferenceableAuthenticationPolicy:
    """Referenceable authentication policy - either a reference or an inline policy."""

    use: str | None = None
    basic: BasicAuthenticationConfiguration | None = None
    bearer: BearerAuthenticationConfiguration | None = None
    digest: DigestAuthenticationConfiguration | None = None
    oauth2: OAuth2AuthenticationConfiguration | None = None
    oidc: OAuth2AuthenticationConfiguration | None = None

    def __post_init__(self):
        """Validate authentication policy configuration."""
        policies = [self.basic, self.bearer, self.digest, self.oauth2, self.oidc]
        set_policies = [p for p in policies if p is not None]
        if self.use is not None and len(set_policies) > 0:
            raise ValueError("Cannot specify both 'use' reference and inline policy")
        if self.use is None and len(set_policies) != 1:
            raise ValueError("Must specify either 'use' reference or exactly one inline policy")

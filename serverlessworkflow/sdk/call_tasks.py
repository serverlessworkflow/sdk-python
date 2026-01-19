"""Call task classes for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serverlessworkflow.sdk.base import Export, Output, TaskItem

from serverlessworkflow.sdk.authentication import ReferenceableAuthenticationPolicy
from serverlessworkflow.sdk.base import Duration, ExternalResource, TaskBase
from serverlessworkflow.sdk.endpoint import Endpoint

# AsyncAPI related classes


@dataclass
class AsyncApiServer:
    """Configures the target server of an AsyncAPI operation."""

    name: str
    variables: dict[str, Any] | None = None


@dataclass
class AsyncApiOutboundMessage:
    """Message configuration for AsyncAPI publish operations."""

    payload: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None


@dataclass
class AsyncApiInboundMessage:
    """Message consumed by an AsyncAPI subscription."""

    payload: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    correlationId: str | None = None


@dataclass
class SubscriptionIterator:
    """Configures iteration over consumed items."""

    item: str | None = None
    at: str | None = None
    do: list[TaskItem] | None = None
    output: Output | None = None
    export: Export | None = None


@dataclass
class AsyncApiMessageConsumptionPolicy:
    """Message consumption policy for AsyncAPI subscriptions."""

    amount: int | None = None
    while_: str | None = field(default=None, metadata={"alias": "while"})
    until: str | None = None  # Runtime expression
    for_: Duration | None = field(default=None, metadata={"alias": "for"})

    def __post_init__(self):
        """Validate consumption policy configuration."""
        policies = [self.amount, self.while_, self.until]
        set_policies = [p for p in policies if p is not None]
        if len(set_policies) != 1:
            raise ValueError("Must specify exactly one of: amount, while, or until")


@dataclass
class AsyncApiSubscription:
    """Subscription configuration for AsyncAPI operations."""

    consume: AsyncApiMessageConsumptionPolicy
    filter: str | None = None  # Runtime expression
    foreach: SubscriptionIterator | None = None


@dataclass
class CallAsyncApiArguments:
    """Arguments for AsyncAPI call."""

    document: ExternalResource
    operation: str | None = None
    channel: str | None = None
    server: AsyncApiServer | None = None
    protocol: str | None = None
    message: AsyncApiOutboundMessage | None = None
    subscription: AsyncApiSubscription | None = None
    authentication: ReferenceableAuthenticationPolicy | None = None

    def __post_init__(self):
        """Validate AsyncAPI call arguments."""
        # Must have either operation or channel
        if not self.operation and not self.channel:
            raise ValueError("Must specify either operation or channel")
        # Must have either message or subscription
        if not self.message and not self.subscription:
            raise ValueError("Must specify either message or subscription")


@dataclass
class CallAsyncApiTask(TaskBase):
    """AsyncAPI call task."""

    call: str = field(default="asyncapi", init=False)
    with_: CallAsyncApiArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate AsyncAPI task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("AsyncAPI call task requires 'with' arguments")


# gRPC related classes


@dataclass
class GrpcService:
    """GRPC service configuration."""

    name: str
    host: str
    port: int | None = None
    authentication: ReferenceableAuthenticationPolicy | None = None


@dataclass
class CallGrpcArguments:
    """Arguments for gRPC call."""

    proto: ExternalResource
    service: GrpcService
    method: str
    arguments: dict[str, Any] | None = None


@dataclass
class CallGrpcTask(TaskBase):
    """gRPC call task."""

    call: str = field(default="grpc", init=False)
    with_: CallGrpcArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate gRPC task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("gRPC call task requires 'with' arguments")


# HTTP related classes


@dataclass
class CallHttpArguments:
    """Arguments for HTTP call."""

    method: str
    endpoint: Endpoint
    headers: dict[str, str] | str | None = None  # Can be runtime expression
    body: Any | None = None
    query: dict[str, str] | str | None = None  # Can be runtime expression
    output: str | None = None  # raw, content, or response (defaults to content if not specified)
    redirect: bool | None = None


@dataclass
class CallHttpTask(TaskBase):
    """HTTP call task."""

    call: str = field(default="http", init=False)
    with_: CallHttpArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate HTTP task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("HTTP call task requires 'with' arguments")


# OpenAPI related classes


@dataclass
class CallOpenApiArguments:
    """Arguments for OpenAPI call."""

    document: ExternalResource
    operationId: str
    parameters: dict[str, Any] | None = None
    authentication: ReferenceableAuthenticationPolicy | None = None
    output: str | None = None  # raw, content, or response
    redirect: bool | None = None


@dataclass
class CallOpenApiTask(TaskBase):
    """OpenAPI call task."""

    call: str = field(default="openapi", init=False)
    with_: CallOpenApiArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate OpenAPI task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("OpenAPI call task requires 'with' arguments")


# A2A related classes


@dataclass
class CallA2AArguments:
    """Arguments for A2A call."""

    method: str
    agentCard: ExternalResource | None = None
    server: Endpoint | None = None
    parameters: dict[str, Any] | str | None = None


@dataclass
class CallA2ATask(TaskBase):
    """A2A call task."""

    call: str = field(default="a2a", init=False)
    with_: CallA2AArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate A2A task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("A2A call task requires 'with' arguments")


# MCP related classes


@dataclass
class McpHttpTransport:
    """HTTP transport for MCP."""

    endpoint: Endpoint
    headers: dict[str, str] | None = None


@dataclass
class McpStdioTransport:
    """STDIO transport for MCP."""

    command: str
    arguments: list[str] | None = None
    environment: dict[str, str] | None = None


@dataclass
class McpTransport:
    """MCP transport configuration."""

    http: McpHttpTransport | None = None
    stdio: McpStdioTransport | None = None
    options: dict[str, str] | None = None

    def __post_init__(self):
        """Validate MCP transport configuration."""
        if not self.http and not self.stdio:
            raise ValueError("Must specify either http or stdio transport")
        if self.http and self.stdio:
            raise ValueError("Cannot specify both http and stdio transport")


@dataclass
class McpClient:
    """MCP client description."""

    name: str
    version: str


@dataclass
class CallMcpArguments:
    """Arguments for MCP call."""

    method: str
    transport: McpTransport
    protocolVersion: str = "2025-06-18"
    parameters: dict[str, Any] | str | None = None
    timeout: Duration | None = None
    client: McpClient | None = None


@dataclass
class CallMcpTask(TaskBase):
    """MCP call task."""

    call: str = field(default="mcp", init=False)
    with_: CallMcpArguments | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate MCP task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.with_ is None:
            raise ValueError("MCP call task requires 'with' arguments")


# Function call


@dataclass
class CallFunctionTask(TaskBase):
    """Function call task."""

    call: str = ""  # The name of the function to call
    with_: dict[str, Any] | None = field(default=None, metadata={"alias": "with"})

    def __post_init__(self):
        """Validate function task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        # Ensure it's not one of the reserved call types
        reserved = ["asyncapi", "grpc", "http", "openapi", "a2a", "mcp"]
        if self.call in reserved:
            raise ValueError(f"call value '{self.call}' is reserved for specific call types")
        if not self.call:
            raise ValueError("call must be specified for function task")


# Union type for all call tasks
CallTask = (
    CallAsyncApiTask
    | CallGrpcTask
    | CallHttpTask
    | CallOpenApiTask
    | CallA2ATask
    | CallMcpTask
    | CallFunctionTask
)

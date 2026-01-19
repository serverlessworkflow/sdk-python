"""Base classes and types for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serverlessworkflow.sdk.endpoint import Endpoint
    from serverlessworkflow.sdk.tasks import Task


@dataclass
class RuntimeExpression:
    """A runtime expression pattern: ${...}."""

    expression: str

    def __post_init__(self):
        """Validate runtime expression format."""
        if not self.expression.startswith("${") or not self.expression.endswith("}"):
            raise ValueError(f"Runtime expression must match pattern ${{...}}: {self.expression}")


@dataclass
class UriTemplate:
    """A URI or URI template."""

    uri: str

    def __post_init__(self):
        """Validate URI format."""
        # Basic validation that it looks like a URI with scheme
        if "://" not in self.uri:
            raise ValueError(f"URI must contain a scheme (protocol://): {self.uri}")


@dataclass
class Duration:
    """Represents a duration in various formats."""

    days: int | None = None
    hours: int | None = None
    minutes: int | None = None
    seconds: int | None = None
    milliseconds: int | None = None
    iso8601: str | None = None
    expression: RuntimeExpression | None = None

    def __post_init__(self):
        """Validate that at least one duration field is set."""
        # At least one field must be set
        if not any(
            [
                self.days,
                self.hours,
                self.minutes,
                self.seconds,
                self.milliseconds,
                self.iso8601,
                self.expression,
            ]
        ):
            raise ValueError("At least one duration field must be set")


@dataclass
class ExternalResource:
    """Represents an external resource."""

    endpoint: Endpoint
    name: str | None = None


@dataclass
class Schema:
    """Represents a schema definition."""

    format: str = "json"
    document: Any | None = None
    resource: ExternalResource | None = None

    def __post_init__(self):
        """Validate that exactly one of document or resource is specified."""
        if self.document is None and self.resource is None:
            raise ValueError("Either document or resource must be specified")
        if self.document is not None and self.resource is not None:
            raise ValueError("Only one of document or resource can be specified")


@dataclass
class Input:
    """Configures the input of a workflow or task."""

    schema: Schema | None = None
    from_: str | dict[str, Any] | None = field(default=None, metadata={"alias": "from"})


@dataclass
class Output:
    """Configures the output of a workflow or task."""

    schema: Schema | None = None
    as_: str | dict[str, Any] | None = field(default=None, metadata={"alias": "as"})


@dataclass
class Export:
    """Configures export to context."""

    schema: Schema | None = None
    as_: str | dict[str, Any] | None = field(default=None, metadata={"alias": "as"})


@dataclass
class Timeout:
    """The definition of a timeout."""

    after: Duration


@dataclass
class Error:
    """Represents an error."""

    type: UriTemplate | RuntimeExpression
    status: int
    instance: str | RuntimeExpression | None = None
    title: str | RuntimeExpression | None = None
    detail: str | RuntimeExpression | None = None


@dataclass
class ErrorFilter:
    """Error filtering based on static values."""

    type: str | None = None
    status: int | None = None
    instance: str | None = None
    title: str | None = None
    details: str | None = None

    def __post_init__(self):
        """Validate that at least one error filter field is set."""
        if not any([self.type, self.status, self.instance, self.title, self.details]):
            raise ValueError("At least one error filter field must be set")


FlowDirective = str  # 'continue', 'exit', 'end', or task name


@dataclass
class TaskBase:
    """Base class for all tasks."""

    if_: str | None = field(default=None, metadata={"alias": "if"})
    input: Input | None = None
    output: Output | None = None
    export: Export | None = None
    timeout: Timeout | str | None = None
    then: FlowDirective | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class TaskItem:
    """A named task item."""

    name: str
    task: Task

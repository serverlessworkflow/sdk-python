"""Task classes for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serverlessworkflow.sdk.base import TaskItem

from serverlessworkflow.sdk.base import (
    Duration,
    Error,
    ErrorFilter,
    ExternalResource,
    FlowDirective,
    TaskBase,
)
from serverlessworkflow.sdk.call_tasks import SubscriptionIterator
from serverlessworkflow.sdk.events import EventConsumptionStrategy, EventProperties
from serverlessworkflow.sdk.retry import RetryPolicy

# Do Task


@dataclass
class DoTask(TaskBase):
    """Execute a list of tasks in sequence."""

    do: list[TaskItem] | None = None

    def __post_init__(self):
        """Validate do task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.do is None:
            raise ValueError("do must be specified for DoTask")


# Fork Task


@dataclass
class ForkConfiguration:
    """Configuration for fork task."""

    branches: list[TaskItem]
    compete: bool = False


@dataclass
class ForkTask(TaskBase):
    """Execute multiple tasks concurrently."""

    fork: ForkConfiguration | None = None

    def __post_init__(self):
        """Validate fork task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.fork is None:
            raise ValueError("fork must be specified for ForkTask")


# Emit Task


@dataclass
class EmitEventConfiguration:
    """Configuration for event emission."""

    with_: EventProperties = field(metadata={"alias": "with"})


@dataclass
class EmitConfiguration:
    """Configuration for emit task."""

    event: dict[str, Any]  # Event definition with 'with' property


@dataclass
class EmitTask(TaskBase):
    """Emit an event."""

    emit: EmitConfiguration | None = None

    def __post_init__(self):
        """Validate emit task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.emit is None:
            raise ValueError("emit must be specified for EmitTask")


# For Task


@dataclass
class ForConfiguration:
    """Configuration for for loop."""

    in_: str = field(metadata={"alias": "in"})  # Runtime expression
    each: str | None = None
    at: str | None = None


@dataclass
class ForTask(TaskBase):
    """Iterate over a collection."""

    for_: ForConfiguration | None = field(default=None, metadata={"alias": "for"})
    do: list[TaskItem] | None = None
    while_: str | None = field(default=None, metadata={"alias": "while"})  # Runtime expression

    def __post_init__(self):
        """Validate for task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.for_ is None:
            raise ValueError("for_ must be specified for ForTask")
        if self.do is None:
            raise ValueError("do must be specified for ForTask")


# Listen Task


@dataclass
class ListenConfiguration:
    """Configuration for listen task."""

    to: EventConsumptionStrategy
    read: str | None = None  # data, envelope, or raw


@dataclass
class ListenTask(TaskBase):
    """Listen for external events."""

    listen: ListenConfiguration | None = None
    foreach: SubscriptionIterator | None = None

    def __post_init__(self):
        """Validate listen task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.listen is None:
            raise ValueError("listen must be specified for ListenTask")


# Raise Task


@dataclass
class RaiseConfiguration:
    """Configuration for raise task."""

    error: Error | str  # Error definition or reference


@dataclass
class RaiseTask(TaskBase):
    """Raise an error."""

    raise_: RaiseConfiguration | None = field(default=None, metadata={"alias": "raise"})

    def __post_init__(self):
        """Validate raise task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.raise_ is None:
            raise ValueError("raise_ must be specified for RaiseTask")


# Run Task


@dataclass
class ContainerLifetime:
    """Container lifetime configuration."""

    cleanup: str = "never"  # always, never, or eventually
    after: Duration | None = None

    def __post_init__(self):
        """Validate container lifetime configuration."""
        if self.cleanup == "eventually" and self.after is None:
            raise ValueError("after must be specified when cleanup is 'eventually'")
        if self.cleanup != "eventually" and self.after is not None:
            raise ValueError("after can only be specified when cleanup is 'eventually'")


@dataclass
class ContainerConfiguration:
    """Container configuration for run task."""

    image: str
    name: str | None = None
    command: str | None = None
    ports: dict[str, Any] | None = None
    volumes: dict[str, Any] | None = None
    environment: dict[str, str] | None = None
    stdin: str | None = None
    arguments: list[str] | None = None
    lifetime: ContainerLifetime | None = None


@dataclass
class ScriptConfiguration:
    """Script configuration for run task."""

    language: str
    code: str | None = None
    source: ExternalResource | None = None
    stdin: str | None = None
    arguments: list[str] | None = None
    environment: dict[str, str] | None = None

    def __post_init__(self):
        """Validate script configuration."""
        if not self.code and not self.source:
            raise ValueError("Must specify either code or source")
        if self.code and self.source:
            raise ValueError("Cannot specify both code and source")


@dataclass
class ShellConfiguration:
    """Shell command configuration for run task."""

    command: str
    stdin: str | None = None
    arguments: list[str] | None = None
    environment: dict[str, str] | None = None


@dataclass
class WorkflowConfiguration:
    """Subworkflow configuration for run task."""

    namespace: str
    name: str
    version: str = "latest"
    input: dict[str, Any] | None = None


@dataclass
class RunConfiguration:
    """Configuration for run task."""

    await_: bool | None = field(
        default=None, metadata={"alias": "await"}
    )  # defaults to True if not specified
    return_: str | None = field(
        default=None, metadata={"alias": "return"}
    )  # stdout, stderr, code, all, or none (defaults to stdout if not specified)
    container: ContainerConfiguration | None = None
    script: ScriptConfiguration | None = None
    shell: ShellConfiguration | None = None
    workflow: WorkflowConfiguration | None = None

    def __post_init__(self):
        """Validate run configuration."""
        processes = [self.container, self.script, self.shell, self.workflow]
        set_processes = [p for p in processes if p is not None]
        if len(set_processes) != 1:
            raise ValueError("Must specify exactly one of: container, script, shell, or workflow")


@dataclass
class RunTask(TaskBase):
    """Execute external processes."""

    run: RunConfiguration | None = None

    def __post_init__(self):
        """Validate run task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.run is None:
            raise ValueError("run must be specified for RunTask")


# Set Task


@dataclass
class SetTask(TaskBase):
    """Set data."""

    set: dict[str, Any] | str | None = None  # Data to set or runtime expression

    def __post_init__(self):
        """Validate set task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.set is None:
            raise ValueError("set must be specified for SetTask")


# Switch Task


@dataclass
class SwitchCase:
    """A case within a switch task."""

    when: str | None = None  # Runtime expression
    then: FlowDirective = "continue"


@dataclass
class SwitchTask(TaskBase):
    """Conditional branching."""

    switch: list[dict[str, SwitchCase]] | None = None  # List of named cases

    def __post_init__(self):
        """Validate switch task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.switch is None:
            raise ValueError("switch must be specified for SwitchTask")


# Try Task


@dataclass
class CatchConfiguration:
    """Configuration for error catching."""

    errors: dict[str, ErrorFilter] | None = None
    as_: str | None = field(default=None, metadata={"alias": "as"})
    when: str | None = None  # Runtime expression
    exceptWhen: str | None = None  # Runtime expression
    retry: RetryPolicy | str | None = None
    do: list[TaskItem] | None = None


@dataclass
class TryTask(TaskBase):
    """Handle errors gracefully."""

    try_: list[TaskItem] | None = field(default=None, metadata={"alias": "try"})
    catch: CatchConfiguration | None = None

    def __post_init__(self):
        """Validate try task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.try_ is None:
            raise ValueError("try_ must be specified for TryTask")
        if self.catch is None:
            raise ValueError("catch must be specified for TryTask")


# Wait Task


@dataclass
class WaitTask(TaskBase):
    """Pause execution for a duration."""

    wait: Duration | None = None

    def __post_init__(self):
        """Validate wait task configuration."""
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        if self.wait is None:
            raise ValueError("wait must be specified for WaitTask")


# Union type for all tasks
Task = (
    DoTask
    | ForkTask
    | EmitTask
    | ForTask
    | ListenTask
    | RaiseTask
    | RunTask
    | SetTask
    | SwitchTask
    | TryTask
    | WaitTask
)

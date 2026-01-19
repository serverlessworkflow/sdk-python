"""Main workflow classes for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serverlessworkflow.sdk.base import Error
    from serverlessworkflow.sdk.tasks import Task

from serverlessworkflow.sdk.authentication import ReferenceableAuthenticationPolicy
from serverlessworkflow.sdk.base import Duration, Input, Output, TaskItem, Timeout
from serverlessworkflow.sdk.endpoint import Catalog
from serverlessworkflow.sdk.events import EventConsumptionStrategy
from serverlessworkflow.sdk.retry import RetryPolicy


@dataclass
class Document:
    """Documents the workflow."""

    dsl: str
    namespace: str
    name: str
    version: str
    title: str | None = None
    summary: str | None = None
    tags: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate document metadata."""
        # Validate patterns if needed
        # dsl, namespace, name should match their respective patterns
        pass


@dataclass
class Extension:
    """Definition of a task extension."""

    extend: str  # call, composite, emit, for, listen, raise, run, set, switch, try, wait, all
    when: str | None = None
    before: list[TaskItem] | None = None
    after: list[TaskItem] | None = None


@dataclass
class Use:
    """Defines reusable workflow components."""

    authentications: dict[str, ReferenceableAuthenticationPolicy] | None = None
    errors: dict[str, Error] | None = None
    extensions: list[dict[str, Extension]] | None = None
    functions: dict[str, Task] | None = None
    retries: dict[str, RetryPolicy] | None = None
    secrets: list[str] | None = None
    timeouts: dict[str, Timeout] | None = None
    catalogs: dict[str, Catalog] | None = None


@dataclass
class Schedule:
    """Schedules the workflow."""

    every: Duration | None = None
    cron: str | None = None
    after: Duration | None = None
    on: EventConsumptionStrategy | None = None

    def __post_init__(self):
        """Validate schedule configuration."""
        # At least one scheduling option should be set
        if not any([self.every, self.cron, self.after, self.on]):
            raise ValueError("At least one schedule option must be specified")


class Workflow:
    """The main workflow definition."""

    document: Document
    do: list[TaskItem]
    input: Input | None = None
    use: Use | None = None
    timeout: Timeout | str | None = None
    output: Output | None = None
    schedule: Schedule | None = None

    def __init__(
        self,
        document: Document,
        do: list[TaskItem],
        input: Input | None = None,
        use: Use | None = None,
        timeout: Timeout | str | None = None,
        output: Output | None = None,
        schedule: Schedule | None = None,
    ):
        """Initialize a new Workflow instance.

        Args:
            document: Workflow document metadata
            do: List of tasks to execute
            input: Input configuration
            use: Resources to use
            timeout: Workflow timeout
            output: Output configuration
            schedule: Workflow schedule
        """
        self.document = document
        self.do = do
        self.input = input
        self.use = use
        self.timeout = timeout
        self.output = output
        self.schedule = schedule

    def serialize(self) -> dict[str, Any]:
        """Serializes the Workflow to a dictionary."""
        result = {
            "document": self._serialize_value(self.document),
            "do": self._serialize_value(self.do),
        }
        if self.input is not None:
            result["input"] = self._serialize_value(self.input)
        if self.use is not None:
            result["use"] = self._serialize_value(self.use)
        if self.timeout is not None:
            result["timeout"] = self._serialize_value(self.timeout)
        if self.output is not None:
            result["output"] = self._serialize_value(self.output)
        if self.schedule is not None:
            result["schedule"] = self._serialize_value(self.schedule)
        return result

    @classmethod
    def _serialize_value(cls, value: Any) -> Any:
        """Recursively serialize a value to JSON-compatible types.

        For dataclasses:
        - Checks field metadata for explicit 'alias' to use as the output key
        - Falls back to stripping trailing underscore from field names (Python keyword convention)
        - Skips None values to match YAML's sparse representation

        This approach leverages dataclass field metadata where defined, and uses
        convention (trailing underscore) for Python reserved keywords elsewhere.
        """
        from dataclasses import fields, is_dataclass

        # Handle None
        if value is None:
            return None

        # Special handling for TaskItem: convert to single-key dict format
        if isinstance(value, TaskItem):
            # Return as {'taskName': taskObject} format
            return {value.name: cls._serialize_value(value.task)}

        # Handle dataclasses
        if is_dataclass(value) and not isinstance(value, type):
            # Convert dataclass to dict and handle field aliases
            result = {}
            for f in fields(value):
                field_value = getattr(value, f.name)
                # Skip None values to match YAML serialization
                if field_value is None:
                    continue
                # Check if field has an alias in metadata
                key = f.metadata["alias"] if f.metadata and "alias" in f.metadata else f.name
                result[key] = cls._serialize_value(field_value)
            return result

        # Handle dictionaries
        if isinstance(value, dict):
            return {k: cls._serialize_value(v) for k, v in value.items()}

        # Handle lists/tuples
        if isinstance(value, (list | tuple)):
            return [cls._serialize_value(item) for item in value]

        # Return as-is for other types
        return value

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Workflow:
        """Parses a Workflow from a YAML string."""
        import yaml

        # Create a custom loader that doesn't convert 'on', 'yes', 'no', etc. to booleans
        class StringBoolLoader(yaml.SafeLoader):
            pass

        # Remove the implicit boolean resolvers that convert on/off/yes/no to booleans
        # This ensures 'on:' stays as the string 'on' instead of becoming True
        for ch in ["o", "O", "y", "Y", "n", "N"]:
            if ch in StringBoolLoader.yaml_implicit_resolvers:
                StringBoolLoader.yaml_implicit_resolvers[ch] = [
                    x
                    for x in StringBoolLoader.yaml_implicit_resolvers[ch]
                    if x[0] != "tag:yaml.org,2002:bool"
                ]

        try:
            loaded_data = yaml.load(yaml_str, Loader=StringBoolLoader)
            return cls._deserialize(loaded_data)
        except yaml.YAMLError as e:
            raise ValueError("Invalid YAML content") from e

    @classmethod
    def _deserialize(cls, data: dict[str, Any]) -> Workflow:
        """Deserialize a dictionary into a Workflow with proper type conversion."""
        # Convert document dict to Document dataclass
        document_data = data.get("document")
        if not isinstance(document_data, dict):
            raise ValueError("document field is required and must be a dict")
        document = Document(**document_data) if isinstance(document_data, dict) else document_data

        # Convert do list items
        do_list = data.get("do", [])
        converted_do: list[TaskItem] = []
        for item in do_list:
            if isinstance(item, dict):
                # Each item is a dict with one key (task name) and value (task config)
                for task_name, task_config in item.items():
                    if isinstance(task_config, dict):
                        # Determine task type and convert
                        converted_task = cls._convert_task(task_config)
                        # Create TaskItem from the name and task
                        task_item = TaskItem(name=task_name, task=converted_task)
                        converted_do.append(task_item)
                    else:
                        # If task_config is already a task object, wrap it
                        task_item = TaskItem(name=task_name, task=task_config)
                        converted_do.append(task_item)
            else:
                # Assume it's already a TaskItem
                if isinstance(item, TaskItem):
                    converted_do.append(item)

        # Convert other optional fields
        input_data = data.get("input")
        use_data = data.get("use")
        timeout_data = data.get("timeout")
        output_data = data.get("output")
        schedule_data = data.get("schedule")

        # Convert Schedule if present
        schedule: Schedule | None = None
        if schedule_data is not None:
            if isinstance(schedule_data, dict):
                schedule = Schedule(**schedule_data)
            elif isinstance(schedule_data, Schedule):
                schedule = schedule_data

        return cls(
            document=document,
            do=converted_do,
            input=input_data,
            use=use_data,
            timeout=timeout_data,
            output=output_data,
            schedule=schedule,
        )

    @classmethod
    def _map_yaml_keys_to_python(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Map YAML keys to Python-safe attribute names (handle reserved keywords).

        Python reserved keywords in YAML are mapped to their underscore-suffixed equivalents.
        For example: 'for' -> 'for_', 'with' -> 'with_', 'if' -> 'if_', etc.

        This mapping is based on Python's convention for avoiding reserved keywords.
        """
        # Python keywords that need underscore suffix
        # See: https://docs.python.org/3/reference/lexical_analysis.html#keywords
        python_keywords = {
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        }

        result = {}
        for key, value in data.items():
            # If key is a reserved word, append underscore
            python_key = f"{key}_" if key in python_keywords else key
            result[python_key] = value
        return result

    @classmethod
    def _convert_task(cls, task_config: dict[str, Any]) -> Any:
        """Convert a task configuration dict to the appropriate task type."""
        from .call_tasks import (
            CallA2ATask,
            CallAsyncApiTask,
            CallFunctionTask,
            CallGrpcTask,
            CallHttpTask,
            CallMcpTask,
            CallOpenApiTask,
        )
        from .tasks import (
            DoTask,
            EmitTask,
            ForkTask,
            ForTask,
            ListenTask,
            RaiseTask,
            RunTask,
            SetTask,
            SwitchTask,
            TryTask,
            WaitTask,
        )

        # Map YAML keys to Python attribute names
        mapped_config = cls._map_yaml_keys_to_python(task_config)

        # Determine task type based on which key is present
        if "call" in mapped_config:
            # Handle call tasks based on the call type
            from .call_tasks import (
                CallA2AArguments,
                CallAsyncApiArguments,
                CallGrpcArguments,
                CallHttpArguments,
                CallMcpArguments,
                CallOpenApiArguments,
            )

            call_type = mapped_config["call"]
            # Remove 'call' from config as it's set via field(init=False) for most call tasks
            config_without_call = {k: v for k, v in mapped_config.items() if k != "call"}

            # Convert with_ argument to appropriate type
            if "with_" in config_without_call and isinstance(config_without_call["with_"], dict):
                with_data = config_without_call["with_"]

                # Convert endpoint string to Endpoint if needed
                if "endpoint" in with_data and isinstance(with_data["endpoint"], str):
                    with_data = {**with_data, "endpoint": with_data["endpoint"]}

                if call_type == "http":
                    config_without_call["with_"] = CallHttpArguments(**with_data)
                elif call_type == "openapi":
                    # Convert document.endpoint if it's a string
                    if (
                        "document" in with_data
                        and isinstance(with_data["document"], dict)
                        and "endpoint" in with_data["document"]
                        and isinstance(with_data["document"]["endpoint"], str)
                    ):
                        from .base import ExternalResource

                        with_data["document"] = ExternalResource(**with_data["document"])
                    config_without_call["with_"] = CallOpenApiArguments(**with_data)
                elif call_type == "asyncapi":
                    # Similar conversion for AsyncAPI
                    if "document" in with_data and isinstance(with_data["document"], dict):
                        from .base import ExternalResource

                        with_data["document"] = ExternalResource(**with_data["document"])
                    config_without_call["with_"] = CallAsyncApiArguments(**with_data)
                elif call_type == "grpc":
                    config_without_call["with_"] = CallGrpcArguments(**with_data)
                elif call_type == "mcp":
                    config_without_call["with_"] = CallMcpArguments(**with_data)
                elif call_type == "a2a":
                    config_without_call["with_"] = CallA2AArguments(**with_data)

            if call_type == "http":
                return CallHttpTask(**config_without_call)
            elif call_type == "openapi":
                return CallOpenApiTask(**config_without_call)
            elif call_type == "asyncapi":
                return CallAsyncApiTask(**config_without_call)
            elif call_type == "grpc":
                return CallGrpcTask(**config_without_call)
            elif call_type == "mcp":
                return CallMcpTask(**config_without_call)
            elif call_type == "a2a":
                return CallA2ATask(**config_without_call)
            else:
                # Custom function call - needs 'call' parameter
                return CallFunctionTask(**mapped_config)
        elif "wait" in mapped_config:
            # Convert wait field if it's a dict (Duration)
            wait_value = mapped_config["wait"]
            if isinstance(wait_value, dict):
                wait_value = Duration(**wait_value)
            return WaitTask(**{**mapped_config, "wait": wait_value})
        elif "do" in mapped_config and "for_" not in mapped_config and "try_" not in mapped_config:
            return DoTask(**mapped_config)
        elif "fork" in mapped_config:
            return ForkTask(**mapped_config)
        elif "emit" in mapped_config:
            return EmitTask(**mapped_config)
        elif "for_" in mapped_config:
            return ForTask(**mapped_config)
        elif "listen" in mapped_config:
            return ListenTask(**mapped_config)
        elif "raise_" in mapped_config:
            return RaiseTask(**mapped_config)
        elif "run" in mapped_config:
            return RunTask(**mapped_config)
        elif "set" in mapped_config:
            return SetTask(**mapped_config)
        elif "switch" in mapped_config:
            return SwitchTask(**mapped_config)
        elif "try_" in mapped_config:
            return TryTask(**mapped_config)
        else:
            # Return as-is if we can't determine the type
            return task_config

    @classmethod
    def _convert_nested_objects(cls, data: dict[str, Any]) -> dict[str, Any | Duration]:
        """Recursively convert nested dicts to appropriate types."""
        result: dict[str, Any | Duration] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                # Try to convert to Duration if it looks like one
                if any(
                    k in value
                    for k in [
                        "days",
                        "hours",
                        "minutes",
                        "seconds",
                        "milliseconds",
                        "iso8601",
                        "expression",
                    ]
                ):
                    result[key] = Duration(**value)
                else:
                    result[key] = cls._convert_nested_objects(value)
            else:
                result[key] = value
        return result

    def to_yaml(self) -> str:
        """Serializes the Workflow to a YAML string."""
        import yaml

        serialized_data = self.serialize()
        try:
            return yaml.safe_dump(serialized_data, sort_keys=False)
        except yaml.YAMLError as e:
            raise ValueError("Error serializing to YAML") from e

    def render_graph(self, filename: str | None = None, engine: str = "graphviz") -> str:
        """Render the workflow as a graph to a file.

        :param filename: Output filename (optional).
        :param engine: Graph engine to use ("graphviz").
        :return: The graph as a DOT string.
        """
        from .draw import render_workflow_graph

        return render_workflow_graph(self, filename, engine)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another workflow."""
        if not isinstance(other, Workflow):
            return False
        return self.serialize() == other.serialize()

    def __repr__(self):
        """Return string representation of workflow."""
        return f"{self.__dict__!r}"

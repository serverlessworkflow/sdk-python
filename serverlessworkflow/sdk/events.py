"""Event-related classes for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from serverlessworkflow.sdk.base import RuntimeExpression, UriTemplate


@dataclass
class EventProperties:
    """Describes the properties of an event."""

    source: UriTemplate | RuntimeExpression
    type: str
    id: str | None = None
    time: str | RuntimeExpression | None = None
    subject: str | None = None
    datacontenttype: str | None = None
    dataschema: UriTemplate | RuntimeExpression | None = None
    data: Any | None = None
    # Allow additional CloudEvents extension attributes
    additional_properties: dict[str, Any] | None = None


@dataclass
class Correlation:
    """Correlation mapping for event filtering."""

    from_: str | None = field(
        default=None, metadata={"alias": "from"}
    )  # Runtime expression to extract correlation value
    expect: str | None = None  # Expected value or expression


@dataclass
class EventFilter:
    """Event filter for selective event processing."""

    with_: EventProperties | None = field(
        default=None, metadata={"alias": "with"}
    )  # The event properties to match
    correlate: dict[str, Correlation] | None = None


@dataclass
class EventConsumptionStrategyOne:
    """Consume one specific event."""

    one: EventFilter


@dataclass
class EventConsumptionStrategyAny:
    """Consume any of the specified events."""

    any: list[EventFilter]
    until: str | EventConsumptionStrategy | None = None


@dataclass
class EventConsumptionStrategyAll:
    """Consume all specified events."""

    all: list[EventFilter]


# Type alias for event consumption strategy
EventConsumptionStrategy = (
    EventConsumptionStrategyOne | EventConsumptionStrategyAny | EventConsumptionStrategyAll
)

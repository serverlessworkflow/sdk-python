"""Retry policy classes for Serverless Workflow SDK v1."""

from dataclasses import dataclass, field

from serverlessworkflow.sdk.base import Duration


@dataclass
class ConstantBackoff:
    """Constant backoff configuration."""

    constant: dict  # Empty object as marker


@dataclass
class ExponentialBackoff:
    """Exponential backoff configuration."""

    exponential: dict  # Empty object as marker


@dataclass
class LinearBackoff:
    """Linear backoff configuration."""

    linear: dict  # Empty object as marker


@dataclass
class RetryLimitAttempt:
    """Retry attempt limit configuration."""

    count: int | None = None
    duration: Duration | None = None


@dataclass
class RetryLimit:
    """Retry limits configuration."""

    attempt: RetryLimitAttempt | None = None
    duration: Duration | None = None


@dataclass
class RetryJitter:
    """Jitter configuration for retry delays."""

    from_: Duration = field(metadata={"alias": "from"})
    to: Duration


@dataclass
class RetryPolicy:
    """Defines a retry policy."""

    when: str | None = None  # Runtime expression
    exceptWhen: str | None = None  # Runtime expression
    delay: Duration | None = None
    backoff: ConstantBackoff | ExponentialBackoff | LinearBackoff | None = None
    limit: RetryLimit | None = None
    jitter: RetryJitter | None = None

"""Endpoint and related classes for Serverless Workflow SDK v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serverlessworkflow.sdk.authentication import ReferenceableAuthenticationPolicy

from serverlessworkflow.sdk.base import RuntimeExpression, UriTemplate


@dataclass
class Endpoint:
    """Represents an endpoint - can be a URI, expression, or configuration object."""

    uri: UriTemplate | RuntimeExpression | None = None
    authentication: ReferenceableAuthenticationPolicy | None = None

    def __post_init__(self):
        """Validate endpoint configuration."""
        # If only uri is set and authentication is None, it's a simple endpoint
        # If both are set, it's a full endpoint configuration
        if self.uri is None:
            raise ValueError("Endpoint must have a uri specified")


@dataclass
class Catalog:
    """The definition of a resource catalog."""

    endpoint: Endpoint

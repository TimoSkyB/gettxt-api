"""Python client for the gettxt document-to-text API."""

from .client import (
    DocumentResult,
    ExtractResponse,
    GettxtApiError,
    GettxtClient,
)

__all__ = [
    "DocumentResult",
    "ExtractResponse",
    "GettxtApiError",
    "GettxtClient",
]


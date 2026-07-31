"""Dependency-free client for https://gettxt.ai/api/extract/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "https://gettxt.ai/api/extract/"


class GettxtApiError(RuntimeError):
    """Raised when the API rejects a request or cannot be reached."""

    def __init__(self, message: str, *, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class DocumentResult:
    document_uri: str
    status: str
    extracted_text: str
    word_count: int
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    translated_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentResult":
        return cls(
            document_uri=str(data.get("documentUri", "")),
            status=str(data.get("status", "")),
            extracted_text=str(data.get("extractedText", "")),
            word_count=int(data.get("wordCount", 0)),
            short_summary=data.get("shortSummary"),
            long_summary=data.get("longSummary"),
            translated_text=data.get("translatedText"),
        )


@dataclass(frozen=True)
class ExtractResponse:
    credits_used: int
    credits_remaining: int
    total_word_count: int
    all_text: str
    documents: List[DocumentResult]
    timestamp: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractResponse":
        return cls(
            credits_used=int(data.get("creditsUsed", 0)),
            credits_remaining=int(data.get("creditsRemaining", 0)),
            total_word_count=int(data.get("totalWordCount", 0)),
            all_text=str(data.get("all_text", "")),
            documents=[
                DocumentResult.from_dict(item)
                for item in data.get("documents", [])
            ],
            timestamp=data.get("timestamp"),
        )


class GettxtClient:
    """Small synchronous client for gettxt extraction requests."""

    def __init__(
        self,
        api_key: str,
        *,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: float = 120.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout

    def extract(
        self,
        document_uris: Sequence[str],
        *,
        output_format: str = "text",
        summarize: bool = False,
        translate: Optional[str] = None,
        new_document_indicator: Optional[str] = None,
    ) -> ExtractResponse:
        """Extract text or Markdown from one to ten public document URLs."""

        uris = list(document_uris)
        if not 1 <= len(uris) <= 10:
            raise ValueError("document_uris must contain between 1 and 10 URLs")
        if any(not isinstance(uri, str) or not uri.strip() for uri in uris):
            raise ValueError("every document URI must be a non-empty string")
        if output_format not in {"text", "markdown"}:
            raise ValueError("output_format must be 'text' or 'markdown'")

        payload: Dict[str, Any] = {
            "documentUris": uris,
            "outputFormat": output_format,
            "summarize": summarize,
        }
        if translate is not None:
            payload["translate"] = translate
        if new_document_indicator is not None:
            payload["newDocumentIndicator"] = new_document_indicator

        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = _read_error(error)
            raise GettxtApiError(detail, status=error.code) from error
        except URLError as error:
            raise GettxtApiError(f"Could not reach gettxt: {error.reason}") from error

        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as error:
            raise GettxtApiError("gettxt returned invalid JSON") from error

        if not isinstance(decoded, dict):
            raise GettxtApiError("gettxt returned an unexpected response")
        return ExtractResponse.from_dict(decoded)


def _read_error(error: HTTPError) -> str:
    try:
        decoded = json.loads(error.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return f"gettxt request failed with HTTP {error.code}"
    if isinstance(decoded, dict):
        for key in ("error", "message", "detail"):
            if decoded.get(key):
                return str(decoded[key])
    return f"gettxt request failed with HTTP {error.code}"


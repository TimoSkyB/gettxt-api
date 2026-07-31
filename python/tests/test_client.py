import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from gettxt import GettxtApiError, GettxtClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class GettxtClientTests(unittest.TestCase):
    @patch("gettxt.client.urlopen")
    def test_extract_builds_request_and_parses_response(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse(
            {
                "creditsUsed": 1,
                "creditsRemaining": 9,
                "totalWordCount": 2,
                "all_text": "Hello world",
                "documents": [
                    {
                        "documentUri": "https://example.com/file.pdf",
                        "status": "succeeded",
                        "wordCount": 2,
                        "extractedText": "Hello world",
                    }
                ],
                "timestamp": "2026-07-31T10:00:00Z",
            }
        )

        result = GettxtClient("secret").extract(
            ["https://example.com/file.pdf"],
            output_format="markdown",
            translate="de",
        )

        request = mocked_urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.get_header("X-api-key"), "secret")
        self.assertEqual(body["outputFormat"], "markdown")
        self.assertEqual(body["translate"], "de")
        self.assertEqual(result.all_text, "Hello world")
        self.assertEqual(result.documents[0].status, "succeeded")

    @patch("gettxt.client.urlopen")
    def test_http_error_exposes_status_and_message(self, mocked_urlopen):
        mocked_urlopen.side_effect = HTTPError(
            "https://gettxt.ai/api/extract/",
            401,
            "Unauthorized",
            {},
            io.BytesIO(b'{"error":"Invalid API key"}'),
        )

        with self.assertRaises(GettxtApiError) as raised:
            GettxtClient("bad-key").extract(["https://example.com/file.pdf"])

        self.assertEqual(raised.exception.status, 401)
        self.assertEqual(str(raised.exception), "Invalid API key")

    def test_rejects_invalid_requests_before_network_call(self):
        client = GettxtClient("secret")
        with self.assertRaises(ValueError):
            client.extract([])
        with self.assertRaises(ValueError):
            client.extract(["https://example.com/file.pdf"], output_format="html")


if __name__ == "__main__":
    unittest.main()


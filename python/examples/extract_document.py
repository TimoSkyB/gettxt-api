"""Extract Markdown from a public document URL."""

import os
import sys

from gettxt import GettxtClient


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: extract_document.py <public-document-url>")

    api_key = os.environ.get("GETTXT_API_KEY")
    if not api_key:
        raise SystemExit("Set GETTXT_API_KEY before running this example")

    result = GettxtClient(api_key=api_key).extract(
        [sys.argv[1]],
        output_format="markdown",
    )
    print(result.all_text)


if __name__ == "__main__":
    main()


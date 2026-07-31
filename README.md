# gettxt API examples

Extract clean text or Markdown from PDFs, office documents, images, audio, and
video with one API call to [gettxt](https://gettxt.ai/).

This repository contains small, dependency-free reference clients for Python
and TypeScript. They cover text extraction, Markdown output, translation,
summarization, multiple documents, and structured API errors.

> These clients are intentionally lightweight examples. See the
> [gettxt API documentation](https://gettxt.ai/api-documentation) for the full
> request schema, supported formats, limits, and current behavior.

## Quick start

1. [Create a gettxt account](https://gettxt.ai/sign-up) and copy your API key.
2. Set the key in your shell:

   ```bash
   export GETTXT_API_KEY="your-api-key"
   ```

3. Run one of the examples below with a publicly accessible document URL.

The API accepts up to 10 document URLs in a request. URLs must be directly
accessible without an interactive login.

## cURL

```bash
curl --request POST 'https://gettxt.ai/api/extract/' \
  --header 'Content-Type: application/json' \
  --header "x-api-key: $GETTXT_API_KEY" \
  --data '{
    "documentUris": ["https://example.com/document.pdf"],
    "outputFormat": "markdown",
    "summarize": false
  }'
```

## Python

The Python client uses only the standard library and supports Python 3.9+.

```bash
cd python
python3 -m pip install -e .
python3 examples/extract_document.py https://example.com/document.pdf
```

```python
from gettxt import GettxtClient

client = GettxtClient(api_key="your-api-key")
result = client.extract(
    ["https://example.com/document.pdf"],
    output_format="markdown",
)
print(result.all_text)
```

## TypeScript

The TypeScript client uses the built-in `fetch` available in Node.js 18+ and
modern browsers.

```bash
cd typescript
npm install
npm run build
GETTXT_API_KEY=your-api-key \
  node dist/examples/extract-document.js https://example.com/document.pdf
```

```typescript
import { GettxtClient } from "./src/index.js";

const client = new GettxtClient({ apiKey: "your-api-key" });
const result = await client.extract({
  documentUris: ["https://example.com/document.pdf"],
  outputFormat: "markdown",
});
console.log(result.all_text);
```

## Options

Both clients expose the documented extraction options:

| Option | Purpose |
| --- | --- |
| `documentUris` | One to ten directly accessible document URLs |
| `outputFormat` | `text` or `markdown` |
| `summarize` | Request short and long summaries |
| `translate` | Translate output to a language code such as `de` or `es` |
| `newDocumentIndicator` | Separator used in the combined `all_text` field |

## Development

All tests are offline and replace the network transport with deterministic
fixtures. No API key or credits are consumed.

```bash
cd python && python3 -m unittest discover -s tests -v
cd ../typescript && npm install && npm test
```

## Security

Never commit API keys. Load them from an environment variable or a secret
manager, and rotate any key that is accidentally exposed.

## License

[MIT](LICENSE)


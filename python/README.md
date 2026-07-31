# gettxt Python client

Dependency-free Python client for the
[gettxt document-to-text API](https://gettxt.ai/api-documentation).

```python
from gettxt import GettxtClient

result = GettxtClient(api_key="your-api-key").extract(
    ["https://example.com/document.pdf"],
    output_format="markdown",
)
print(result.all_text)
```


import { GettxtClient } from "../src/index.js";

const apiKey = process.env.GETTXT_API_KEY;
const documentUrl = process.argv[2];

if (!apiKey) {
  throw new Error("Set GETTXT_API_KEY before running this example");
}
if (!documentUrl) {
  throw new Error("Usage: extract-document <public-document-url>");
}

const client = new GettxtClient({ apiKey });
const result = await client.extract({
  documentUris: [documentUrl],
  outputFormat: "markdown",
});

console.log(result.all_text);


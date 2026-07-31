import assert from "node:assert/strict";
import test from "node:test";

import { GettxtApiError, GettxtClient } from "../dist/src/index.js";

test("extract sends the documented request and returns parsed output", async () => {
  let capturedUrl;
  let capturedOptions;
  const fakeFetch = async (url, options) => {
    capturedUrl = url;
    capturedOptions = options;
    return new Response(
      JSON.stringify({
        creditsUsed: 1,
        creditsRemaining: 9,
        totalWordCount: 2,
        all_text: "Hello world",
        documents: [],
      }),
      { status: 200, headers: { "content-type": "application/json" } },
    );
  };

  const client = new GettxtClient({ apiKey: "secret", fetch: fakeFetch });
  const result = await client.extract({
    documentUris: ["https://example.com/file.pdf"],
    outputFormat: "markdown",
  });

  assert.equal(capturedUrl, "https://gettxt.ai/api/extract/");
  assert.equal(capturedOptions.headers["x-api-key"], "secret");
  assert.equal(JSON.parse(capturedOptions.body).outputFormat, "markdown");
  assert.equal(result.all_text, "Hello world");
});

test("extract exposes API status and error details", async () => {
  const fakeFetch = async () => new Response(
    JSON.stringify({ error: "Invalid API key" }),
    { status: 401, headers: { "content-type": "application/json" } },
  );
  const client = new GettxtClient({ apiKey: "bad-key", fetch: fakeFetch });

  await assert.rejects(
    () => client.extract({ documentUris: ["https://example.com/file.pdf"] }),
    (error) => error instanceof GettxtApiError
      && error.status === 401
      && error.message === "Invalid API key",
  );
});

test("extract rejects invalid input before calling fetch", async () => {
  const client = new GettxtClient({
    apiKey: "secret",
    fetch: async () => { throw new Error("fetch should not be called"); },
  });

  await assert.rejects(
    () => client.extract({ documentUris: [] }),
    /between 1 and 10 URLs/,
  );
});


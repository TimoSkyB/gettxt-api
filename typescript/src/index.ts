const DEFAULT_ENDPOINT = "https://gettxt.ai/api/extract/";

export type OutputFormat = "text" | "markdown";

export interface ExtractRequest {
  documentUris: string[];
  outputFormat?: OutputFormat;
  summarize?: boolean;
  translate?: string;
  newDocumentIndicator?: string;
}

export interface DocumentResult {
  documentUri: string;
  status: string;
  extractedText: string;
  wordCount: number;
  shortSummary?: string;
  longSummary?: string;
  translatedText?: string;
  createdDateTime?: string;
  lastUpdatedDateTime?: string;
}

export interface ExtractResponse {
  creditsUsed: number;
  creditsRemaining: number;
  totalWordCount: number;
  all_text: string;
  documents: DocumentResult[];
  timestamp?: string;
}

export interface GettxtClientOptions {
  apiKey: string;
  endpoint?: string;
  fetch?: typeof globalThis.fetch;
}

export class GettxtApiError extends Error {
  override name = "GettxtApiError";

  constructor(
    message: string,
    readonly status?: number,
    readonly response?: unknown,
  ) {
    super(message);
  }
}

export class GettxtClient {
  private readonly apiKey: string;
  private readonly endpoint: string;
  private readonly fetchImplementation: typeof globalThis.fetch;

  constructor(options: GettxtClientOptions) {
    if (!options.apiKey.trim()) {
      throw new TypeError("apiKey must not be empty");
    }
    this.apiKey = options.apiKey;
    this.endpoint = options.endpoint ?? DEFAULT_ENDPOINT;
    this.fetchImplementation = options.fetch ?? globalThis.fetch;
  }

  async extract(request: ExtractRequest): Promise<ExtractResponse> {
    validateRequest(request);

    let response: Response;
    try {
      response = await this.fetchImplementation(this.endpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": this.apiKey,
        },
        body: JSON.stringify({
          ...request,
          outputFormat: request.outputFormat ?? "text",
          summarize: request.summarize ?? false,
        }),
      });
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      throw new GettxtApiError(`Could not reach gettxt: ${detail}`);
    }

    const payload: unknown = await parseJson(response);
    if (!response.ok) {
      throw new GettxtApiError(
        readErrorMessage(payload) ?? `gettxt request failed with HTTP ${response.status}`,
        response.status,
        payload,
      );
    }
    if (!isExtractResponse(payload)) {
      throw new GettxtApiError("gettxt returned an unexpected response", response.status, payload);
    }
    return payload;
  }
}

function validateRequest(request: ExtractRequest): void {
  if (!Array.isArray(request.documentUris) || request.documentUris.length < 1 || request.documentUris.length > 10) {
    throw new TypeError("documentUris must contain between 1 and 10 URLs");
  }
  if (request.documentUris.some((uri) => typeof uri !== "string" || uri.trim() === "")) {
    throw new TypeError("every document URI must be a non-empty string");
  }
  if (request.outputFormat !== undefined && !["text", "markdown"].includes(request.outputFormat)) {
    throw new TypeError("outputFormat must be 'text' or 'markdown'");
  }
}

async function parseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    throw new GettxtApiError("gettxt returned invalid JSON", response.status);
  }
}

function readErrorMessage(payload: unknown): string | undefined {
  if (typeof payload !== "object" || payload === null) return undefined;
  const value = payload as Record<string, unknown>;
  for (const key of ["error", "message", "detail"]) {
    if (typeof value[key] === "string" && value[key]) return value[key];
  }
  return undefined;
}

function isExtractResponse(payload: unknown): payload is ExtractResponse {
  if (typeof payload !== "object" || payload === null) return false;
  const value = payload as Record<string, unknown>;
  return typeof value.all_text === "string" && Array.isArray(value.documents);
}


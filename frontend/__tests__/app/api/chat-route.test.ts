import { POST } from "@/app/api/chat/route";

class FakeHeaders {
  private readonly values = new Map<string, string>();

  constructor(init?: Record<string, string>) {
    Object.entries(init ?? {}).forEach(([key, value]) => {
      this.values.set(key.toLowerCase(), value);
    });
  }

  get(name: string) {
    return this.values.get(name.toLowerCase()) ?? null;
  }
}

class FakeResponse {
  readonly status: number;
  readonly headers: FakeHeaders;
  readonly ok: boolean;
  readonly body: string;

  constructor(body?: string, init?: { status?: number; headers?: Record<string, string> }) {
    this.status = init?.status ?? 200;
    this.headers = new FakeHeaders(init?.headers);
    this.ok = this.status >= 200 && this.status < 300;
    this.body = body ?? "";
  }

  async text() {
    return this.body;
  }

  async json() {
    return JSON.parse(this.body);
  }
}

describe("POST /api/chat", () => {
  const originalFetch = global.fetch;
  const originalResponse = global.Response;

  beforeEach(() => {
    global.fetch = jest.fn();
    global.Response = FakeResponse as unknown as typeof Response;
  });

  afterAll(() => {
    global.fetch = originalFetch;
    global.Response = originalResponse;
  });

  it("forwards the request body to the backend and streams back a successful response", async () => {
    const request = {
      text: jest.fn().mockResolvedValue('{"message":"hello"}'),
    };

    jest.mocked(global.fetch).mockResolvedValue(
      new FakeResponse("streamed body", {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      }) as never,
    );

    const response = await POST(request as never);

    expect(request.text).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: '{"message":"hello"}',
    });
    expect(response.headers.get("Content-Type")).toBe("text/plain");
    expect(response.headers.get("Cache-Control")).toBe("no-cache");
    expect(await response.text()).toBe("streamed body");
  });

  it("returns 502 when the backend cannot be reached", async () => {
    jest.mocked(global.fetch).mockRejectedValue(new Error("network"));

    const response = await POST({
      text: async () => '{"message":"hello"}',
    } as never);

    expect(response.status).toBe(502);
    expect(response.headers.get("Content-Type")).toBe("application/json");
    expect(await response.json()).toEqual({ error: "Could not reach backend" });
  });

  it("returns the backend status when the backend responds with an error", async () => {
    jest.mocked(global.fetch).mockResolvedValue(
      new FakeResponse("upstream failed", {
        status: 503,
        headers: { "Content-Type": "text/plain" },
      }) as never,
    );

    const response = await POST({
      text: async () => '{"message":"hello"}',
    } as never);

    expect(response.status).toBe(503);
    expect(response.headers.get("Content-Type")).toBe("application/json");
    expect(await response.json()).toEqual({ error: "Backend error" });
  });

  it("defaults to text/event-stream when the backend omits a content type", async () => {
    jest.mocked(global.fetch).mockResolvedValue(
      new FakeResponse("event data", {
        status: 200,
      }) as never,
    );

    const response = await POST({
      text: async () => '{"message":"hello"}',
    } as never);

    expect(response.headers.get("Content-Type")).toBe("text/event-stream");
    expect(await response.text()).toBe("event data");
  });
});

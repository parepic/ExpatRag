import { ApiError, logout } from "@/lib/api/auth";

describe("logout", () => {
  afterEach(() => {
    jest.restoreAllMocks();
    delete (global as Partial<typeof globalThis>).fetch;
  });

  it("posts to the backend logout endpoint with credentials", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true }) as typeof fetch;

    await logout();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/logout",
      {
        method: "POST",
        credentials: "include",
      },
    );
  });

  it("throws an ApiError when the backend rejects the request", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Session store unavailable" }),
    }) as typeof fetch;

    await expect(logout()).rejects.toThrow(
      new ApiError(500, "Session store unavailable"),
    );
  });
});

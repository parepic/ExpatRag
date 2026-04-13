import { renderHook, waitFor } from "@testing-library/react";

import { useAuth } from "@/hooks/useAuth";

describe("useAuth", () => {
  afterEach(() => {
    jest.restoreAllMocks();
    delete (global as Partial<typeof globalThis>).fetch;
  });

  it("returns the user after a successful auth check", async () => {
    global.fetch = jest.fn().mockResolvedValue(
      {
        ok: true,
        json: async () => ({ id: "user-1", username: "alice" }),
      },
    ) as typeof fetch;

    const { result } = renderHook(() => useAuth());

    expect(result.current).toEqual({ user: null, isLoading: true });

    await waitFor(() => {
      expect(result.current).toEqual({
        user: { id: "user-1", username: "alice" },
        isLoading: false,
      });
    });

    expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/auth/me", {
      credentials: "include",
    });
  });

  it("returns no user when the backend responds with 401", async () => {
    global.fetch = jest.fn().mockResolvedValue(
      {
        ok: false,
      },
    ) as typeof fetch;

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current).toEqual({ user: null, isLoading: false });
    });
  });

  it("returns no user when the request fails", async () => {
    global.fetch = jest
      .fn()
      .mockRejectedValue(new Error("Could not reach backend")) as typeof fetch;

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current).toEqual({ user: null, isLoading: false });
    });
  });
});

describe("profile storage fallback", () => {
  const originalLocalStorage = window.localStorage;

  afterEach(() => {
    jest.resetModules();
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: originalLocalStorage,
    });
  });

  it("falls back to in-memory storage when localStorage throws", () => {
    const failingStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(() => {
        throw new Error("blocked");
      }),
      removeItem: jest.fn(() => {
        throw new Error("blocked");
      }),
    };

    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: failingStorage,
    });

    jest.isolateModules(() => {
      const profile = require("@/lib/profile") as typeof import("@/lib/profile");

      profile.setField("nationality", "Non-EU national");

      expect(profile.getField("nationality")).toBe("Non-EU national");
      expect(profile.isStorageAvailable()).toBe(false);
    });
  });

  it("keeps serving subsequent reads and writes from memory after storage becomes unavailable", () => {
    const failingStorage = {
      getItem: jest.fn(() => null),
      setItem: jest.fn(() => {
        throw new Error("blocked");
      }),
      removeItem: jest.fn(() => {
        throw new Error("blocked");
      }),
    };

    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: failingStorage,
    });

    jest.isolateModules(() => {
      const profile = require("@/lib/profile") as typeof import("@/lib/profile");

      profile.setField("nationality", "Dutch citizen");
      profile.setField("purpose_of_stay", "Study");

      expect(profile.getField("nationality")).toBe("Dutch citizen");
      expect(profile.getField("purpose_of_stay")).toBe("Study");
      expect(profile.isStorageAvailable()).toBe(false);
    });
  });
});

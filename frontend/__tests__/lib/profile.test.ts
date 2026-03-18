import {
  getField,
  setField,
  isComplete,
  getMissingFields,
  REQUIRED_FIELDS,
} from "@/lib/profile";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, "localStorage", { value: localStorageMock });

beforeEach(() => localStorageMock.clear());

describe("getField", () => {
  it("returns null when key is not set", () => {
    expect(getField("nationality")).toBeNull();
  });
  it("returns the stored value", () => {
    localStorageMock.setItem("nationality", "EU/EEA citizen");
    expect(getField("nationality")).toBe("EU/EEA citizen");
  });
});

describe("setField", () => {
  it("writes the value to localStorage", () => {
    setField("nationality", "Non-EU national");
    expect(localStorageMock.getItem("nationality")).toBe("Non-EU national");
  });
});

describe("isComplete", () => {
  it("returns false when no fields are set", () => {
    expect(isComplete()).toBe(false);
  });

  it("returns false when only some fields are set", () => {
    setField("nationality", "EU/EEA citizen");
    expect(isComplete()).toBe(false);
  });

  it("returns false when a required field is only whitespace", () => {
    REQUIRED_FIELDS.forEach((key) => setField(key, "some-value"));
    setField("nationality", "   ");

    expect(isComplete()).toBe(false);
  });

  it("returns true when all required fields are set", () => {
    REQUIRED_FIELDS.forEach((key) => setField(key, "some-value"));
    expect(isComplete()).toBe(true);
  });
});

describe("getMissingFields", () => {
  it("returns all required fields when nothing is set", () => {
    expect(getMissingFields()).toEqual(REQUIRED_FIELDS);
  });

  it("returns only the unset fields", () => {
    setField("nationality", "EU/EEA citizen");
    setField("purpose_of_stay", "Study");
    const missing = getMissingFields();
    expect(missing).not.toContain("nationality");
    expect(missing).not.toContain("purpose_of_stay");
    expect(missing.length).toBe(REQUIRED_FIELDS.length - 2);
  });

  it("treats whitespace-only values as missing", () => {
    setField("nationality", " ");

    expect(getMissingFields()).toContain("nationality");
  });
});

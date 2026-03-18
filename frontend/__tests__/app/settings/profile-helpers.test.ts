jest.mock("@/lib/profile", () => ({
  getField: jest.fn(() => null),
  setField: jest.fn(),
}));
jest.mock("@/components/onboarding/ChipSelect", () => ({ ChipSelect: () => null }));
jest.mock("@/components/onboarding/YesNoToggle", () => ({ YesNoToggle: () => null }));
jest.mock("@/components/onboarding/LanguageCombobox", () => ({ LanguageCombobox: () => null }));
jest.mock("@/components/ui/button", () => ({ Button: () => null }));

import { displayValue, toYesNo, fromYesNo } from "@/app/(app)/settings/profile/page";

describe("displayValue", () => {
  it("undefined → —", () => {
    expect(displayValue("nationality", undefined)).toBe("—");
  });

  it("empty array → —", () => {
    expect(displayValue("languages", [])).toBe("—");
  });

  it("non-empty array → joined string", () => {
    expect(displayValue("languages", ["Dutch", "English"])).toBe("Dutch, English");
  });

  it("age_bracket under_30 → Under 30", () => {
    expect(displayValue("age_bracket", "under_30")).toBe("Under 30");
  });

  it("age_bracket 30_or_older → 30 or older", () => {
    expect(displayValue("age_bracket", "30_or_older")).toBe("30 or older");
  });

  it("nationality passthrough", () => {
    expect(displayValue("nationality", "Dutch")).toBe("Dutch");
  });
});

describe("toYesNo", () => {
  it("age_bracket under_30 → yes", () => {
    expect(toYesNo("age_bracket", "under_30")).toBe("yes");
  });

  it("age_bracket 30_or_older → no", () => {
    expect(toYesNo("age_bracket", "30_or_older")).toBe("no");
  });

  it("age_bracket legacy yes → yes", () => {
    expect(toYesNo("age_bracket", "yes")).toBe("yes");
  });

  it("has_fiscal_partner yes → yes", () => {
    expect(toYesNo("has_fiscal_partner", "yes")).toBe("yes");
  });

  it("has_fiscal_partner no → no", () => {
    expect(toYesNo("has_fiscal_partner", "no")).toBe("no");
  });

  it("has_fiscal_partner maybe → null", () => {
    expect(toYesNo("has_fiscal_partner", "maybe")).toBeNull();
  });

  it("array value → null", () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect(toYesNo("languages", ["array"] as any)).toBeNull();
  });
});

describe("fromYesNo", () => {
  it("age_bracket yes → under_30", () => {
    expect(fromYesNo("age_bracket", "yes")).toBe("under_30");
  });

  it("age_bracket no → 30_or_older", () => {
    expect(fromYesNo("age_bracket", "no")).toBe("30_or_older");
  });

  it("has_fiscal_partner yes → yes (passthrough)", () => {
    expect(fromYesNo("has_fiscal_partner", "yes")).toBe("yes");
  });
});

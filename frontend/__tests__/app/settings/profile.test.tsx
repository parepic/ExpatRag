import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { getField, setField } from "@/lib/profile";

jest.mock("@/lib/profile", () => ({
  getField: jest.fn(() => null),
  setField: jest.fn(),
}));
jest.mock("@/components/onboarding/ChipSelect", () => ({
  ChipSelect: ({
    options,
    value,
    onChange,
  }: {
    options: readonly string[];
    value: string | null;
    onChange: (value: string) => void;
  }) => (
    <div data-testid={`chip-select-${value ?? "empty"}`}>
      {options.slice(0, 2).map((option) => (
        <button key={option} type="button" onClick={() => onChange(option)}>
          {option}
        </button>
      ))}
    </div>
  ),
}));
jest.mock("@/components/onboarding/YesNoToggle", () => ({
  YesNoToggle: ({
    value,
    onChange,
  }: {
    value: "yes" | "no" | null;
    onChange: (value: "yes" | "no") => void;
  }) => (
    <div data-testid={`yesno-${value ?? "empty"}`}>
      <button type="button" onClick={() => onChange("yes")}>
        Yes
      </button>
      <button type="button" onClick={() => onChange("no")}>
        No
      </button>
    </div>
  ),
}));
jest.mock("@/components/onboarding/LanguageCombobox", () => ({
  LanguageCombobox: ({
    value,
    onChange,
  }: {
    value: string[];
    onChange: (value: string[]) => void;
  }) => (
    <div data-testid={`languages-${value.join(",") || "empty"}`}>
      <button type="button" onClick={() => onChange(["English", "Dutch"])}>
        Set languages
      </button>
    </div>
  ),
}));

// Imported after mocks so loadValues() uses the mocked getField
import ProfilePage from "@/app/(app)/settings/profile/page";

const mockGetField = jest.mocked(getField);
const mockSetField = jest.mocked(setField);

function setStoredFields(values: Record<string, string | null>) {
  mockGetField.mockImplementation((key) => values[key] ?? null);
}

beforeEach(() => {
  mockGetField.mockReset();
  mockSetField.mockReset();
  mockGetField.mockReturnValue(null);
});

describe("ProfilePage field labels", () => {
  it("renders all 10 field labels", () => {
    render(<ProfilePage />);
    expect(screen.getByText("Nationality / citizenship")).toBeInTheDocument();
    expect(screen.getByText("Purpose of stay")).toBeInTheDocument();
    expect(screen.getByText("Employment situation")).toBeInTheDocument();
    expect(screen.getByText("Registration / BSN status")).toBeInTheDocument();
    expect(screen.getByText("Fiscal partner?")).toBeInTheDocument();
    expect(screen.getByText("Housing situation")).toBeInTheDocument();
    expect(screen.getByText("Gross annual salary")).toBeInTheDocument();
    expect(screen.getByText("Under 30?")).toBeInTheDocument();
    expect(screen.getByText("Prior NL residency")).toBeInTheDocument();
    expect(screen.getByText("Languages spoken")).toBeInTheDocument();
  });
});

describe("ProfilePage view/edit mode", () => {
  it("view mode: shows Edit button, no Cancel or Save", () => {
    render(<ProfilePage />);
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancel" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Save" })).toBeNull();
  });

  it("clicking Edit shows Cancel and Save, hides Edit", async () => {
    render(<ProfilePage />);
    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Edit" })).toBeNull();
  });

  it("clicking Cancel returns to view mode", async () => {
    render(<ProfilePage />);
    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancel" })).toBeNull();
  });
});

describe("ProfilePage field display", () => {
  it("unset fields display —", () => {
    render(<ProfilePage />);
    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBeGreaterThan(0);
  });

  it("mocked fields display their values", () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mockGetField.mockImplementation((key: any) => {
      if (key === "nationality") return "Dutch";
      return null;
    });
    render(<ProfilePage />);
    expect(screen.getByText("Dutch")).toBeInTheDocument();
  });

  it("renders stored language arrays as a joined string", () => {
    setStoredFields({
      languages: JSON.stringify(["English", "Dutch"]),
    });

    render(<ProfilePage />);

    expect(screen.getByText("English, Dutch")).toBeInTheDocument();
  });
});

describe("ProfilePage save flow", () => {
  it("saves edited values, serializes languages, and returns to view mode", async () => {
    const user = userEvent.setup();

    render(<ProfilePage />);

    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByRole("button", { name: "Non-EU national" }));
    await user.click(screen.getAllByRole("button", { name: "Yes" })[0]);
    await user.click(screen.getByRole("button", { name: "Set languages" }));
    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(mockSetField).toHaveBeenCalledWith("nationality", "Non-EU national");
    expect(mockSetField).toHaveBeenCalledWith("has_fiscal_partner", "yes");
    expect(mockSetField).toHaveBeenCalledWith("languages", JSON.stringify(["English", "Dutch"]));
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
    expect(screen.getByText("Non-EU national")).toBeInTheDocument();
    expect(screen.getByText("yes")).toBeInTheDocument();
    expect(screen.getByText("English, Dutch")).toBeInTheDocument();
  });

  it("maps age_bracket values through the yes/no editor and saves under_30", async () => {
    const user = userEvent.setup();
    setStoredFields({ age_bracket: "30_or_older" });

    render(<ProfilePage />);

    await user.click(screen.getByRole("button", { name: "Edit" }));
    expect(screen.getByTestId("yesno-no")).toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Yes" })[1]);
    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(mockSetField).toHaveBeenCalledWith("age_bracket", "under_30");
    expect(screen.getByText("Under 30")).toBeInTheDocument();
  });

  it("cancel restores the saved draft instead of unsaved edits", async () => {
    const user = userEvent.setup();
    setStoredFields({ nationality: "Dutch citizen" });

    render(<ProfilePage />);

    expect(screen.getByText("Dutch citizen")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByRole("button", { name: "Non-EU national" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.getByText("Dutch citizen")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Edit" }));
    expect(screen.getByTestId("chip-select-Dutch citizen")).toBeInTheDocument();
  });
});

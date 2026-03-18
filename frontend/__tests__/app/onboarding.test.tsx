import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";
import { getField, getMissingFields, setField } from "@/lib/profile";
import OnboardingPage from "@/app/onboarding/page";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/hooks/useProfileGuard", () => ({ useProfileGuard: jest.fn() }));
jest.mock("@/lib/profile", () => ({
  getField: jest.fn(),
  getMissingFields: jest.fn(),
  setField: jest.fn(),
  REQUIRED_FIELDS: [
    "nationality",
    "purpose_of_stay",
    "employment_situation",
    "registration_status",
    "has_fiscal_partner",
    "housing_situation",
    "salary_band",
    "age_bracket",
    "prior_nl_residency",
  ],
}));
jest.mock("framer-motion", () => ({
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
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
    <div data-testid="chip-select" data-value={value ?? ""}>
      {options.map((option) => (
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
    <div data-testid="yesno-toggle" data-value={value ?? ""}>
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
    <div data-testid="language-combobox" data-value={value.join(",")}>
      <button type="button" onClick={() => onChange(["English"])}>
        Set languages
      </button>
    </div>
  ),
}));
jest.mock("@/components/onboarding/QuestionCard", () => ({
  QuestionCard: ({
    children,
    direction,
  }: {
    children: React.ReactNode;
    direction?: "forward" | "back";
  }) => (
    <div data-testid="question-card" data-direction={direction}>
      {children}
    </div>
  ),
}));
jest.mock("@/components/onboarding/ProgressDots", () => ({
  ProgressDots: ({ total, current }: { total: number; current: number }) => (
    <div data-testid="progress-dots">
      {current}/{total}
    </div>
  ),
}));

const mockUseRouter = jest.mocked(useRouter);
const mockGetField = jest.mocked(getField);
const mockGetMissingFields = jest.mocked(getMissingFields);
const mockSetField = jest.mocked(setField);
const mockPush = jest.fn();

function setStoredValues(values: Record<string, string | null>, missing: string[]) {
  mockGetMissingFields.mockReturnValue(missing as never);
  mockGetField.mockImplementation((key) => values[key] ?? null);
}

async function goToAgeBracketQuestion() {
  const user = userEvent.setup();
  render(<OnboardingPage />);

  await user.click(screen.getByRole("button", { name: "EU/EEA citizen" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Highly Skilled Migrant" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Employed full-time" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "BRP registered at a municipality" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Yes" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Renting privately" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Under €20,000" }));
  await user.click(screen.getByRole("button", { name: "Next" }));

  return user;
}

async function goToFinalQuestion() {
  const user = await goToAgeBracketQuestion();

  await user.click(screen.getByRole("button", { name: "Yes" }));
  await user.click(screen.getByRole("button", { name: "Next" }));
  await user.click(screen.getByRole("button", { name: "Never lived in the Netherlands" }));
  await user.click(screen.getByRole("button", { name: "Next" }));

  return user;
}

beforeEach(() => {
  mockUseRouter.mockReturnValue({ push: mockPush } as never);
  mockPush.mockClear();
  mockSetField.mockClear();
  setStoredValues({}, ["nationality"]);
});

describe("OnboardingPage", () => {
  it("starts at the first missing required question", async () => {
    setStoredValues({ nationality: "EU/EEA citizen" }, ["purpose_of_stay"]);

    render(<OnboardingPage />);

    expect(
      await screen.findByText("What is your main reason for coming to the Netherlands?")
    ).toBeInTheDocument();
  });

  it("falls back to the first question when the missing key does not match a question", async () => {
    setStoredValues({}, ["not_a_real_field"]);

    render(<OnboardingPage />);

    expect(
      await screen.findByText("What is your nationality / citizenship status?")
    ).toBeInTheDocument();
  });

  it("hydrates saved string and JSON answers into page state", async () => {
    setStoredValues(
      {
        nationality: "EU/EEA citizen",
        languages: JSON.stringify(["English", "Dutch"]),
      },
      ["nationality"],
    );

    render(<OnboardingPage />);

    await waitFor(() => {
      expect(screen.getByTestId("progress-dots")).toHaveTextContent("2/10");
    });
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("keeps Back disabled on the first step and disables forward actions without an answer", async () => {
    render(<OnboardingPage />);

    expect(await screen.findByRole("button", { name: "← Back" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Forward →" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("enables navigation after answering and moves forward and back between steps", async () => {
    const user = userEvent.setup();
    render(<OnboardingPage />);

    await user.click(screen.getByRole("button", { name: "EU/EEA citizen" }));

    expect(screen.getByRole("button", { name: "Forward →" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Forward →" }));
    expect(
      await screen.findByText("What is your main reason for coming to the Netherlands?")
    ).toBeInTheDocument();
    expect(screen.getByTestId("question-card")).toHaveAttribute("data-direction", "forward");

    await user.click(screen.getByRole("button", { name: "← Back" }));
    expect(
      await screen.findByText("What is your nationality / citizenship status?")
    ).toBeInTheDocument();
    expect(screen.getByTestId("question-card")).toHaveAttribute("data-direction", "back");
  });

  it("stores a chip answer as a plain string and advances to the next question", async () => {
    const user = userEvent.setup();
    render(<OnboardingPage />);

    await user.click(screen.getByRole("button", { name: "EU/EEA citizen" }));
    await user.click(screen.getByRole("button", { name: "Next" }));

    expect(mockSetField).toHaveBeenCalledWith("nationality", "EU/EEA citizen");
    expect(
      await screen.findByText("What is your main reason for coming to the Netherlands?")
    ).toBeInTheDocument();
  });

  it("stores age bracket answers using the under_30/30_or_older format", async () => {
    const user = await goToAgeBracketQuestion();

    expect(await screen.findByText("Are you under 30 years old?")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Yes" }));
    await user.click(screen.getByRole("button", { name: "Next" }));

    expect(mockSetField).toHaveBeenCalledWith("age_bracket", "under_30");
  });

  it("finishes on the languages step and routes to chat from the completion CTA", async () => {
    const user = await goToFinalQuestion();

    expect(await screen.findByText("What languages do you speak?")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Set languages" }));
    await user.click(screen.getByRole("button", { name: "Finish" }));

    expect(await screen.findByText("You're all set!")).toBeInTheDocument();
    expect(mockSetField).toHaveBeenCalledWith("languages", JSON.stringify(["English"]));

    await user.click(screen.getByRole("button", { name: "Start chatting with Patty" }));
    expect(mockPush).toHaveBeenCalledWith("/chat");
  });
});

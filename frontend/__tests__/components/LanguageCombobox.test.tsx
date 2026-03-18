import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LanguageCombobox } from "@/components/onboarding/LanguageCombobox";

jest.mock("@/components/ui/popover", () => ({
  Popover: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PopoverTrigger: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PopoverContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));
jest.mock("@/components/ui/command", () => ({
  Command: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandEmpty: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandGroup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandInput: (props: React.InputHTMLAttributes<HTMLInputElement>) => <input {...props} />,
  CommandItem: ({
    children,
    onSelect,
  }: {
    children: React.ReactNode;
    onSelect?: () => void;
  }) => (
    <button type="button" onClick={() => onSelect?.()}>
      {children}
    </button>
  ),
}));

describe("LanguageCombobox", () => {
  it('shows "Search languages…" when there are no selected languages', () => {
    render(<LanguageCombobox value={[]} onChange={() => {}} />);

    expect(screen.getByRole("button", { name: "Search languages…" })).toBeInTheDocument();
  });

  it('shows "Add another language…" and selected badges when languages exist', () => {
    render(<LanguageCombobox value={["English"]} onChange={() => {}} />);

    expect(screen.getByRole("button", { name: "Add another language…" })).toBeInTheDocument();
    expect(screen.getByText("English")).toBeInTheDocument();
  });

  it("adds a language when a command item is selected", async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    render(<LanguageCombobox value={[]} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: "English" }));

    expect(onChange).toHaveBeenCalledWith(["English"]);
  });

  it("removes a language when a selected item is clicked again", async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    render(<LanguageCombobox value={["English"]} onChange={onChange} />);
    await user.click(screen.getAllByRole("button", { name: "✓ English" })[0]);

    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("removes a language from the badge dismiss button", async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    render(<LanguageCombobox value={["English", "Dutch"]} onChange={onChange} />);
    await user.click(screen.getAllByRole("button", { name: "×" })[0]);

    expect(onChange).toHaveBeenCalledWith(["Dutch"]);
  });
});

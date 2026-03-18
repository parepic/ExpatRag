import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";

describe("YesNoToggle", () => {
  it("marks the selected option", () => {
    render(<YesNoToggle value="yes" onChange={() => {}} />);

    expect(screen.getByRole("button", { name: "Yes" })).toHaveAttribute("data-selected", "true");
    expect(screen.getByRole("button", { name: "No" })).not.toHaveAttribute("data-selected");
  });

  it("calls onChange with yes and no", async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    render(<YesNoToggle value={null} onChange={onChange} />);

    await user.click(screen.getByRole("button", { name: "Yes" }));
    await user.click(screen.getByRole("button", { name: "No" }));

    expect(onChange).toHaveBeenNthCalledWith(1, "yes");
    expect(onChange).toHaveBeenNthCalledWith(2, "no");
  });
});

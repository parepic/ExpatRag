import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChipSelect } from "@/components/onboarding/ChipSelect";

const options = ["Option A", "Option B", "Option C"];

describe("ChipSelect", () => {
  it("renders all options", () => {
    render(<ChipSelect options={options} value={null} onChange={() => {}} />);
    options.forEach((opt) => expect(screen.getByText(opt)).toBeInTheDocument());
  });

  it("marks the selected option", () => {
    render(<ChipSelect options={options} value="Option B" onChange={() => {}} />);
    expect(screen.getByText("Option B").closest("[data-selected]")).toBeTruthy();
  });

  it("calls onChange when an option is clicked", async () => {
    const onChange = jest.fn();
    render(<ChipSelect options={options} value={null} onChange={onChange} />);
    await userEvent.click(screen.getByText("Option A"));
    expect(onChange).toHaveBeenCalledWith("Option A");
  });
});

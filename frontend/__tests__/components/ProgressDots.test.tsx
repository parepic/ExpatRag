import { render, screen } from "@testing-library/react";
import { ProgressDots } from "@/components/onboarding/ProgressDots";

describe("ProgressDots", () => {
  it("renders the correct number of dots", () => {
    render(<ProgressDots total={5} current={2} />);
    const dots = screen.getAllByRole("presentation");
    expect(dots).toHaveLength(5);
  });

  it("marks dots up to current as filled", () => {
    render(<ProgressDots total={5} current={2} />);
    const dots = screen.getAllByRole("presentation");
    expect(dots[0]).toHaveAttribute("data-filled", "true");
    expect(dots[1]).toHaveAttribute("data-filled", "true");
    expect(dots[2]).toHaveAttribute("data-filled", "false");
  });
});

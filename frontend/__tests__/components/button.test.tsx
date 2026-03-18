import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders a <button> element by default", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
  });

  it("base classes include rounded-full", () => {
    render(<Button>x</Button>);
    expect(screen.getByRole("button")).toHaveClass("rounded-full");
  });

  it("default variant includes bg-primary", () => {
    render(<Button>x</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-primary");
  });

  it("outline variant includes border-input", () => {
    render(<Button variant="outline">x</Button>);
    expect(screen.getByRole("button")).toHaveClass("border-input");
  });

  it("ghost variant includes bg-transparent", () => {
    render(<Button variant="ghost">x</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-transparent");
  });

  it("size sm includes h-9", () => {
    render(<Button size="sm">x</Button>);
    expect(screen.getByRole("button")).toHaveClass("h-9");
  });

  it("merges custom className", () => {
    render(<Button className="my-custom">x</Button>);
    expect(screen.getByRole("button")).toHaveClass("my-custom");
  });

  it("onClick fires when clicked", async () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>x</Button>);
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("disabled button has disabled attribute", () => {
    render(<Button disabled>x</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("asChild renders child element instead of button", () => {
    render(
      <Button asChild>
        <a href="/home">link</a>
      </Button>
    );
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.getByRole("link", { name: "link" })).toBeInTheDocument();
  });
});

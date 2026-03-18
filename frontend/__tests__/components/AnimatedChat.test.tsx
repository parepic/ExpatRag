import { render, act } from "@testing-library/react";
import { AnimatedChat } from "@/components/welcome/AnimatedChat";

beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

describe("AnimatedChat", () => {
  it("renders two grid columns", () => {
    const { container } = render(<AnimatedChat />);
    const grid = container.querySelector(".grid-cols-2");
    expect(grid).toBeInTheDocument();
    expect(grid!.children).toHaveLength(2);
  });

  it("column 1 contains DigiD-related text", () => {
    const { container } = render(<AnimatedChat />);
    const col1 = container.querySelector(".grid-cols-2")!.children[0];
    expect(col1.textContent).toContain("DigiD");
  });

  it("column 2 contains 30% ruling text", () => {
    const { container } = render(<AnimatedChat />);
    const col2 = container.querySelector(".grid-cols-2")!.children[1];
    expect(col2.textContent).toContain("30% ruling");
  });

  it("user messages have self-end class", () => {
    const { container } = render(<AnimatedChat />);
    const userMsgs = container.querySelectorAll(".self-end");
    expect(userMsgs.length).toBeGreaterThan(0);
  });

  it("patty messages have self-start class", () => {
    const { container } = render(<AnimatedChat />);
    const pattyMsgs = container.querySelectorAll(".self-start");
    expect(pattyMsgs.length).toBeGreaterThan(0);
  });

  it("initially all messages are hidden (opacity-0)", () => {
    const { container } = render(<AnimatedChat />);
    const hidden = container.querySelectorAll(".opacity-0");
    // 6 messages per column = 12 total
    expect(hidden.length).toBe(12);
  });

  it("after advancing fake timers, messages become visible", () => {
    const { container } = render(<AnimatedChat />);

    act(() => {
      // Column 1 starts at 800ms, Column 2 at 2400ms
      jest.advanceTimersByTime(900);
    });

    const visible = container.querySelectorAll(".opacity-100");
    expect(visible.length).toBeGreaterThan(0);
  });

  it("resets and restarts the first column after the full message cycle", () => {
    const { container } = render(<AnimatedChat />);

    act(() => {
      jest.advanceTimersByTime(14801);
    });

    const visible = container.querySelectorAll(".opacity-100");
    expect(visible.length).toBeGreaterThan(0);
  });

  it("does not throw when timers continue after unmount", () => {
    const { unmount } = render(<AnimatedChat />);

    unmount();

    expect(() => {
      act(() => {
        jest.runOnlyPendingTimers();
      });
    }).not.toThrow();
  });
});

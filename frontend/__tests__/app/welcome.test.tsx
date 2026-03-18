import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";
import { isComplete } from "@/lib/profile";
import WelcomePage from "@/app/page";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/profile", () => ({ isComplete: jest.fn() }));
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}));
jest.mock("@/components/welcome/AnimatedChat", () => ({
  AnimatedChat: () => <div data-testid="animated-chat" />,
}));

const mockUseRouter = jest.mocked(useRouter);
const mockIsComplete = jest.mocked(isComplete);
const mockPush = jest.fn();

beforeEach(() => {
  mockUseRouter.mockReturnValue({ push: mockPush } as never);
  mockPush.mockClear();
  mockIsComplete.mockReset();
});

describe("WelcomePage", () => {
  it("redirects complete profiles to /chat", async () => {
    mockIsComplete.mockReturnValue(true);

    const { container } = render(<WelcomePage />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/chat");
    });
    expect(container).toBeEmptyDOMElement();
  });

  it("renders the welcome content when the profile is incomplete", async () => {
    mockIsComplete.mockReturnValue(false);

    render(<WelcomePage />);

    expect(
      await screen.findByText("Your all-in-one expat moving assistant")
    ).toBeInTheDocument();
    expect(screen.getByTestId("animated-chat")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Get Started" })).toBeInTheDocument();
  });

  it("routes to onboarding when Get Started is clicked", async () => {
    const user = userEvent.setup();
    mockIsComplete.mockReturnValue(false);

    render(<WelcomePage />);

    await user.click(await screen.findByRole("button", { name: "Get Started" }));

    expect(mockPush).toHaveBeenCalledWith("/onboarding");
  });
});

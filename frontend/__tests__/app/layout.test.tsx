import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { usePathname } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { createChat } from "@/lib/chat-store";
import { useChatSessions } from "@/hooks/useChatSessions";
import AppLayout from "@/app/(app)/layout";

jest.mock("next/navigation", () => ({ usePathname: jest.fn() }));
jest.mock("@/context/AppContext", () => ({ useAppContext: jest.fn() }));
jest.mock("@/lib/chat-store", () => ({ createChat: jest.fn() }));
jest.mock("@/hooks/useChatSessions", () => ({ useChatSessions: jest.fn() }));
jest.mock("next/link", () => ({
  __esModule: true,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  default: ({ children, href, className }: any) => (
    <a href={href} className={className}>{children}</a>
  ),
}));

const mockUsePathname = jest.mocked(usePathname);
const mockUseAppContext = jest.mocked(useAppContext);
const mockCreateChat = jest.mocked(createChat);
const mockUseChatSessions = jest.mocked(useChatSessions);

const baseCtx = {
  activeChatId: null as string | null,
  isChatStoreReady: true,
  setActiveChatId: jest.fn(),
};

beforeEach(() => {
  mockUsePathname.mockReturnValue("/chat");
  baseCtx.setActiveChatId.mockClear();
  mockCreateChat.mockReset();
  mockCreateChat.mockReturnValue({
    id: "new-chat-id",
    title: "New chat",
    createdAt: 1,
    updatedAt: 1,
  });
  mockUseChatSessions.mockReturnValue([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  mockUseAppContext.mockReturnValue(baseCtx as any);
});

function renderLayout() {
  return render(<AppLayout><div>content</div></AppLayout>);
}

describe("header breadcrumb", () => {
  it('shows "Chat with Patty" on /chat', () => {
    mockUsePathname.mockReturnValue("/chat");
    renderLayout();
    expect(screen.getByText("Chat with Patty")).toBeInTheDocument();
  });

  it('shows "Settings" and "Profile" on /settings/profile', () => {
    mockUsePathname.mockReturnValue("/settings/profile");
    const { container } = renderLayout();
    const header = container.querySelector("header")!;
    expect(within(header).getByText("Settings")).toBeInTheDocument();
    expect(within(header).getByText("Profile")).toBeInTheDocument();
  });
});

describe("sidebar nav — chat route", () => {
  it('shows only the "Chats" section heading', () => {
    mockUsePathname.mockReturnValue("/chat");
    renderLayout();
    expect(screen.getByText("Chats")).toBeInTheDocument();
    expect(screen.queryByText("Tasks")).toBeNull();
  });
});

describe("sidebar nav — settings route", () => {
  it('shows "Back to Patty" link and hides chats', () => {
    mockUsePathname.mockReturnValue("/settings");
    renderLayout();
    expect(screen.getByText(/Back to Patty/)).toBeInTheDocument();
    expect(screen.queryByText("Chats")).toBeNull();
  });

  it('"Profile" link has active styling on /settings/profile', () => {
    mockUsePathname.mockReturnValue("/settings/profile");
    renderLayout();
    const profileLink = screen.getAllByRole("link").find(
      (el) => el.textContent?.trim() === "Profile",
    );
    expect(profileLink).toBeTruthy();
    expect(profileLink).toHaveClass("bg-sidebar-primary");
  });
});

describe("chats section", () => {
  it('shows "No previous chats" when chats is empty', () => {
    renderLayout();
    expect(screen.getByText(/No previous chats/)).toBeInTheDocument();
  });

  it("renders chat title buttons when chats exist", () => {
    mockUseChatSessions.mockReturnValue([
      { id: "c1", title: "DigiD help", createdAt: 1, updatedAt: 1 },
      { id: "c2", title: "Tax filing", createdAt: 2, updatedAt: 2 },
    ]);
    renderLayout();
    expect(screen.getByText("DigiD help")).toBeInTheDocument();
    expect(screen.getByText("Tax filing")).toBeInTheDocument();
  });

  it("active chat button has highlighted styling", () => {
    mockUseAppContext.mockReturnValue({
      ...baseCtx,
      activeChatId: "c1",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);
    mockUseChatSessions.mockReturnValue([
      { id: "c1", title: "DigiD help", createdAt: 1, updatedAt: 1 },
    ]);
    renderLayout();
    const btn = screen.getByText("DigiD help").closest("button");
    expect(btn).toHaveClass("bg-sidebar-primary");
  });

  it('clicking "+ New" creates a new chat and activates it', async () => {
    const user = userEvent.setup();

    renderLayout();
    await user.click(screen.getByRole("button", { name: "+ New" }));

    expect(mockCreateChat).toHaveBeenCalledTimes(1);
    expect(baseCtx.setActiveChatId).toHaveBeenCalledWith("new-chat-id");
  });

  it("clicking a chat button sets it active", async () => {
    const user = userEvent.setup();
    mockUseChatSessions.mockReturnValue([
      { id: "c1", title: "DigiD help", createdAt: 1, updatedAt: 1 },
    ]);

    renderLayout();
    await user.click(screen.getByRole("button", { name: "DigiD help" }));

    expect(baseCtx.setActiveChatId).toHaveBeenCalledWith("c1");
  });
});

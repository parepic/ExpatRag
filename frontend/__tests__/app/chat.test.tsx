import { render, screen } from "@testing-library/react";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { DefaultChatTransport } from "ai";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import { useAppContext } from "@/context/AppContext";
import { createChat, getChat, getMessages, saveMessages } from "@/lib/chat-store";
import ChatPage from "@/app/(app)/chat/page";

jest.mock("@assistant-ui/react", () => ({
  AssistantRuntimeProvider: jest.fn(
    ({
      children,
    }: {
      children: React.ReactNode;
      runtime: unknown;
    }) => <div data-testid="assistant-runtime-provider">{children}</div>,
  ),
}));
jest.mock("@assistant-ui/react-ai-sdk", () => ({
  useChatRuntime: jest.fn(),
}));
jest.mock("ai", () => ({
  DefaultChatTransport: jest.fn(function MockTransport(config: { api: string; body: () => object }) {
    return { kind: "transport", config };
  }),
}));
jest.mock("@/hooks/useProfileGuard", () => ({ useProfileGuard: jest.fn() }));
jest.mock("@/context/AppContext", () => ({ useAppContext: jest.fn() }));
jest.mock("@/lib/chat-store", () => ({
  createChat: jest.fn(),
  getChat: jest.fn(),
  getMessages: jest.fn(),
  saveMessages: jest.fn(),
}));
jest.mock("@/components/assistant-ui/thread", () => ({
  Thread: () => <div data-testid="thread" />,
}));

const mockUseChatRuntime = jest.mocked(useChatRuntime);
const mockDefaultChatTransport = jest.mocked(DefaultChatTransport);
const mockUseProfileGuard = jest.mocked(useProfileGuard);
const mockUseAppContext = jest.mocked(useAppContext);
const mockAssistantRuntimeProvider = jest.mocked(AssistantRuntimeProvider);
const mockCreateChat = jest.mocked(createChat);
const mockGetChat = jest.mocked(getChat);
const mockGetMessages = jest.mocked(getMessages);
const mockSaveMessages = jest.mocked(saveMessages);

const runtime = { kind: "runtime" };
const setActiveChatId = jest.fn();

beforeEach(() => {
  setActiveChatId.mockClear();
  mockDefaultChatTransport.mockClear();
  mockUseProfileGuard.mockClear();
  mockAssistantRuntimeProvider.mockClear();
  mockCreateChat.mockReset();
  mockGetChat.mockReset();
  mockGetMessages.mockReset();
  mockSaveMessages.mockReset();

  mockUseChatRuntime.mockReturnValue(runtime as never);
  mockUseAppContext.mockReturnValue({
    activeChatId: "chat-1",
    isChatStoreReady: true,
    setActiveChatId,
  } as never);
  mockGetChat.mockReturnValue({
    id: "chat-1",
    title: "New chat",
    createdAt: 1,
    updatedAt: 1,
  });
  mockGetMessages.mockReturnValue([]);
  mockCreateChat.mockReturnValue({
    id: "new-chat-id",
    title: "New chat",
    createdAt: 1,
    updatedAt: 1,
  });
});

describe("ChatPage", () => {
  it("guards the route, creates the runtime transport, and renders the thread", () => {
    render(<ChatPage />);

    expect(mockUseProfileGuard).toHaveBeenCalledWith("chat");
    expect(mockDefaultChatTransport).toHaveBeenCalledWith({
      api: "/api/chat",
      body: expect.any(Function),
    });
    expect(mockUseChatRuntime).toHaveBeenCalledWith({
      id: "chat-1",
      messages: [],
      onFinish: expect.any(Function),
      transport: expect.objectContaining({
        kind: "transport",
        config: {
          api: "/api/chat",
          body: expect.any(Function),
        },
      }),
    });
    expect(mockAssistantRuntimeProvider).toHaveBeenCalledWith(
      expect.objectContaining({ runtime }),
      undefined,
    );
    expect(screen.getByTestId("thread")).toBeInTheDocument();
  });

  it("creates and activates a chat when there is no active chat", () => {
    mockUseAppContext.mockReturnValue({
      activeChatId: null,
      isChatStoreReady: true,
      setActiveChatId,
    } as never);

    render(<ChatPage />);

    expect(mockCreateChat).toHaveBeenCalledTimes(1);
    expect(setActiveChatId).toHaveBeenCalledWith("new-chat-id");
    expect(screen.queryByTestId("thread")).toBeNull();
  });

  it("creates and activates a replacement chat when the active chat no longer exists", () => {
    mockGetChat.mockReturnValue(null);

    render(<ChatPage />);

    expect(mockCreateChat).toHaveBeenCalledTimes(1);
    expect(setActiveChatId).toHaveBeenCalledWith("new-chat-id");
    expect(screen.queryByTestId("thread")).toBeNull();
  });

  it("waits for the chat store hydration before creating or rendering a chat", () => {
    mockUseAppContext.mockReturnValue({
      activeChatId: null,
      isChatStoreReady: false,
      setActiveChatId,
    } as never);

    render(<ChatPage />);

    expect(mockCreateChat).not.toHaveBeenCalled();
    expect(screen.queryByTestId("thread")).toBeNull();
  });

  it("persists the finished message list for the active chat", () => {
    render(<ChatPage />);

    const options = mockUseChatRuntime.mock.calls[0]?.[0];
    options?.onFinish?.({
      message: { id: "m2" },
      messages: [{ id: "m1" }, { id: "m2" }],
      isAbort: false,
      isDisconnect: false,
      isError: false,
      finishReason: "stop",
    } as never);

    expect(mockSaveMessages).toHaveBeenCalledWith("chat-1", [{ id: "m1" }, { id: "m2" }]);
  });
});

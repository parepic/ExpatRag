import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppProvider, useAppContext } from "@/context/AppContext";
import * as chatStore from "@/lib/chat-store";

function TestConsumer() {
  const { activeChatId, isChatStoreReady, setActiveChatId } = useAppContext();

  return (
    <div>
      <div data-testid="active-chat">{activeChatId ?? "none"}</div>
      <div data-testid="store-ready">{isChatStoreReady ? "ready" : "loading"}</div>
      <button onClick={() => setActiveChatId("chat-1")}>Set Active</button>
      <button onClick={() => setActiveChatId(null)}>Clear Active</button>
    </div>
  );
}

const renderWithProvider = () =>
  render(
    <AppProvider>
      <TestConsumer />
    </AppProvider>,
  );

beforeEach(() => {
  chatStore.clearChatStore();
});

describe("AppContext", () => {
  it("starts with no active chat", () => {
    renderWithProvider();
    expect(screen.getByTestId("store-ready")).toHaveTextContent("ready");
    expect(screen.getByTestId("active-chat")).toHaveTextContent("none");
  });

  it("updates the active chat id", async () => {
    renderWithProvider();

    await userEvent.click(screen.getByText("Set Active"));

    expect(screen.getByTestId("active-chat")).toHaveTextContent("chat-1");
  });

  it("clears the active chat id", async () => {
    renderWithProvider();

    await userEvent.click(screen.getByText("Set Active"));
    await userEvent.click(screen.getByText("Clear Active"));

    expect(screen.getByTestId("active-chat")).toHaveTextContent("none");
  });
});

describe("useAppContext", () => {
  function OutsideProviderConsumer() {
    useAppContext();
    return null;
  }

  it("throws when used outside AppProvider", () => {
    const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    expect(() => render(<OutsideProviderConsumer />)).toThrow(
      "useAppContext must be used within AppProvider",
    );

    consoleErrorSpy.mockRestore();
  });
});

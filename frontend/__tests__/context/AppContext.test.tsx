import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppProvider, useAppContext } from "@/context/AppContext";

function TestConsumer() {
  const { todos, addTodo, toggleTodo, chats, addChat, activeChat, setActiveChat } = useAppContext();
  return (
    <div>
      <div data-testid="todos">{todos.length}</div>
      <div data-testid="chats">{chats.length}</div>
      <div data-testid="active-chat">{activeChat ?? "none"}</div>
      <button onClick={() => addTodo("Register at municipality")}>Add Todo</button>
      <button onClick={() => toggleTodo(todos[0]?.id ?? "")}>Toggle Todo</button>
      <button onClick={() => addChat("My first chat")}>Add Chat</button>
      <button onClick={() => setActiveChat("chat-1")}>Set Active</button>
    </div>
  );
}

const renderWithProvider = () =>
  render(<AppProvider><TestConsumer /></AppProvider>);

describe("AppContext todos", () => {
  it("starts with no todos", () => {
    renderWithProvider();
    expect(screen.getByTestId("todos")).toHaveTextContent("0");
  });
  it("adds a todo", async () => {
    renderWithProvider();
    await userEvent.click(screen.getByText("Add Todo"));
    expect(screen.getByTestId("todos")).toHaveTextContent("1");
  });
});

describe("AppContext chats", () => {
  it("starts with no chats", () => {
    renderWithProvider();
    expect(screen.getByTestId("chats")).toHaveTextContent("0");
  });
  it("adds a chat session", async () => {
    renderWithProvider();
    await userEvent.click(screen.getByText("Add Chat"));
    expect(screen.getByTestId("chats")).toHaveTextContent("1");
  });
});

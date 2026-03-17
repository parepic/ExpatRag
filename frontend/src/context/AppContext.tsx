"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: number;
}

interface AppContextValue {
  todos: Todo[];
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
  chats: ChatSession[];
  addChat: (title: string) => string;
  activeChat: string | null;
  setActiveChat: (id: string | null) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);

  const addTodo = useCallback((text: string) => {
    const id = crypto.randomUUID();
    setTodos((prev) => [...prev, { id, text, completed: false }]);
  }, []);

  const toggleTodo = useCallback((id: string) => {
    setTodos((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }, []);

  const addChat = useCallback((title: string): string => {
    const id = crypto.randomUUID();
    setChats((prev) => [{ id, title, createdAt: Date.now() }, ...prev]);
    setActiveChat(id);
    return id;
  }, []);

  return (
    <AppContext.Provider value={{ todos, addTodo, toggleTodo, chats, addChat, activeChat, setActiveChat }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}

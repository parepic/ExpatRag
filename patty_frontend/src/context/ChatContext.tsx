"use client";

import {
  createContext,
  useContext,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

import type { Chat } from "@/lib/types/chat";

type ChatContextValue = {
  activeChatId: string | null;
  chats: Chat[];
  setActiveChatId: Dispatch<SetStateAction<string | null>>;
  setChats: Dispatch<SetStateAction<Chat[]>>;
};

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);

  return (
    <ChatContext.Provider
      value={{ activeChatId, chats, setActiveChatId, setChats }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext(): ChatContextValue {
  const value = useContext(ChatContext);

  if (!value) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }

  return value;
}

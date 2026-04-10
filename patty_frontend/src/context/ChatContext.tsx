"use client";

import {
  createContext,
  useContext,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

type ChatContextValue = {
  activeChatId: string | null;
  setActiveChatId: Dispatch<SetStateAction<string | null>>;
};

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  return (
    <ChatContext.Provider value={{ activeChatId, setActiveChatId }}>
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

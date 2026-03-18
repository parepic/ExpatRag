"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { getStoredActiveChatId, setStoredActiveChatId } from "@/lib/chat-store";

interface AppContextValue {
  activeChatId: string | null;
  isChatStoreReady: boolean;
  setActiveChatId: (id: string | null) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [activeChatIdState, setActiveChatIdState] = useState<string | null>(null);
  const [isChatStoreReady, setIsChatStoreReady] = useState(false);

  useEffect(() => {
    setActiveChatIdState(getStoredActiveChatId());
    setIsChatStoreReady(true);
  }, []);

  const value = useMemo<AppContextValue>(
    () => ({
      activeChatId: activeChatIdState,
      isChatStoreReady,
      setActiveChatId: (id) => {
        setStoredActiveChatId(id);
        setActiveChatIdState(id);
      },
    }),
    [activeChatIdState, isChatStoreReady],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}

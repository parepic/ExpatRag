"use client";

import {
  createContext,
  useContext,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

type AppContextValue = {
  activeChatId: string | null;
  setActiveChatId: Dispatch<SetStateAction<string | null>>;
};

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  return (
    <AppContext.Provider value={{ activeChatId, setActiveChatId }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppContextValue {
  const value = useContext(AppContext);

  if (!value) {
    throw new Error("useAppContext must be used within an AppProvider");
  }

  return value;
}

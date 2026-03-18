import type { UIMessage } from "ai";

export interface ChatSessionSummary {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
}

interface ChatStore {
  activeChatId: string | null;
  sessions: ChatSessionSummary[];
  messagesByChatId: Record<string, UIMessage[]>;
}

const CHAT_STORE_KEY = "expatrag-chat-store";
const DEFAULT_CHAT_TITLE = "New chat";
const TITLE_MAX_LENGTH = 40;

let inMemoryStore: ChatStore = {
  activeChatId: null,
  sessions: [],
  messagesByChatId: {},
};
let useInMemory = false;
let cachedStore: ChatStore | null = null;
const listeners = new Set<() => void>();
const EMPTY_MESSAGES: UIMessage[] = [];

function getStorage(): Pick<Storage, "getItem" | "setItem" | "removeItem"> | null {
  if (useInMemory || typeof window === "undefined") return null;

  try {
    sessionStorage.setItem("__chat_store_test__", "1");
    sessionStorage.removeItem("__chat_store_test__");
    return sessionStorage;
  } catch {
    useInMemory = true;
    return null;
  }
}

function cloneStore(store: ChatStore): ChatStore {
  return {
    activeChatId: store.activeChatId,
    sessions: [...store.sessions],
    messagesByChatId: Object.fromEntries(
      Object.entries(store.messagesByChatId).map(([chatId, messages]) => [
        chatId,
        [...messages],
      ]),
    ),
  };
}

function getEmptyStore(): ChatStore {
  return {
    activeChatId: null,
    sessions: [],
    messagesByChatId: {},
  };
}

function loadStore(): ChatStore {
  const storage = getStorage();
  if (!storage) return cloneStore(inMemoryStore);

  const raw = storage.getItem(CHAT_STORE_KEY);
  if (!raw) return getEmptyStore();

  try {
    const parsed = JSON.parse(raw) as Partial<ChatStore>;
    return {
      activeChatId: typeof parsed.activeChatId === "string" ? parsed.activeChatId : null,
      sessions: Array.isArray(parsed.sessions) ? parsed.sessions : [],
      messagesByChatId: parsed.messagesByChatId ?? {},
    };
  } catch {
    return getEmptyStore();
  }
}

function readStore(): ChatStore {
  if (cachedStore) return cachedStore;

  cachedStore = loadStore();
  return cachedStore;
}

function writeStore(nextStore: ChatStore): void {
  const normalizedStore = cloneStore(nextStore);
  cachedStore = normalizedStore;
  const storage = getStorage();

  if (!storage) {
    inMemoryStore = normalizedStore;
  } else {
    storage.setItem(CHAT_STORE_KEY, JSON.stringify(normalizedStore));
  }

  listeners.forEach((listener) => listener());
}

function updateStore(updater: (store: ChatStore) => ChatStore): ChatStore {
  const nextStore = updater(readStore());
  writeStore(nextStore);
  return nextStore;
}

function getFirstUserMessageText(messages: UIMessage[]): string {
  const firstUserMessage = messages.find((message) => message.role === "user");
  if (!firstUserMessage) return "";

  return firstUserMessage.parts
    .filter((part): part is Extract<UIMessage["parts"][number], { type: "text" }> => part.type === "text")
    .map((part) => part.text)
    .join("")
    .trim();
}

function buildChatTitle(messages: UIMessage[]): string {
  const text = getFirstUserMessageText(messages);
  if (!text) return DEFAULT_CHAT_TITLE;
  return text.slice(0, TITLE_MAX_LENGTH);
}

export function subscribeToChatStore(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function listChats(): ChatSessionSummary[] {
  return readStore().sessions;
}

export function getChat(chatId: string): ChatSessionSummary | null {
  return readStore().sessions.find((session) => session.id === chatId) ?? null;
}

export function createChat(): ChatSessionSummary {
  const now = Date.now();
  const session: ChatSessionSummary = {
    id: crypto.randomUUID(),
    title: DEFAULT_CHAT_TITLE,
    createdAt: now,
    updatedAt: now,
  };

  updateStore((store) => ({
    ...store,
    sessions: [session, ...store.sessions],
    messagesByChatId: {
      ...store.messagesByChatId,
      [session.id]: [],
    },
  }));

  return session;
}

export function getMessages(chatId: string): UIMessage[] {
  return readStore().messagesByChatId[chatId] ?? EMPTY_MESSAGES;
}

export function saveMessages(chatId: string, messages: UIMessage[]): void {
  updateStore((store) => {
    const sessions = store.sessions.map((session) => {
      if (session.id !== chatId) return session;

      const title =
        session.title === DEFAULT_CHAT_TITLE ? buildChatTitle(messages) : session.title;

      return {
        ...session,
        title,
        updatedAt: Date.now(),
      };
    });

    const currentSession = sessions.find((session) => session.id === chatId);

    return {
      ...store,
      sessions: currentSession
        ? [
            currentSession,
            ...sessions.filter((session) => session.id !== chatId),
          ]
        : sessions,
      messagesByChatId: {
        ...store.messagesByChatId,
        [chatId]: messages,
      },
    };
  });
}

export function getStoredActiveChatId(): string | null {
  const store = readStore();
  if (store.activeChatId && store.sessions.some((session) => session.id === store.activeChatId)) {
    return store.activeChatId;
  }
  return store.sessions[0]?.id ?? null;
}

export function setStoredActiveChatId(chatId: string | null): void {
  updateStore((store) => ({
    ...store,
    activeChatId: chatId,
  }));
}

export function clearChatStore(): void {
  cachedStore = getEmptyStore();
  const storage = getStorage();
  if (!storage) {
    inMemoryStore = cachedStore;
  } else {
    storage.removeItem(CHAT_STORE_KEY);
  }
  listeners.forEach((listener) => listener());
}

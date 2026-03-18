"use client";

import { useSyncExternalStore } from "react";
import type { ChatSessionSummary } from "@/lib/chat-store";
import { listChats, subscribeToChatStore } from "@/lib/chat-store";

const EMPTY_CHATS: ChatSessionSummary[] = [];

export function useChatSessions() {
  return useSyncExternalStore(
    subscribeToChatStore,
    listChats,
    () => EMPTY_CHATS,
  );
}

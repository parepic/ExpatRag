"use client";

import { useEffect, useRef, useState } from "react";

import { ChatWelcome } from "@/components/chat/ChatWelcome";
import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import { useChatContext } from "@/context/ChatContext";
import { addMessage, createChat, fetchChat } from "@/lib/api/chats";
import type { Message } from "@/lib/types/chat";

export default function ChatPage() {
  const { activeChatId, setActiveChatId } = useChatContext();
  const skipNextLoadChatIdRef = useRef<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!activeChatId) {
      setMessages([]);
      setError("");
      setIsLoading(false);
      return;
    }

    if (skipNextLoadChatIdRef.current === activeChatId) {
      skipNextLoadChatIdRef.current = null;
      return;
    }

    const chatId = activeChatId;
    let cancelled = false;

    async function loadChat() {
      setError("");
      setIsLoading(true);

      try {
        const thread = await fetchChat(chatId);

        if (!cancelled) {
          setMessages(thread.messages);
        }
      } catch (caughtError) {
        if (!cancelled) {
          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to load chat",
          );
          setMessages([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadChat();

    return () => {
      cancelled = true;
    };
  }, [activeChatId]);

  async function handleSend(draft: string) {
    if (!draft.trim() || isLoading) {
      return;
    }

    setError("");

    const optimisticMessage: Message = {
      role: "user",
      content: draft,
      citations: null,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [...current, optimisticMessage]);
    setIsLoading(true);

    try {
      if (!activeChatId) {
        const reply = await createChat(draft);

        skipNextLoadChatIdRef.current = reply.chat_id;
        setActiveChatId(reply.chat_id);
        setMessages((current) => [...current, reply.assistant_message]);
      } else {
        const reply = await addMessage(activeChatId, draft);

        setMessages((current) => [...current, reply.assistant_message]);
      }
    } catch (caughtError) {
      setMessages((current) =>
        current.filter(
          (message) =>
            !(
              message.role === optimisticMessage.role &&
              message.content === optimisticMessage.content &&
              message.created_at === optimisticMessage.created_at
            ),
        ),
      );

      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Failed to send message",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex h-full min-h-0 flex-col overflow-hidden px-6 py-6">
      <div className="mx-auto flex w-full max-w-4xl flex-1 min-h-0 flex-col gap-4">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <p className="text-sm text-muted-foreground">
            Active chat: {activeChatId ?? "new conversation"}
          </p>
          {error ? (
            <p className="mt-2 text-sm text-destructive">{error}</p>
          ) : null}
        </div>

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-3xl border border-border bg-card shadow-sm">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            emptyState={
              <ChatWelcome
                onSuggestionClick={(text) => {
                  void handleSend(text);
                }}
              />
            }
          />
        </div>

        <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
          <Composer onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </main>
  );
}

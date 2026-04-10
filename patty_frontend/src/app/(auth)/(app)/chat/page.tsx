"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useChatContext } from "@/context/ChatContext";
import { addMessage, createChat, fetchChat } from "@/lib/api/chats";
import type { Message } from "@/lib/types/chat";

export default function ChatPage() {
  const { activeChatId, setActiveChatId } = useChatContext();
  const skipNextLoadChatIdRef = useRef<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
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

  async function handleSend() {
    const trimmedDraft = draft.trim();

    if (!trimmedDraft || isLoading) {
      return;
    }

    setError("");
    setDraft("");

    const optimisticMessage: Message = {
      role: "user",
      content: trimmedDraft,
      citations: null,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [...current, optimisticMessage]);
    setIsLoading(true);

    try {
      if (!activeChatId) {
        const reply = await createChat(trimmedDraft);

        skipNextLoadChatIdRef.current = reply.chat_id;
        setActiveChatId(reply.chat_id);
        setMessages((current) => [...current, reply.assistant_message]);
      } else {
        const reply = await addMessage(activeChatId, trimmedDraft);

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
    <main className="flex h-full min-h-0 flex-col px-6 py-6">
      <div className="mx-auto flex w-full max-w-4xl flex-1 min-h-0 flex-col gap-4">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <p className="text-sm text-muted-foreground">
            Active chat: {activeChatId ?? "new conversation"}
          </p>
          {error ? (
            <p className="mt-2 text-sm text-destructive">{error}</p>
          ) : null}
        </div>

        <div className="min-h-0 flex-1 rounded-3xl border border-border bg-card p-6 shadow-sm">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-sm text-muted-foreground">
                Start a new conversation with Patty
              </p>
            </div>
          ) : (
            <ul className="space-y-4">
              {messages.map((message) => (
                <li
                  key={`${message.role}-${message.created_at}-${message.content}`}
                  className="space-y-1"
                >
                  <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
                    {message.role}
                  </p>
                  <p className="text-sm leading-6 text-foreground">
                    {message.content}
                  </p>
                </li>
              ))}
              {isLoading ? (
                <li className="text-sm text-muted-foreground">
                  Patty is thinking...
                </li>
              ) : null}
            </ul>
          )}
        </div>

        <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
          <form
            className="flex items-center gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSend();
            }}
          >
            <Input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask Patty anything..."
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading || !draft.trim()}>
              Send
            </Button>
          </form>
        </div>
      </div>
    </main>
  );
}

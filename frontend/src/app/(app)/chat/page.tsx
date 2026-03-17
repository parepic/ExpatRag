"use client";

import { useEffect, useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import { useAppContext } from "@/context/AppContext";

export default function ChatPage() {
  useProfileGuard("chat");
  const { addChat } = useAppContext();
  const [input, setInput] = useState("");

  const { messages, sendMessage, status, error, regenerate } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  // Register this session in sidebar on first message
  useEffect(() => {
    if (messages.length === 1 && messages[0].role === "user") {
      const text = messages[0].parts
        .filter((p) => p.type === "text")
        .map((p) => (p as { type: "text"; text: string }).text)
        .join("")
        .slice(0, 40);
      addChat(text);
    }
  }, [messages, addChat]);

  const isStreaming = status === "streaming" || status === "submitted";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    sendMessage({ text });
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-[--color-text-muted] text-sm">Start a new conversation with Patty</p>
          </div>
        )}
        {messages.map((msg) => {
          const textContent = msg.parts
            .filter((p) => p.type === "text")
            .map((p) => (p as { type: "text"; text: string }).text)
            .join("");
          return (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`
                max-w-[70%] px-4 py-2.5 rounded-2xl text-sm
                ${msg.role === "user"
                  ? "bg-[--color-accent] text-white rounded-br-sm"
                  : "bg-[--color-bg-subtle] text-[--color-text] border border-[--color-border] rounded-bl-sm"
                }
              `}>
                {textContent}
              </div>
            </div>
          );
        })}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="px-4 py-2.5 rounded-2xl bg-[--color-bg-subtle] border border-[--color-border] text-sm text-[--color-text-muted] rounded-bl-sm">
              <span className="animate-pulse">Patty is thinking…</span>
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <div className="text-sm text-[--color-error] flex items-center gap-2">
              Something went wrong. Please try again.
              <button onClick={() => regenerate()} className="underline">Retry</button>
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-[--color-border] px-6 py-4 flex gap-3 items-end"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Patty anything…"
          rows={1}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e as unknown as React.FormEvent);
            }
          }}
          className="flex-1 resize-none border border-[--color-border] rounded-[--radius] px-3 py-2 text-sm text-[--color-text] placeholder:text-[--color-text-muted] focus:outline-none focus:border-[--color-accent]"
        />
        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="px-4 py-2 bg-[--color-accent] hover:bg-[--color-accent-hover] disabled:opacity-40 text-white text-sm font-medium rounded-[--radius] transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}

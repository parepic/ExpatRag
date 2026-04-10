"use client";

import { useEffect, useRef } from "react";

import { MessageBubble } from "@/components/chat/MessageBubble";
import type { Message } from "@/lib/types/chat";

type MessageListProps = {
  messages: Message[];
  isLoading: boolean;
};

export function MessageList({ messages, isLoading }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const element = containerRef.current;

    if (!element) {
      return;
    }

    element.scrollTo({
      top: element.scrollHeight,
      behavior: "smooth",
    });
  }, [isLoading, messages]);

  return (
    <div ref={containerRef} className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
      {messages.length === 0 ? (
        <div className="flex h-full items-center justify-center">
          <p className="text-sm text-muted-foreground">
            Start a new conversation with Patty
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {messages.map((message) => (
            <MessageBubble
              key={`${message.role}-${message.created_at}-${message.content}`}
              message={message}
            />
          ))}

          {isLoading ? (
            <div className="mx-auto w-full max-w-3xl px-2 py-3">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="size-2 animate-pulse rounded-full bg-primary/70" />
                Patty is thinking...
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}

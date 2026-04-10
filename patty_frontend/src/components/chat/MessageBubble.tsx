"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { CitationList } from "@/components/chat/CitationList";
import type { Message } from "@/lib/types/chat";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  if (message.role === "user") {
    return (
      <div className="mx-auto flex w-full max-w-3xl justify-end px-2 py-3">
        <div className="max-w-[85%] min-w-0 rounded-3xl rounded-br-sm bg-primary px-5 py-3 text-sm leading-7 text-primary-foreground shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl justify-start px-2 py-3">
      <div className="max-w-[85%] min-w-0 rounded-3xl rounded-bl-sm bg-secondary px-5 py-4 text-secondary-foreground shadow-sm">
        <div className="prose prose-sm max-w-none text-foreground prose-headings:mt-0 prose-headings:tracking-tight prose-p:my-0 prose-p:leading-7 prose-li:leading-7 prose-strong:text-foreground prose-a:text-primary">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {message.citations && message.citations.length > 0 ? (
          <CitationList citations={message.citations} />
        ) : null}
      </div>
    </div>
  );
}

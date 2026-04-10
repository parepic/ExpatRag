"use client";

import { ArrowUp } from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type ComposerProps = {
  onSend: (message: string) => Promise<void> | void;
  disabled: boolean;
};

function autoresize(element: HTMLTextAreaElement) {
  element.style.height = "0px";
  element.style.height = `${Math.min(element.scrollHeight, 128)}px`;
}

export function Composer({ onSend, disabled }: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    const element = textareaRef.current;

    if (!element) {
      return;
    }

    autoresize(element);
  }, [draft]);

  async function submit() {
    const trimmedDraft = draft.trim();

    if (!trimmedDraft || disabled) {
      return;
    }

    setDraft("");
    await onSend(trimmedDraft);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }

    event.preventDefault();
    void submit();
  }

  return (
    <div className="rounded-[24px] border border-border bg-background p-3 shadow-sm transition-shadow focus-within:border-ring/75 focus-within:ring-2 focus-within:ring-ring/20">
      <textarea
        ref={textareaRef}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask Patty anything..."
        disabled={disabled}
        rows={1}
        className={cn(
          "max-h-32 min-h-10 w-full resize-none bg-transparent px-1.5 py-1 text-sm leading-6 text-foreground outline-none placeholder:text-muted-foreground/80",
          disabled && "cursor-not-allowed opacity-60",
        )}
      />

      <div className="flex items-center justify-end">
        <Button
          type="button"
          size="icon-lg"
          className="rounded-full"
          onClick={() => void submit()}
          disabled={disabled || !draft.trim()}
        >
          <ArrowUp className="size-4" />
        </Button>
      </div>
    </div>
  );
}

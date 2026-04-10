"use client";

import { Button } from "@/components/ui/button";

type ChatWelcomeProps = {
  onSuggestionClick: (text: string) => void;
};

const SUGGESTIONS = [
  "How do I get a BSN?",
  "Am I eligible for the 30% ruling?",
  "What do I need to register at the gemeente?",
];

export function ChatWelcome({ onSuggestionClick }: ChatWelcomeProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-6 py-10 text-center">
      <div className="max-w-2xl">
        <p className="text-sm text-muted-foreground">
          Start a new conversation with Patty
        </p>
      </div>

      <div className="mt-6 grid w-full max-w-2xl gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map((suggestion) => (
          <Button
            key={suggestion}
            type="button"
            variant="ghost"
            className="h-auto justify-start rounded-3xl border bg-background px-4 py-3 text-left text-sm shadow-none hover:bg-muted sm:flex-col sm:items-start"
            onClick={() => onSuggestionClick(suggestion)}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

import type { Citation } from "@/lib/types/chat";

type CitationListProps = {
  citations: Citation[];
};

export function CitationList({ citations }: CitationListProps) {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <div className="mt-4 space-y-2">
      {citations.map((citation, index) => {
        const isOpen = openIndex === index;

        return (
          <button
            key={`${citation.source_url}-${index}`}
            type="button"
            onClick={() => setOpenIndex(isOpen ? -1 : index)}
            className="w-full rounded-2xl border border-border bg-muted/50 p-4 text-left transition-colors hover:bg-muted"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <Link
                  href={citation.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm font-medium text-foreground underline-offset-4 hover:underline"
                  onClick={(event) => event.stopPropagation()}
                >
                  {citation.source_title}
                </Link>
              </div>
              {isOpen ? (
                <ChevronUp className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
              ) : (
                <ChevronDown className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
              )}
            </div>

            {isOpen ? (
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                {citation.content}
              </p>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}

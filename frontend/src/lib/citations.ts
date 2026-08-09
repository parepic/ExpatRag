import type { Citation } from "@/lib/types/chat";

/**
 * Collapse a citation list down to one entry per source link.
 *
 * Retrieval emits one citation per matched chunk, so a single document that matches
 * on several passages arrives as several citations that are indistinguishable in the
 * UI. Agents can also call the RAG tool more than once in a turn, and those lists are
 * concatenated rather than merged, which repeats whole sources again.
 *
 * Citations arrive in relevance order, so the first occurrence of a link is the
 * highest-ranked one and is the copy we keep.
 */
export function dedupeCitationsByUrl(citations: Citation[]): Citation[] {
  const seen = new Set<string>();
  const unique: Citation[] = [];

  for (const citation of citations) {
    // Citations without a URL fall back to their title, so they de-duplicate against
    // each other instead of collapsing into a single entry under a shared blank key.
    const key = citation.source_url?.trim() || `title:${citation.source_title}`;

    if (seen.has(key)) {
      continue;
    }

    seen.add(key);
    unique.push(citation);
  }

  return unique;
}

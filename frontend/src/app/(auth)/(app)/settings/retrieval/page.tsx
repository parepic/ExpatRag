"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Info } from "lucide-react";
import type { ProjectSettings } from "@/lib/types/project-settings";
import {
  updateProjectSettings,
  getProjectSettings,
} from "@/lib/api/project-settings";

const RAG_STRATEGY_OPTIONS = [
  { value: "vector search", label: "Vector search" },
  { value: "hybrid search", label: "Hybrid search" },
  { value: "multi query vector search", label: "Multi-query vector" },
  { value: "multi query hybrid", label: "Multi-query hybrid" },
];

const AGENT_TYPE_OPTIONS = [
  { value: "simple", label: "Simple", description: "Only RAG search" },
  {
    value: "supervisor",
    label: "Supervisor",
    description: "Coordinates between RAG and web search",
  },
];

const SEARCH_STRATEGY_INFO: Record<string, string> = {
  "vector search":
    "Finds documents based on meaning, even if the exact words are different",
  "hybrid search":
    "Combines keyword matching and meaning-based search for more accurate results.",
  "multi query vector search":
    "Rewrites your question in different ways to find more relevant information by meaning.",
  "multi query hybrid":
    "Uses multiple versions of your question with both keyword and meaning-based search for broader and more reliable results.",
};

const DEFAULT_SETTINGS: ProjectSettings = {
  rag_strategy: "vector search",
  agent_type: "supervisor",
  chunks_per_search: 5,
  final_context_size: 5,
  similarity_threshold: 0.5,
  number_of_queries: 3,
  vector_weight: 0.5,
  keyword_weight: 0.5,
};

export default function RetrievalSettingsPage() {
  const [settings, setSettings] = useState<ProjectSettings>(DEFAULT_SETTINGS);
  const [showStrategyInfo, setShowStrategyInfo] = useState(false);
  const [rerankingEnabled, setRerankingEnabled] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const showNumberOfQueries = useMemo(
    () => settings.rag_strategy.includes("multi query"),
    [settings.rag_strategy],
  );

  const showWeightedSearch = useMemo(
    () => settings.rag_strategy.includes("hybrid"),
    [settings.rag_strategy],
  );

  const keywordWeight = useMemo(
    () => 1.0 - (settings.vector_weight ?? 0.5),
    [settings.vector_weight],
  );

  const updateStrategy = (nextValue: string) => {
    setSettings((currentSettings) => {
      const updated = { ...currentSettings, rag_strategy: nextValue };

      if (!nextValue.includes("multi query")) {
        delete updated.number_of_queries;
      } else if (!updated.number_of_queries) {
        updated.number_of_queries = 3;
      }

      if (!nextValue.includes("hybrid")) {
        delete updated.vector_weight;
        delete updated.keyword_weight;
      } else if (!updated.vector_weight) {
        updated.vector_weight = 0.5;
        updated.keyword_weight = 0.5;
      } else {
        updated.keyword_weight = Number(
          (1.0 - updated.vector_weight).toFixed(1),
        );
      }

      return updated;
    });
  };

  const updateVectorWeight = (nextValue: number) => {
    const vector = Number(nextValue.toFixed(1));
    setSettings((currentSettings) => ({
      ...currentSettings,
      vector_weight: vector,
      keyword_weight: Number((1.0 - vector).toFixed(1)),
    }));
  };

  const buildSavePayload = (current: ProjectSettings): ProjectSettings => {
    const payload: ProjectSettings = { ...current };
    const strategy = payload.rag_strategy ?? "";

    if (strategy.includes("hybrid")) {
      const vector = Number((payload.vector_weight ?? 0.5).toFixed(1));
      payload.vector_weight = vector;
      payload.keyword_weight = Number((1.0 - vector).toFixed(1));
    } else {
      delete payload.vector_weight;
      delete payload.keyword_weight;
    }

    if (!strategy.includes("multi query")) {
      delete payload.number_of_queries;
    } else if (!payload.number_of_queries) {
      payload.number_of_queries = 3;
    }

    return payload;
  };

  const handleSaveDraft = async () => {
    setIsSaving(true);
    setSaveError(null);
    try {
      const payload = buildSavePayload(settings);
      await updateProjectSettings(payload);
      setSettings((prev) => ({ ...prev, ...payload }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : String(err ?? "Failed to save settings");
      setSaveError(msg);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    setIsLoading(true);
    setLoadError(null);

    getProjectSettings()
      .then((data) => {
        if (!mounted) return;
        const merged: ProjectSettings = {
          ...DEFAULT_SETTINGS,
          ...data,
          rag_strategy: data.rag_strategy ?? DEFAULT_SETTINGS.rag_strategy,
          agent_type: data.agent_type ?? DEFAULT_SETTINGS.agent_type,
          chunks_per_search:
            data.chunks_per_search ?? DEFAULT_SETTINGS.chunks_per_search,
          final_context_size:
            data.final_context_size ?? DEFAULT_SETTINGS.final_context_size,
          similarity_threshold:
            data.similarity_threshold ?? DEFAULT_SETTINGS.similarity_threshold,
        };

        const payload = buildSavePayload(merged);
        setSettings(payload);
      })
      .catch((err: unknown) => {
        const msg =
          err instanceof Error
            ? err.message
            : String(err ?? "Failed to load settings");
        if (mounted) setLoadError(msg);
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="px-6 py-8">
      <div className="mx-auto w-full max-w-3xl rounded-2xl border border-border bg-card p-6 shadow-sm">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
              Retrieval
            </p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">
              Retrieval settings
            </h1>
          </div>

          <div className="rounded-full border border-border bg-background px-3 py-1 text-xs font-medium text-muted-foreground">
            Draft
          </div>
        </div>

        <p className="mt-6 text-sm leading-6 text-muted-foreground">
          Configure how Patty retrieves and ranks information. Choose an agent
          execution style, then select a search strategy and adjust the tuning
          parameters that appear below.
        </p>

        <div className="mt-8 space-y-4">
          <section className="rounded-lg border border-border bg-background px-3 py-3">
            <Label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Agent type
            </Label>
            <div className="mt-3 space-y-2">
              {AGENT_TYPE_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex cursor-pointer items-start gap-2"
                >
                  <input
                    type="radio"
                    name="agent_type"
                    value={option.value}
                    checked={settings.agent_type === option.value}
                    onChange={(event) =>
                      setSettings((currentSettings) => ({
                        ...currentSettings,
                        agent_type: event.target.value,
                      }))
                    }
                    className="mt-1 h-3 w-3 cursor-pointer accent-primary"
                  />
                  <div>
                    <span className="text-xs font-medium text-foreground">
                      {option.label}
                    </span>
                    <p className="text-xs text-muted-foreground">
                      {option.description}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-border bg-background px-3 py-3">
            <div className="flex items-center gap-2">
              <Label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Search strategy
              </Label>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowStrategyInfo((current) => !current)}
                  className="rounded-full p-1 hover:bg-muted"
                  aria-label="Show search strategy info"
                >
                  <Info className="h-3 w-3 text-muted-foreground" />
                </button>
              </div>
            </div>
            <div className="mt-3 space-y-2">
              {RAG_STRATEGY_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex cursor-pointer items-center gap-2"
                >
                  <input
                    type="radio"
                    name="rag_strategy"
                    value={option.value}
                    checked={settings.rag_strategy === option.value}
                    onChange={(event) => updateStrategy(event.target.value)}
                    className="h-3 w-3 cursor-pointer accent-primary"
                  />
                  <span className="text-xs text-foreground">
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          </section>

          {showStrategyInfo ? (
            <div
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6 backdrop-blur-sm"
              onClick={() => setShowStrategyInfo(false)}
            >
              <div
                role="dialog"
                aria-modal="true"
                aria-label="Search strategy information"
                className="w-full max-w-2xl rounded-2xl border border-border bg-card p-4 shadow-2xl sm:p-6"
                onClick={(event) => event.stopPropagation()}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      Search strategy
                    </p>
                    <h2 className="mt-1 text-lg font-semibold text-foreground sm:text-xl">
                      How the four search modes work
                    </h2>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowStrategyInfo(false)}
                    className="rounded px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  >
                    Close
                  </button>
                </div>

                <div className="mt-4 grid gap-3 text-sm text-muted-foreground sm:grid-cols-2">
                  {RAG_STRATEGY_OPTIONS.map((option) => (
                    <div
                      key={option.value}
                      className="rounded-xl border border-border bg-background p-3"
                    >
                      <p className="font-medium text-foreground">
                        {option.label}
                      </p>
                      <p className="mt-1 leading-6">
                        {SEARCH_STRATEGY_INFO[option.value]}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          <div className="rounded-lg border border-border bg-background p-3">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Search parameters
            </h3>

            <section className="mt-3 space-y-3">
              <div className="rounded-md border border-border/50 bg-background px-2 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Label className="text-xs font-medium text-foreground">
                      Chunks per search
                    </Label>
                    <p className="mt-0.5 text-xs leading-3 text-muted-foreground">
                      Number of chunks retrieved per query.
                    </p>
                  </div>
                  <span className="rounded-full border border-border bg-card px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    {settings.chunks_per_search}
                  </span>
                </div>
                <div className="mt-2">
                  <input
                    type="range"
                    min={3}
                    max={10}
                    step={1}
                    value={settings.chunks_per_search ?? 5}
                    onChange={(event) =>
                      setSettings((currentSettings) => ({
                        ...currentSettings,
                        chunks_per_search: Number(event.target.value),
                      }))
                    }
                    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                  <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                    <span>3</span>
                    <span>10</span>
                  </div>
                </div>
              </div>

              <div className="rounded-md border border-border/50 bg-background px-2 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Label className="text-xs font-medium text-foreground">
                      Final context size
                    </Label>
                    <p className="mt-0.5 text-xs leading-3 text-muted-foreground">
                      Chunks to keep before model processing.
                    </p>
                  </div>
                  <span className="rounded-full border border-border bg-card px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    {settings.final_context_size}
                  </span>
                </div>
                <div className="mt-2">
                  <input
                    type="range"
                    min={3}
                    max={10}
                    step={1}
                    value={settings.final_context_size ?? 5}
                    onChange={(event) =>
                      setSettings((currentSettings) => ({
                        ...currentSettings,
                        final_context_size: Number(event.target.value),
                      }))
                    }
                    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                  <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                    <span>3</span>
                    <span>10</span>
                  </div>
                </div>
              </div>

              <div className="rounded-md border border-border/50 bg-background px-2 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Label className="text-xs font-medium text-foreground">
                      Similarity threshold
                    </Label>
                    <p className="mt-0.5 text-xs leading-3 text-muted-foreground">
                      Minimum score for chunk relevance.
                    </p>
                  </div>
                  <span className="rounded-full border border-border bg-card px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    {settings.similarity_threshold.toFixed(1)}
                  </span>
                </div>
                <div className="mt-2">
                  <input
                    type="range"
                    min={0.1}
                    max={0.9}
                    step={0.1}
                    value={settings.similarity_threshold ?? 0.5}
                    onChange={(event) =>
                      setSettings((currentSettings) => ({
                        ...currentSettings,
                        similarity_threshold: Number(event.target.value),
                      }))
                    }
                    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                  <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                    <span>0.1</span>
                    <span>0.9</span>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {showNumberOfQueries ? (
            <div className="rounded-lg border border-border bg-background p-3">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Multi-query settings
              </h3>

              <section className="mt-3 rounded-md border border-border/50 bg-background px-2 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Label className="text-xs font-medium text-foreground">
                      Number of queries
                    </Label>
                    <p className="mt-0.5 text-xs leading-3 text-muted-foreground">
                      Alternative queries per search.
                    </p>
                  </div>
                  <span className="rounded-full border border-border bg-card px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    {settings.number_of_queries}
                  </span>
                </div>
                <div className="mt-2">
                  <input
                    type="range"
                    min={3}
                    max={7}
                    step={1}
                    value={settings.number_of_queries || 3}
                    onChange={(event) =>
                      setSettings((currentSettings) => ({
                        ...currentSettings,
                        number_of_queries: Number(event.target.value),
                      }))
                    }
                    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                  <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                    <span>3</span>
                    <span>7</span>
                  </div>
                </div>
              </section>
            </div>
          ) : null}

          {showWeightedSearch ? (
            <div className="rounded-lg border border-border bg-background p-3">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Hybrid search weights
              </h3>

              <section className="mt-3 rounded-md border border-border/50 bg-background px-2 py-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Label className="text-xs font-medium text-foreground">
                      Vector vs. keyword balance
                    </Label>
                    <p className="mt-0.5 text-xs leading-3 text-muted-foreground">
                      Weighting for semantic vs. keyword search.
                    </p>
                  </div>
                  <span className="rounded-full border border-border bg-card px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    V: {(settings.vector_weight ?? 0.5).toFixed(1)} / K:{" "}
                    {keywordWeight.toFixed(1)}
                  </span>
                </div>

                <div className="mt-2">
                  <input
                    type="range"
                    min={0.1}
                    max={0.9}
                    step={0.1}
                    value={settings.vector_weight ?? 0.5}
                    onChange={(event) =>
                      updateVectorWeight(Number(event.target.value))
                    }
                    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                  <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                    <span>More keyword</span>
                    <span>More vector</span>
                  </div>
                </div>
              </section>
            </div>
          ) : null}

          <section className="rounded-lg border border-border bg-background p-3">
            <Label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Reranking
            </Label>
            <div className="mt-3 space-y-2">
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="radio"
                  name="reranking"
                  value="enabled"
                  checked={rerankingEnabled}
                  onChange={() => setRerankingEnabled(true)}
                  className="h-3 w-3 cursor-pointer accent-primary"
                />
                <span className="text-xs text-foreground">Enabled</span>
              </label>
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="radio"
                  name="reranking"
                  value="disabled"
                  checked={!rerankingEnabled}
                  onChange={() => setRerankingEnabled(false)}
                  className="h-3 w-3 cursor-pointer accent-primary"
                />
                <span className="text-xs text-foreground">Disabled</span>
              </label>
            </div>
          </section>

          <div className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-background px-4 py-4">
            <div>
              <p className="text-sm font-medium text-foreground">
                Current configuration
              </p>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">
                This is a local draft for now. The controls match the backend
                schema and can be wired to persistence later.
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              {saveError ? (
                <p className="text-xs text-destructive">{saveError}</p>
              ) : null}
              {loadError ? (
                <p className="text-xs text-destructive">{loadError}</p>
              ) : null}
              <Button
                type="button"
                variant="outline"
                onClick={handleSaveDraft}
                disabled={isSaving || isLoading}
              >
                {isSaving
                  ? "Saving..."
                  : saved
                    ? "Saved"
                    : isLoading
                      ? "Loading..."
                      : "Save draft"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

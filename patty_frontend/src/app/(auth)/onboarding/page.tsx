"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { updateUser } from "@/lib/api/users";
import { ONBOARDING_QUESTIONS } from "@/lib/onboarding/questions";
import type { User } from "@/lib/types/user";

type OnboardingAnswerKey = (typeof ONBOARDING_QUESTIONS)[number]["key"];
type OnboardingAnswers = Partial<Pick<User, OnboardingAnswerKey>>;

export default function OnboardingPage() {
  const router = useRouter();
  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [answers, setAnswers] = useState<OnboardingAnswers>({});
  const [completed, setCompleted] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  const isLastStep = stepIndex === ONBOARDING_QUESTIONS.length - 1;

  function handleBack() {
    if (stepIndex === 0) {
      return;
    }

    setDirection("back");
    setStepIndex((current) => current - 1);
  }

  async function handleNext() {
    setError("");

    if (!isLastStep) {
      setDirection("forward");
      setStepIndex((current) => current + 1);
      return;
    }

    setIsSaving(true);

    try {
      const payload = Object.fromEntries(
        Object.entries(answers).filter(([, value]) => value !== null),
      ) as Record<string, string | boolean>;

      await updateUser(payload);
      setCompleted(true);
    } catch (caughtError) {
      if (caughtError instanceof Error) {
        setError(caughtError.message);
      } else {
        setError("Failed to save onboarding answers");
      }
    } finally {
      setIsSaving(false);
    }
  }

  function handleSkip() {
    router.push("/chat");
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-2xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Protected Route
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Onboarding navigation ready
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Step 5 adds linear navigation, finish/save behavior, and skip
          handling. Rendering the actual wizard comes next.
        </p>

        <div className="mt-8 space-y-3 text-sm">
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Current step index</p>
            <p className="mt-1 text-muted-foreground">{stepIndex}</p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Direction</p>
            <p className="mt-1 text-muted-foreground">{direction}</p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Completed</p>
            <p className="mt-1 text-muted-foreground">
              {completed ? "Yes" : "No"}
            </p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Saving</p>
            <p className="mt-1 text-muted-foreground">
              {isSaving ? "Yes" : "No"}
            </p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Questions</p>
            <p className="mt-1 text-muted-foreground">
              {ONBOARDING_QUESTIONS.length} total
            </p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Current action label</p>
            <p className="mt-1 text-muted-foreground">
              {isLastStep ? "Finish" : "Next"}
            </p>
          </div>
          <div className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3">
            <p className="font-medium text-foreground">Collected answers</p>
            <pre className="mt-2 overflow-x-auto text-xs leading-6 text-muted-foreground">
              {JSON.stringify(answers, null, 2)}
            </pre>
          </div>
          {error ? (
            <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-3">
              <p className="font-medium text-destructive">Error</p>
              <p className="mt-1 text-destructive">{error}</p>
            </div>
          ) : null}
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <button
            type="button"
            className="rounded-full border border-border px-4 py-2 text-sm"
            onClick={handleBack}
            disabled={stepIndex === 0}
          >
            Back
          </button>
          <button
            type="button"
            className="rounded-full border border-border px-4 py-2 text-sm"
            onClick={handleNext}
            disabled={isSaving}
          >
            {isLastStep ? "Finish" : "Next"}
          </button>
          <button
            type="button"
            className="rounded-full border border-border px-4 py-2 text-sm"
            onClick={handleSkip}
          >
            Skip onboarding
          </button>
        </div>
      </div>
    </main>
  );
}

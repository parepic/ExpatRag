"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence } from "framer-motion";

import { Button } from "@/components/ui/button";
import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { ProgressDots } from "@/components/onboarding/ProgressDots";
import { QuestionCard } from "@/components/onboarding/QuestionCard";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { updateUser } from "@/lib/api/users";
import { ONBOARDING_QUESTIONS } from "@/lib/onboarding/questions";
import type { UserProfile } from "@/lib/types/user";

type OnboardingAnswerKey = (typeof ONBOARDING_QUESTIONS)[number]["key"];
type OnboardingAnswers = Partial<Pick<UserProfile, OnboardingAnswerKey>>;

export default function OnboardingPage() {
  const router = useRouter();
  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [answers, setAnswers] = useState<OnboardingAnswers>({});
  const [completed, setCompleted] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  const currentQuestion = ONBOARDING_QUESTIONS[stepIndex];
  const isLastStep = stepIndex === ONBOARDING_QUESTIONS.length - 1;

  useEffect(() => {
    if (!completed) {
      return;
    }

    const redirectTimeout = window.setTimeout(() => {
      router.push("/chat");
    }, 3000);

    return () => {
      window.clearTimeout(redirectTimeout);
    };
  }, [completed, router]);

  function setAnswer<K extends OnboardingAnswerKey>(
    key: K,
    value: OnboardingAnswers[K],
  ) {
    setAnswers((current) => ({
      ...current,
      [key]: value,
    }));
  }

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

  if (completed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6 py-16">
        <div className="w-full max-w-xl rounded-3xl border border-border bg-card p-8 text-center shadow-sm">
          <div className="space-y-6">
            <h1 className="text-3xl font-semibold tracking-tight text-foreground">
              You&apos;re all set!
            </h1>
            <p className="text-sm leading-6 text-muted-foreground">
              We&apos;ve saved your details and will use them to give you
              personalised advice.
            </p>
            <div className="flex flex-col items-center gap-3">
              <div
                className="h-6 w-6 animate-spin rounded-full border-2 border-primary/25 border-t-primary"
                aria-hidden="true"
              />
              <p className="text-sm text-muted-foreground">
                Starting your chat with Patty...
              </p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-16">
      <div className="flex w-full max-w-3xl flex-col items-center">
        <div className="mb-6 flex w-full max-w-xl justify-start">
          <Button
            type="button"
            variant="outline"
            onClick={handleBack}
            disabled={stepIndex === 0}
          >
            Back
          </Button>
        </div>

        <AnimatePresence mode="wait" initial={false}>
          <QuestionCard key={currentQuestion.key} direction={direction}>
            <div className="space-y-8">
              <div className="space-y-3">
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
                  Step {stepIndex + 1} of {ONBOARDING_QUESTIONS.length}
                </p>
                <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                  {currentQuestion.label}
                </h1>
                {currentQuestion.sublabel ? (
                  <p className="text-sm leading-6 text-muted-foreground">
                    {currentQuestion.sublabel}
                  </p>
                ) : null}
              </div>

              {currentQuestion.type === "chip" ? (
                <ChipSelect
                  options={currentQuestion.options ?? []}
                  value={(answers[currentQuestion.key] as string | null) ?? null}
                  onChange={(value) =>
                    setAnswer(
                      currentQuestion.key,
                      value as OnboardingAnswers[typeof currentQuestion.key],
                    )
                  }
                />
              ) : (
                <YesNoToggle
                  value={(answers[currentQuestion.key] as boolean | null) ?? null}
                  onChange={(value) =>
                    setAnswer(
                      currentQuestion.key,
                      value as OnboardingAnswers[typeof currentQuestion.key],
                    )
                  }
                />
              )}

              {error ? <p className="text-sm text-destructive">{error}</p> : null}

              <div className="flex justify-center">
                <Button type="button" onClick={handleNext} disabled={isSaving}>
                  {isSaving ? "Saving..." : isLastStep ? "Finish" : "Next"}
                </Button>
              </div>
            </div>
          </QuestionCard>
        </AnimatePresence>

        <div className="mt-6">
          <ProgressDots total={ONBOARDING_QUESTIONS.length} current={stepIndex + 1} />
        </div>

        <button
          type="button"
          className="mt-6 text-sm text-muted-foreground underline-offset-4 hover:underline"
          onClick={handleSkip}
        >
          Skip onboarding
        </button>
      </div>
    </main>
  );
}

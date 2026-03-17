"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { LanguageCombobox } from "@/components/onboarding/LanguageCombobox";
import { ProgressDots } from "@/components/onboarding/ProgressDots";
import { QuestionCard } from "@/components/onboarding/QuestionCard";
import { getField, setField, getMissingFields, REQUIRED_FIELDS } from "@/lib/profile";
import { NATIONALITY_OPTIONS } from "@/lib/constants/nationality-options";
import { PURPOSE_OPTIONS } from "@/lib/constants/purpose-types";
import { OCCUPATION_OPTIONS } from "@/lib/constants/occupation-types";
import { REGISTRATION_OPTIONS } from "@/lib/constants/registration-status";
import { HOUSING_OPTIONS } from "@/lib/constants/housing-options";
import { SALARY_BANDS } from "@/lib/constants/salary-bands";
import { RESIDENCY_OPTIONS } from "@/lib/constants/residency-options";
import { useProfileGuard } from "@/hooks/useProfileGuard";

interface Question {
  key: string;
  label: string;
  sublabel?: string;
  type: "chip" | "yesno" | "language";
  options?: readonly string[];
}

const QUESTIONS: Question[] = [
  { key: "nationality", label: "What is your nationality / citizenship status?", type: "chip", options: NATIONALITY_OPTIONS },
  { key: "purpose_of_stay", label: "What is your main reason for coming to the Netherlands?", type: "chip", options: PURPOSE_OPTIONS },
  { key: "employment_situation", label: "What is your employment situation?", type: "chip", options: OCCUPATION_OPTIONS },
  { key: "registration_status", label: "What is your current registration status in the Netherlands?", type: "chip", options: REGISTRATION_OPTIONS },
  { key: "has_fiscal_partner", label: "Do you have a fiscal (registered) partner?", sublabel: "Married, registered partnership, or cohabiting at the same address.", type: "yesno" },
  { key: "housing_situation", label: "What is your current or planned housing situation?", type: "chip", options: HOUSING_OPTIONS },
  { key: "salary_band", label: "What is your gross annual salary (or expected income)?", type: "chip", options: SALARY_BANDS },
  { key: "age_bracket", label: "Are you under 30 years old?", sublabel: "This affects eligibility for the HSM permit and 30% ruling.", type: "yesno" },
  { key: "prior_nl_residency", label: "Have you previously lived in the Netherlands?", type: "chip", options: RESIDENCY_OPTIONS },
  { key: "languages", label: "What languages do you speak?", type: "language" },
];

export default function OnboardingPage() {
  useProfileGuard("onboarding");
  const router = useRouter();

  const getStartIndex = () => {
    const missing = getMissingFields();
    if (missing.length === 0) return 0;
    const firstMissingKey = missing[0];
    const idx = QUESTIONS.findIndex((q) => q.key === firstMissingKey);
    return idx >= 0 ? idx : 0;
  };

  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const start = getStartIndex();
    setStepIndex(start);
    const saved: Record<string, string | string[]> = {};
    QUESTIONS.forEach((q) => {
      const val = getField(q.key as any);
      if (val) {
        try { saved[q.key] = JSON.parse(val); }
        catch { saved[q.key] = val; }
      }
    });
    setAnswers(saved);
  }, []);

  const currentQuestion = QUESTIONS[stepIndex];
  const currentAnswer = answers[currentQuestion?.key ?? ""];
  const hasAnswer = currentAnswer !== undefined && currentAnswer !== null &&
    (Array.isArray(currentAnswer) ? currentAnswer.length > 0 : currentAnswer !== "");
  const isFirst = stepIndex === 0;
  const isLast = stepIndex === QUESTIONS.length - 1;

  function setAnswer(key: string, value: string | string[]) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit() {
    const key = currentQuestion.key;
    const value = answers[key];
    const stored = Array.isArray(value) ? JSON.stringify(value) : String(value);
    setField(key as any, stored);

    if (isLast) {
      setCompleted(true);
    } else {
      setDirection("forward");
      setStepIndex((i) => i + 1);
    }
  }

  function handleBack() {
    setDirection("back");
    setStepIndex((i) => i - 1);
  }

  function handleForward() {
    setDirection("forward");
    setStepIndex((i) => i + 1);
  }

  const answeredCount = QUESTIONS.filter((q) => {
    const val = answers[q.key];
    return val !== undefined && (Array.isArray(val) ? val.length > 0 : val !== "");
  }).length;

  if (completed) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-[--color-bg] px-4">
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="w-full max-w-lg bg-white rounded-[--radius] border border-[--color-border] p-8 shadow-sm text-center"
        >
          <div className="text-4xl mb-4">🎉</div>
          <h2 className="text-xl font-semibold mb-2">You're all set!</h2>
          <p className="text-[--color-text-muted] mb-6">
            We've saved your details and will use them to give you personalised advice.
          </p>
          <button
            onClick={() => router.push("/chat")}
            className="px-6 py-3 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white rounded-[--radius] font-medium transition-colors"
          >
            Start chatting with Patty
          </button>
        </motion.div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-[--color-bg] px-4">
      {/* Back / Forward buttons */}
      <div className="w-full max-w-lg flex justify-between mb-4">
        <button
          onClick={handleBack}
          disabled={isFirst}
          className="text-sm text-[--color-text-muted] disabled:opacity-30 hover:text-[--color-text] transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={handleForward}
          disabled={!hasAnswer || isLast}
          className="text-sm text-[--color-text-muted] disabled:opacity-30 hover:text-[--color-text] transition-colors"
        >
          Forward →
        </button>
      </div>

      {/* Question card */}
      <AnimatePresence mode="wait" custom={direction}>
        <QuestionCard key={stepIndex} direction={direction}>
          <h2 className="text-lg font-semibold mb-1">{currentQuestion.label}</h2>
          {currentQuestion.sublabel && (
            <p className="text-sm text-[--color-text-muted] mb-4">{currentQuestion.sublabel}</p>
          )}
          <div className="mt-4">
            {currentQuestion.type === "chip" && (
              <ChipSelect
                options={currentQuestion.options!}
                value={(currentAnswer as string) ?? null}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
            {currentQuestion.type === "yesno" && (
              <YesNoToggle
                value={(currentAnswer as "yes" | "no") ?? null}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
            {currentQuestion.type === "language" && (
              <LanguageCombobox
                value={(currentAnswer as string[]) ?? []}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
          </div>
          <div className="mt-6">
            <button
              onClick={handleSubmit}
              disabled={!hasAnswer}
              className="w-full py-2.5 bg-[--color-accent] hover:bg-[--color-accent-hover] disabled:opacity-40 text-white rounded-[--radius] font-medium transition-colors"
            >
              {isLast ? "Finish" : "Next"}
            </button>
          </div>
        </QuestionCard>
      </AnimatePresence>

      {/* Progress dots */}
      <div className="mt-6">
        <ProgressDots total={QUESTIONS.length} current={answeredCount} />
      </div>
    </main>
  );
}

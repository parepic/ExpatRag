import { ONBOARDING_QUESTIONS } from "@/lib/onboarding/questions";

export default function OnboardingPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-2xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Protected Route
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Onboarding questions defined
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Step 3 sets up the typed question list. The wizard state and rendering
          logic come next.
        </p>

        <div className="mt-8 space-y-3">
          {ONBOARDING_QUESTIONS.map((question, index) => (
            <div
              key={question.key}
              className="rounded-2xl border border-border/80 bg-muted/30 px-4 py-3 text-sm"
            >
              <p className="font-medium text-foreground">
                {index + 1}. {question.label}
              </p>
              <p className="mt-1 text-muted-foreground">
                {question.type === "chip"
                  ? `${question.options?.length ?? 0} options`
                  : "Yes / No"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

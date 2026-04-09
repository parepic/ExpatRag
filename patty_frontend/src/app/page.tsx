"use client";

import { useAuth } from "@/hooks/useAuth";

export default function Home() {
  const { user, isLoading } = useAuth();

  const statusMessage = isLoading
    ? "Checking login status..."
    : user
      ? `You are already logged in as ${user.username}.`
      : "You are not logged in.";

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="fixed right-4 top-4 z-50 max-w-sm rounded-2xl border border-border bg-card/95 px-4 py-3 text-sm shadow-lg backdrop-blur">
        <p className="font-medium text-foreground">{statusMessage}</p>
      </div>

      <div className="w-full max-w-2xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Patty Frontend v2
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-foreground">
          Fresh frontend scaffold in place.
        </h1>
        <p className="mt-4 max-w-xl text-base leading-7 text-muted-foreground">
          This starter page replaces the default Vercel intro so the project now
          has an app-specific baseline while we build out the real routes and UI.
        </p>
      </div>
    </main>
  );
}

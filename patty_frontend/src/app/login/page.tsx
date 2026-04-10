"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (user) {
      router.push("/chat");
    }
  }, [router, user]);

  if (isLoading) {
    return null;
  }

  if (user) {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-2xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Public Route
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Login page scaffold
        </h1>
      </div>
    </main>
  );
}

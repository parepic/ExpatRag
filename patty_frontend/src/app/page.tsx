"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AnimatedChat } from "@/components/welcome/AnimatedChat";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

const VALUE_HIGHLIGHTS = [
  {
    icon: "↗",
    text: "Every answer cited from official Dutch sources",
  },
  {
    icon: "◎",
    text: "Personalized to your visa, job, and situation",
  },
  {
    icon: "◌",
    text: "Ask in plain language, without legal jargon",
  },
  {
    icon: "€",
    text: "Free to use, with no lawyer-fee shock",
  },
] as const;

export default function Home() {
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
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-background px-6 py-16">
      <AnimatedChat />
      <section className="relative z-10 flex w-full max-w-4xl flex-col items-center text-center">
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-foreground md:text-5xl">
          Your all-in-one expat moving assistant
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
          Personalized legal and compliance guidance for expats in the
          Netherlands, grounded in official Dutch sources you can actually
          trust.
        </p>
        <div className="mt-10 grid w-full max-w-3xl grid-cols-1 gap-4 sm:grid-cols-2">
          {VALUE_HIGHLIGHTS.map((item) => (
            <div
              key={item.text}
              className="flex items-center justify-center gap-3 text-sm text-muted-foreground sm:justify-start"
            >
              <span className="text-base text-foreground">{item.icon}</span>
              <span>{item.text}</span>
            </div>
          ))}
        </div>
        <div className="mt-12">
          <Button
            size="lg"
            className="rounded-full px-12 shadow-xl shadow-primary/25 transition-transform hover:-translate-y-0.5 hover:shadow-2xl hover:shadow-primary/30"
            onClick={() => router.push("/login")}
          >
            Get Started
          </Button>
        </div>
      </section>
    </main>
  );
}

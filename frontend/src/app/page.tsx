"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { isComplete } from "@/lib/profile";
import { AnimatedChat } from "@/components/welcome/AnimatedChat";
import { Button } from "@/components/ui/button";

export default function WelcomePage() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (isComplete()) {
      router.push("/chat");
    } else {
      setChecked(true);
    }
  }, [router]);

  if (!checked) return null;

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-background">
      <AnimatedChat />

      {/* Foreground content */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 flex flex-col items-center text-center px-6"
      >
        <h1 className="max-w-2xl text-4xl font-bold leading-tight text-foreground md:text-5xl">
          Your all-in-one expat moving assistant
        </h1>
        <p className="mt-4 max-w-md text-lg text-muted-foreground">
          Personalised legal and compliance guidance for expats in the Netherlands — cited from official sources.
        </p>
      </motion.div>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="absolute bottom-16 z-10"
      >
        <Button
          onClick={() => router.push("/onboarding")}
          size="lg"
          className="rounded-full px-8 shadow-md"
        >
          Get Started
        </Button>
      </motion.div>
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { isComplete } from "@/lib/profile";
import { AnimatedChat } from "@/components/welcome/AnimatedChat";

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
    <main className="relative min-h-screen flex flex-col items-center justify-center bg-white overflow-hidden">
      <AnimatedChat />

      {/* Foreground content */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 flex flex-col items-center text-center px-6"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-[--color-text] leading-tight max-w-2xl">
          Your all-in-one expat moving assistant
        </h1>
        <p className="mt-4 text-[--color-text-muted] text-lg max-w-md">
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
        <button
          onClick={() => router.push("/onboarding")}
          className="px-8 py-3.5 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white text-base font-semibold rounded-full shadow-md transition-colors"
        >
          Get Started
        </button>
      </motion.div>
    </main>
  );
}

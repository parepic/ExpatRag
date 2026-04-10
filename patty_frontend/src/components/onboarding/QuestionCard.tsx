"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

type QuestionCardProps = {
  direction: "forward" | "back";
  children: ReactNode;
};

const variants = {
  enter: (direction: "forward" | "back") => ({
    x: direction === "forward" ? 40 : -40,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: "forward" | "back") => ({
    x: direction === "forward" ? -40 : 40,
    opacity: 0,
  }),
};

export function QuestionCard({
  direction,
  children,
}: QuestionCardProps) {
  return (
    <motion.div
      custom={direction}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className="w-full max-w-xl rounded-3xl border border-border bg-card p-8 shadow-sm"
    >
      {children}
    </motion.div>
  );
}

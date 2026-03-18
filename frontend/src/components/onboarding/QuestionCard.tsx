"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface QuestionCardProps {
  children: ReactNode;
  direction?: "forward" | "back";
}

const variants = {
  enter: (direction: "forward" | "back") => ({
    y: direction === "forward" ? 40 : -40,
    opacity: 0,
  }),
  center: { y: 0, opacity: 1 },
  exit: (direction: "forward" | "back") => ({
    y: direction === "forward" ? -40 : 40,
    opacity: 0,
  }),
};

export function QuestionCard({ children, direction = "forward" }: QuestionCardProps) {
  return (
    <motion.div
      custom={direction}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className="w-full max-w-lg rounded-[--radius] border border-border bg-card p-8 shadow-sm"
    >
      {children}
    </motion.div>
  );
}

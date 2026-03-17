"use client";

import { useEffect, useState } from "react";

const SCRIPT = [
  { role: "user", text: "Can you help me get started with my DigiD?" },
  { role: "patty", text: "Of course! DigiD is your digital identity for Dutch government services. First, you'll need a BSN number from your municipality." },
  { role: "user", text: "How do I get a BSN number?" },
  { role: "patty", text: "You get your BSN when you register at your local gemeente. Book an appointment at the BRP desk — you'll need your passport and proof of address." },
  { role: "user", text: "What documents do I need?" },
  { role: "patty", text: "Bring a valid passport or ID, a completed registration form, and proof of your Dutch address (e.g. rental contract or letter from your landlord)." },
];

export function AnimatedChat() {
  const [visible, setVisible] = useState<number[]>([]);

  useEffect(() => {
    let i = 0;
    let cancelled = false;

    function showNext() {
      if (cancelled) return;
      setVisible((prev) => [...prev, i]);
      i++;
      if (i < SCRIPT.length) {
        setTimeout(showNext, 1800);
      } else {
        setTimeout(() => {
          if (cancelled) return;
          setVisible([]);
          i = 0;
          setTimeout(showNext, 600);
        }, 3000);
      }
    }

    const timer = setTimeout(showNext, 800);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  return (
    <div
      className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none"
      style={{ opacity: 0.18, filter: "blur(1.5px)" }}
    >
      <div className="w-full max-w-sm flex flex-col gap-3 px-6">
        {SCRIPT.map((msg, i) => (
          <div
            key={i}
            className={[
              "transition-all duration-500",
              visible.includes(i) ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2",
              msg.role === "user" ? "self-end" : "self-start",
            ].join(" ")}
          >
            <div
              className={[
                "px-4 py-2 rounded-2xl text-sm max-w-[260px]",
                msg.role === "user"
                  ? "bg-[--color-accent] text-white rounded-br-sm"
                  : "bg-[--color-bg-subtle] text-[--color-text] border border-[--color-border] rounded-bl-sm",
              ].join(" ")}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

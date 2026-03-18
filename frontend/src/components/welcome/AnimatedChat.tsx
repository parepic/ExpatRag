"use client";

import { useEffect, useState } from "react";

const SCRIPT_1 = [
  { role: "user", text: "Can you help me get started with my DigiD?" },
  { role: "patty", text: "Of course! DigiD is your digital identity for Dutch government services. First, you'll need a BSN number from your municipality." },
  { role: "user", text: "How do I get a BSN number?" },
  { role: "patty", text: "You get your BSN when you register at your local gemeente. Book an appointment at the BRP desk — you'll need your passport and proof of address." },
  { role: "user", text: "What documents do I need?" },
  { role: "patty", text: "Bring a valid passport or ID, a completed registration form, and proof of your Dutch address (e.g. rental contract or letter from your landlord)." },
];

const SCRIPT_2 = [
  { role: "user", text: "Am I eligible for the 30% ruling?" },
  { role: "patty", text: "The 30% ruling lets qualifying expats receive 30% of their salary tax-free. You must be hired from abroad for specific expertise." },
  { role: "user", text: "What are the main requirements?" },
  { role: "patty", text: "You need to earn above €46,107, have lived 150+ km from the Dutch border before hiring, and have skills scarce in the Netherlands." },
  { role: "user", text: "How does my employer apply?" },
  { role: "patty", text: "Your employer applies with the Belastingdienst within 4 months of your start date, using your employment contract and foreign address proof." },
];

type Script = typeof SCRIPT_1;

function ChatColumn({ script, delayMs }: { script: Script; delayMs: number }) {
  const [visible, setVisible] = useState<number[]>([]);

  useEffect(() => {
    let i = 0;
    let cancelled = false;

    function showNext() {
      if (cancelled) return;
      setVisible((prev) => [...prev, i]);
      i++;
      if (i < script.length) {
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

    const timer = setTimeout(showNext, delayMs);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [script, delayMs]);

  return (
    <div className="flex flex-col gap-3">
      {script.map((msg, i) => (
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
                ? "rounded-br-sm bg-primary text-primary-foreground"
                : "rounded-bl-sm border border-border bg-card text-card-foreground",
            ].join(" ")}
          >
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  );
}

export function AnimatedChat() {
  return (
    <div
      className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none"
      style={{ opacity: 0.18, filter: "blur(1.5px)" }}
    >
      <div className="grid grid-cols-2 gap-8 max-w-5xl w-[80%] px-6">
        <ChatColumn script={SCRIPT_1} delayMs={800} />
        <ChatColumn script={SCRIPT_2} delayMs={2400} />
      </div>
    </div>
  );
}

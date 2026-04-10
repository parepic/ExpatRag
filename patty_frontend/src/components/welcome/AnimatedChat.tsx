"use client";

import { useEffect, useState } from "react";

type ChatMessage = {
  role: "user" | "patty";
  text: string;
};

const DIGID_SCRIPT: ChatMessage[] = [
  { role: "user", text: "Can you help me get started with my DigiD?" },
  {
    role: "patty",
    text: "Of course. DigiD is your digital identity for Dutch government services, and you will first need a BSN from your municipality.",
  },
  { role: "user", text: "How do I get a BSN number?" },
  {
    role: "patty",
    text: "You receive a BSN when you register with your local gemeente. Bring your passport and proof of your Dutch address.",
  },
  { role: "user", text: "What documents should I prepare?" },
  {
    role: "patty",
    text: "Usually a valid passport or ID, a registration form, and proof of address such as a rental contract or landlord letter.",
  },
];

const TAX_SCRIPT: ChatMessage[] = [
  { role: "user", text: "Am I eligible for the 30% ruling?" },
  {
    role: "patty",
    text: "It can apply if you were hired from abroad and meet the salary and distance requirements for the Dutch tax ruling.",
  },
  { role: "user", text: "What are the main requirements?" },
  {
    role: "patty",
    text: "You generally need qualifying expertise, to have lived far enough from the Dutch border, and to meet the minimum salary threshold.",
  },
  { role: "user", text: "How does my employer apply?" },
  {
    role: "patty",
    text: "Your employer applies with the Belastingdienst, ideally within the first four months, using your contract and supporting documents.",
  },
];

function ChatColumn({
  script,
  initialDelayMs,
}: {
  script: ChatMessage[];
  initialDelayMs: number;
}) {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;

    const schedule = (callback: () => void, delayMs: number) => {
      timeoutId = setTimeout(() => {
        if (!cancelled) {
          callback();
        }
      }, delayMs);
    };

    const runLoop = (nextIndex: number) => {
      if (nextIndex < script.length) {
        schedule(() => {
          setVisibleCount(nextIndex + 1);
          runLoop(nextIndex + 1);
        }, nextIndex === 0 ? initialDelayMs : 1800);
        return;
      }

      schedule(() => {
        setVisibleCount(0);
        runLoop(0);
      }, 3000);
    };

    runLoop(0);

    return () => {
      cancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [initialDelayMs, script]);

  return (
    <div className="flex flex-col gap-3">
      {script.map((message, index) => {
        const isVisible = index < visibleCount;
        const isUser = message.role === "user";

        return (
          <div
            key={`${message.role}-${index}`}
            className={[
              "flex transition-all duration-500",
              isUser ? "justify-end" : "justify-start",
              isVisible ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0",
            ].join(" ")}
          >
            <div
              className={[
                "max-w-[18rem] rounded-2xl px-4 py-2 text-sm leading-6 shadow-sm",
                isUser
                  ? "rounded-br-sm bg-primary text-primary-foreground"
                  : "rounded-bl-sm border border-border bg-card text-card-foreground",
              ].join(" ")}
            >
              {message.text}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function AnimatedChat() {
  return (
    <div
      className="pointer-events-none absolute inset-0 overflow-hidden"
      style={{ opacity: 0.18, filter: "blur(1.5px)" }}
    >
      <div className="flex h-full items-center justify-center">
        <div className="grid w-full max-w-5xl grid-cols-1 gap-8 px-6 md:grid-cols-2">
          <ChatColumn script={DIGID_SCRIPT} initialDelayMs={800} />
          <ChatColumn script={TAX_SCRIPT} initialDelayMs={2400} />
        </div>
      </div>
    </div>
  );
}

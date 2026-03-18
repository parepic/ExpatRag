"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isComplete } from "@/lib/profile";

type PageContext = "welcome" | "onboarding" | "chat";

export function useProfileGuard(context: PageContext) {
  const router = useRouter();

  useEffect(() => {
    const complete = isComplete();
    if (context === "onboarding" && complete) {
      router.push("/chat");
    } else if (context === "chat" && !complete) {
      router.push("/onboarding");
    }
    // welcome: no redirect — page handles its own CTA
  }, [context, router]);
}

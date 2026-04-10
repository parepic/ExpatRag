"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [tab, setTab] = useState<"login" | "register">("register");

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
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-16">
      <div className="w-full max-w-sm rounded-3xl border border-border bg-card p-8 shadow-md">
        {tab === "login" && (<p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          {"Welcome Back"}
        </p>)}
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">
          {tab === "login"
            ? "Sign in to continue"
            : "Create your Patty account"}
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          {tab === "login"
            ? "Pick up your chats and profile from any device with your existing account."
            : "Use a simple username and password to start saving your chats and profile."}
        </p>

        <Tabs
          value={tab}
          onValueChange={(value) => setTab(value as "login" | "register")}
          className="mt-8"
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="mt-8 rounded-2xl border border-dashed border-border/80 bg-muted/30 px-5 py-6">
          <p className="text-sm font-medium text-foreground">
            {tab === "login" ? "Sign in form next" : "Registration form next"}
          </p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Step 3 sets up the card and tabs. The actual form fields and submit
            handling are added in Step 4.
          </p>
        </div>
      </div>
    </main>
  );
}

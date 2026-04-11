"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { login, register, ApiError } from "@/lib/api/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [tab, setTab] = useState<"login" | "register">("register");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const trimmedUsername = username.trim();

    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsSubmitting(true);

    try {
      if (tab === "login") {
        await login(trimmedUsername, password);
        router.push("/chat");
        return;
      }

      await register(trimmedUsername, password);
      await login(trimmedUsername, password);
      router.push("/onboarding");
    } catch (caughtError) {
      if (caughtError instanceof ApiError) {
        if (tab === "register" && caughtError.status === 409) {
          setError("This username is already taken");
        } else {
          setError(caughtError.message);
        }
      } else {
        setError("Something went wrong");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-16">
      <div className="w-full max-w-sm rounded-3xl border border-border bg-card p-8 shadow-md">
        {tab === "login" && (
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
            Welcome Back
          </p>
        )}
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
          onValueChange={(value) => {
            setTab(value as "login" | "register");
            setError("");
          }}
          className="mt-8"
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
        </Tabs>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              autoFocus
              autoComplete="username"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                setError("");
              }}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete={tab === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError("");
              }}
              required
            />
          </div>

          <div className="pt-2">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting
                ? tab === "login"
                  ? "Signing In..."
                  : "Creating Account..."
                : tab === "login"
                  ? "Sign In"
                  : "Create Account"}
            </Button>
          </div>

          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </form>
      </div>
    </main>
  );
}

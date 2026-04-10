"use client";

import {
  createContext,
  useContext,
  useEffect,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import type { AuthUser } from "@/lib/types/user";

type AuthContextValue = {
  user: AuthUser;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) {
      console.log("[AuthContext] Checking session...");
      return;
    }

    if (user) {
      console.log("[AuthContext] Authenticated user:", user.username);
      return;
    }

    console.log("[AuthContext] No active session found.");
    console.log("[AuthContext] Redirecting to /login");
    router.push("/login");
  }, [isLoading, router, user]);

  if (isLoading) {
    return null;
  }

  if (!user) {
    return null;
  }

  return (
    <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>
  );
}

export function useAuthContext(): AuthContextValue {
  const value = useContext(AuthContext);

  if (!value) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }

  return value;
}

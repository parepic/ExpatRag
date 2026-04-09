"use client";

import { useEffect, useState } from "react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export interface AuthUser {
  id: string;
  username: string;
  [key: string]: unknown;
}

interface UseAuthResult {
  user: AuthUser | null;
  isLoading: boolean;
}

export function useAuth(): UseAuthResult {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;

    async function loadUser() {
      try {
        const response = await fetch(`${BACKEND_URL}/auth/me`, {
          credentials: "include",
        });

        if (!response.ok) {
          if (!isCancelled) {
            setUser(null);
            setIsLoading(false);
          }
          return;
        }

        const data = (await response.json()) as AuthUser;

        if (!isCancelled) {
          setUser(data);
          setIsLoading(false);
        }
      } catch {
        if (!isCancelled) {
          setUser(null);
          setIsLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      isCancelled = true;
    };
  }, []);

  return { user, isLoading };
}

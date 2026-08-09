"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { logout } from "@/lib/api/auth";

export function LogoutButton() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setErrorMessage("");
    setIsLoggingOut(true);

    try {
      await logout();
      router.replace("/login");
      router.refresh();
    } catch (caughtError) {
      setErrorMessage(
        caughtError instanceof Error ? caughtError.message : "Logout failed",
      );
      setIsLoggingOut(false);
    }
  }

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        onClick={handleLogout}
        disabled={isLoggingOut}
        className="w-full justify-start px-2 py-1.5 text-sm text-muted-foreground shadow-none transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      >
        <LogOut className="size-4" />
        {isLoggingOut ? "Logging out..." : "Log out"}
      </Button>

      {errorMessage ? (
        <p className="mt-1 px-2 text-xs text-destructive">{errorMessage}</p>
      ) : null}
    </>
  );
}

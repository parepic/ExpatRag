import { ApiError } from "@/lib/api/auth";
import type { UserProfile } from "@/lib/types/user";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export async function updateUser(
  fields: Partial<UserProfile>,
): Promise<void> {
  const res = await fetch(`${API_BASE}/users/me`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(fields),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Failed to update profile");
  }
}

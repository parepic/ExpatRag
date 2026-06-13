import { ApiError } from "@/lib/api/auth";
import type { UserProfile } from "@/lib/types/user";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export type NotificationSettings = {
  daily_news_email_enabled: boolean;
};

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

export async function getNotificationSettings(): Promise<NotificationSettings> {
  const res = await fetch(`${API_BASE}/users/notifications`, {
    credentials: "include",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.detail ?? "Failed to load notification settings",
    );
  }

  return res.json();
}

export async function updateNotificationSettings(
  settings: NotificationSettings,
): Promise<NotificationSettings> {
  const res = await fetch(`${API_BASE}/users/notifications`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(settings),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.detail ?? "Failed to update notification settings",
    );
  }

  return res.json();
}

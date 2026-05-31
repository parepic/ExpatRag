import { ApiError } from "@/lib/api/auth";
import type { ProjectSettings } from "@/lib/types/project-settings";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export async function updateProjectSettings(
  fields: Partial<ProjectSettings>,
): Promise<void> {
  const res = await fetch(`${API_BASE}/users/retrieval`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(fields),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Failed to update project settings");
  }
}

export async function getProjectSettings(): Promise<ProjectSettings> {
  const res = await fetch(`${API_BASE}/users/retrieval`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Failed to fetch project settings");
  }

  const data = await res.json().catch(() => ({} as ProjectSettings));
  return data as ProjectSettings;
}

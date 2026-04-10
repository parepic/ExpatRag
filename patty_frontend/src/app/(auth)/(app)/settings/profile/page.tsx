"use client";

import { PROFILE_FIELDS } from "@/lib/settings/profile-fields";

export default function SettingsProfilePage() {
  return (
    <main className="px-6 py-16">
      <div className="mx-auto w-full max-w-3xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Profile
        </p>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">
          Profile settings
        </h1>

        <div className="mt-10 space-y-3">
          {PROFILE_FIELDS.map((field) => (
            <div
              key={field.key}
              className="rounded-2xl border border-border bg-background px-4 py-3"
            >
              <p className="text-sm font-medium text-foreground">{field.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {field.type === "chip"
                  ? `${field.options?.length ?? 0} options`
                  : "Yes / No"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

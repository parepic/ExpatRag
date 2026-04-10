"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/context/AuthContext";
import { PROFILE_FIELDS } from "@/lib/settings/profile-fields";
import type { AuthUser, UserProfile } from "@/lib/types/user";

type ProfileDraft = Partial<UserProfile>;

function createDraftFromUser(user: AuthUser): ProfileDraft {
  return {
    nationality: user.nationality,
    purpose_of_stay: user.purpose_of_stay,
    employment_status: user.employment_status,
    registration_status: user.registration_status,
    has_fiscal_partner: user.has_fiscal_partner,
    salary_band: user.salary_band,
    age_bracket_under_30: user.age_bracket_under_30,
    prior_nl_residency: user.prior_nl_residency,
  };
}

function formatValue(value: string | boolean | null) {
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return value ?? "—";
}

export default function SettingsProfilePage() {
  const { user } = useAuthContext();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<ProfileDraft>(() => createDraftFromUser(user));

  return (
    <main className="px-6 py-16">
      <div className="mx-auto w-full max-w-3xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
              Profile
            </p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">
              Profile settings
            </h1>
          </div>

          <Button
            type="button"
            onClick={() => {
              setDraft(createDraftFromUser(user));
              setEditing(true);
            }}
          >
            Edit
          </Button>
        </div>

        {editing ? (
          <div className="mt-10 rounded-2xl border border-border bg-background px-4 py-3">
            <p className="text-sm text-muted-foreground">
              Edit mode is ready. The actual inputs come in the next step.
            </p>
          </div>
        ) : null}

        <div className="mt-10 space-y-3">
          {PROFILE_FIELDS.map((field) => {
            const value = user[field.key];

            return (
              <div
                key={field.key}
                className="rounded-2xl border border-border bg-background px-4 py-4"
              >
                <p className="text-sm font-medium text-foreground">{field.label}</p>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {formatValue(value)}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}

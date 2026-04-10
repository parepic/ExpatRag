"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/context/AuthContext";
import { updateUser } from "@/lib/api/users";
import { PROFILE_FIELDS } from "@/lib/settings/profile-fields";
import type { AuthUser, UserProfile, UserProfileKey } from "@/lib/types/user";

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
  const router = useRouter();
  const { user } = useAuthContext();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<ProfileDraft>(() => createDraftFromUser(user));
  const [profile, setProfile] = useState<ProfileDraft>(() => createDraftFromUser(user));
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    console.log("[settings/profile] AuthContext user changed:", user);
  }, [user]);

  useEffect(() => {
    if (editing) {
      return;
    }

    setProfile(createDraftFromUser(user));
  }, [editing, user]);

  function setField<K extends UserProfileKey>(key: K, value: UserProfile[K]) {
    setDraft((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function handleEdit() {
    setError("");
    setDraft(profile);
    setEditing(true);
  }

  function handleCancel() {
    setError("");
    setDraft(profile);
    setEditing(false);
  }

  async function handleSave() {
    setError("");
    setIsSaving(true);
    console.log("[settings/profile] AuthContext user before save:", user);

    try {
      await updateUser(draft);
      setProfile(draft);
      setEditing(false);
      console.log("[settings/profile] Save succeeded. AuthContext user after save:", user);
      router.refresh();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Failed to save profile",
      );
    } finally {
      setIsSaving(false);
    }
  }

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

          {editing ? (
            <div className="flex items-center gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button type="button" onClick={handleSave} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          ) : (
            <Button type="button" onClick={handleEdit}>
              Edit
            </Button>
          )}
        </div>

        {error ? <p className="mt-6 text-sm text-destructive">{error}</p> : null}

        <div className="mt-10 space-y-3">
          {PROFILE_FIELDS.map((field) => {
            const value = editing ? draft[field.key] ?? null : profile[field.key] ?? null;

            return (
              <div
                key={field.key}
                className="rounded-2xl border border-border bg-background px-4 py-4"
              >
                <p className="text-sm font-medium text-foreground">{field.label}</p>

                <div className="mt-3">
                  {editing ? (
                    field.type === "chip" ? (
                      <ChipSelect
                        options={field.options ?? []}
                        value={(value as string | null) ?? null}
                        onChange={(nextValue) =>
                          setField(
                            field.key,
                            nextValue as UserProfile[typeof field.key],
                          )
                        }
                      />
                    ) : (
                      <YesNoToggle
                        value={(value as boolean | null) ?? null}
                        onChange={(nextValue) =>
                          setField(
                            field.key,
                            nextValue as UserProfile[typeof field.key],
                          )
                        }
                      />
                    )
                  ) : (
                    <p className="text-sm leading-6 text-muted-foreground">
                      {formatValue(value)}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}

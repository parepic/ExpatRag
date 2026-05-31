"use client";

import { useEffect, useState } from "react";

import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/context/AuthContext";
import { updateUser } from "@/lib/api/users";
import { USER_SETTINGS_FIELDS } from "@/lib/settings/profile-fields";
import type { AuthUser, UserProfile, UserProfileKey } from "@/lib/types/user";

type UserSettingsDraft = Partial<UserProfile>;

function createUserSettingsDraft(user: AuthUser): UserSettingsDraft {
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

function formatSettingValue(value: string | boolean | null) {
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return value ?? "—";
}

export default function UserSettingsPage() {
  const { user } = useAuthContext();
  const [isEditing, setIsEditing] = useState(false);
  const [draftSettings, setDraftSettings] = useState<UserSettingsDraft>(() =>
    createUserSettingsDraft(user),
  );
  const [savedSettings, setSavedSettings] = useState<UserSettingsDraft>(() =>
    createUserSettingsDraft(user),
  );
  const [errorMessage, setErrorMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    console.log("[settings/user] AuthContext user changed:", user);
  }, [user]);

  useEffect(() => {
    setSavedSettings(createUserSettingsDraft(user));
  }, [user]);

  function setSettingValue<K extends UserProfileKey>(
    key: K,
    value: UserProfile[K],
  ) {
    setDraftSettings((currentSettings) => ({
      ...currentSettings,
      [key]: value,
    }));
  }

  function handleEdit() {
    setErrorMessage("");
    setDraftSettings(savedSettings);
    setIsEditing(true);
  }

  function handleCancel() {
    setErrorMessage("");
    setDraftSettings(savedSettings);
    setIsEditing(false);
  }

  async function handleSave() {
    setErrorMessage("");
    setIsSaving(true);
    console.log("[settings/user] AuthContext user before save:", user);

    try {
      await updateUser(draftSettings);
      setSavedSettings(draftSettings);
      setIsEditing(false);
      console.log(
        "[settings/user] Save succeeded. AuthContext user after save:",
        user,
      );
      window.location.reload();
    } catch (caughtError) {
      setErrorMessage(
        caughtError instanceof Error
          ? caughtError.message
          : "Failed to save user settings",
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
              User
            </p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground">
              User settings
            </h1>
          </div>

          {isEditing ? (
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

        {errorMessage ? (
          <p className="mt-6 text-sm text-destructive">{errorMessage}</p>
        ) : null}

        <div className="mt-10 space-y-3">
          {USER_SETTINGS_FIELDS.map((field) => {
            const currentValue = isEditing
              ? (draftSettings[field.key] ?? null)
              : (savedSettings[field.key] ?? null);

            return (
              <div
                key={field.key}
                className="rounded-2xl border border-border bg-background px-4 py-4"
              >
                <p className="text-sm font-medium text-foreground">
                  {field.label}
                </p>

                <div className="mt-3">
                  {isEditing ? (
                    field.type === "chip" ? (
                      <ChipSelect
                        options={field.options ?? []}
                        value={(currentValue as string | null) ?? null}
                        onChange={(nextValue) =>
                          setSettingValue(
                            field.key,
                            nextValue as UserProfile[typeof field.key],
                          )
                        }
                      />
                    ) : (
                      <YesNoToggle
                        value={(currentValue as boolean | null) ?? null}
                        onChange={(nextValue) =>
                          setSettingValue(
                            field.key,
                            nextValue as UserProfile[typeof field.key],
                          )
                        }
                      />
                    )
                  ) : (
                    <p className="text-sm leading-6 text-muted-foreground">
                      {formatSettingValue(currentValue)}
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

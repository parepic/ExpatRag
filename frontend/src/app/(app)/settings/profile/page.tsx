"use client";

import { useState } from "react";
import { getField, setField } from "@/lib/profile";
import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { LanguageCombobox } from "@/components/onboarding/LanguageCombobox";
import { NATIONALITY_OPTIONS } from "@/lib/constants/nationality-options";
import { PURPOSE_OPTIONS } from "@/lib/constants/purpose-types";
import { OCCUPATION_OPTIONS } from "@/lib/constants/occupation-types";
import { REGISTRATION_OPTIONS } from "@/lib/constants/registration-status";
import { HOUSING_OPTIONS } from "@/lib/constants/housing-options";
import { SALARY_BANDS } from "@/lib/constants/salary-bands";
import { RESIDENCY_OPTIONS } from "@/lib/constants/residency-options";
import { Button } from "@/components/ui/button";

interface FieldDef {
  key: string;
  label: string;
  type: "chip" | "yesno" | "language";
  options?: readonly string[];
}

const FIELDS: FieldDef[] = [
  { key: "nationality", label: "Nationality / citizenship", type: "chip", options: NATIONALITY_OPTIONS },
  { key: "purpose_of_stay", label: "Purpose of stay", type: "chip", options: PURPOSE_OPTIONS },
  { key: "employment_situation", label: "Employment situation", type: "chip", options: OCCUPATION_OPTIONS },
  { key: "registration_status", label: "Registration / BSN status", type: "chip", options: REGISTRATION_OPTIONS },
  { key: "has_fiscal_partner", label: "Fiscal partner?", type: "yesno" },
  { key: "housing_situation", label: "Housing situation", type: "chip", options: HOUSING_OPTIONS },
  { key: "salary_band", label: "Gross annual salary", type: "chip", options: SALARY_BANDS },
  { key: "age_bracket", label: "Under 30?", type: "yesno" },
  { key: "prior_nl_residency", label: "Prior NL residency", type: "chip", options: RESIDENCY_OPTIONS },
  { key: "languages", label: "Languages spoken", type: "language" },
];

function loadValues(): Record<string, string | string[]> {
  const vals: Record<string, string | string[]> = {};
  FIELDS.forEach(({ key }) => {
    const raw = getField(key as any);
    if (raw === null) return;
    try { vals[key] = JSON.parse(raw); }
    catch { vals[key] = raw; }
  });
  return vals;
}

export function displayValue(key: string, val: string | string[] | undefined): string {
  if (val === undefined || val === null) return "—";
  if (Array.isArray(val)) return val.length > 0 ? val.join(", ") : "—";
  if (key === "age_bracket") {
    if (val === "under_30") return "Under 30";
    if (val === "30_or_older") return "30 or older";
  }
  return val;
}

export function toYesNo(key: string, val: string | string[] | undefined): "yes" | "no" | null {
  if (typeof val !== "string") return null;
  if (key === "age_bracket") {
    if (val === "under_30") return "yes";
    if (val === "30_or_older") return "no";
    // legacy "yes"/"no" stored before fix
    if (val === "yes" || val === "no") return val;
    return null;
  }
  if (val === "yes" || val === "no") return val;
  return null;
}

export function fromYesNo(key: string, v: string): string {
  if (key === "age_bracket") return v === "yes" ? "under_30" : "30_or_older";
  return v;
}

export default function ProfilePage() {
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(loadValues);
  const [draft, setDraft] = useState(saved);

  function handleEdit() {
    setDraft(saved);
    setEditing(true);
  }

  function handleSave() {
    FIELDS.forEach(({ key }) => {
      const val = draft[key];
      if (val !== undefined) {
        setField(key as any, Array.isArray(val) ? JSON.stringify(val) : String(val));
      }
    });
    setSaved(draft);
    setEditing(false);
  }

  function handleCancel() {
    setDraft(saved);
    setEditing(false);
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-foreground">Profile</h1>
        {!editing ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleEdit}
            className="h-auto px-0 py-0 text-sm text-primary shadow-none hover:bg-transparent hover:text-primary/80"
          >
            Edit
          </Button>
        ) : (
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              size="sm"
            >
              Save
            </Button>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {FIELDS.map(({ key, label, type, options }) => (
          <div key={key} className="border-b border-border pb-5">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
            {!editing ? (
              <p className="text-sm text-foreground">{displayValue(key, saved[key])}</p>
            ) : (
              <div>
                {type === "chip" && (
                  <ChipSelect
                    options={options!}
                    value={(draft[key] as string) ?? null}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
                  />
                )}
                {type === "yesno" && (
                  <YesNoToggle
                    value={toYesNo(key, draft[key])}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: fromYesNo(key, v) }))}
                  />
                )}
                {type === "language" && (
                  <LanguageCombobox
                    value={(draft[key] as string[]) ?? []}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

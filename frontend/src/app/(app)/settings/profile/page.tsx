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

  function displayValue(key: string, val: string | string[] | undefined): string {
    if (val === undefined || val === null) return "—";
    if (Array.isArray(val)) return val.length > 0 ? val.join(", ") : "—";
    return val;
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-[--color-text]">Profile</h1>
        {!editing ? (
          <button
            onClick={handleEdit}
            className="text-sm text-[--color-accent] hover:underline"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-3">
            <button onClick={handleCancel} className="text-sm text-[--color-text-muted] hover:text-[--color-text]">
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="text-sm px-4 py-1.5 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white rounded-[--radius] transition-colors"
            >
              Save
            </button>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {FIELDS.map(({ key, label, type, options }) => (
          <div key={key} className="border-b border-[--color-border] pb-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted] mb-2">{label}</p>
            {!editing ? (
              <p className="text-sm text-[--color-text]">{displayValue(key, saved[key])}</p>
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
                    value={(draft[key] as "yes" | "no") ?? null}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
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

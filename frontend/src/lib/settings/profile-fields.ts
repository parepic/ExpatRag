import type { UserProfileKey } from "@/lib/types/user";
import {
  EMPLOYMENT_STATUS_OPTIONS,
  NATIONALITY_OPTIONS,
  PURPOSE_OF_STAY_OPTIONS,
  REGISTRATION_STATUS_OPTIONS,
  SALARY_BANDS,
} from "@/lib/constants";

export type ProfileField = {
  key: UserProfileKey;
  label: string;
  type: "chip" | "yesno";
  options?: readonly string[];
};

export const PROFILE_FIELDS: ProfileField[] = [
  {
    key: "nationality",
    label: "Nationality / citizenship",
    type: "chip",
    options: NATIONALITY_OPTIONS,
  },
  {
    key: "purpose_of_stay",
    label: "Purpose of stay",
    type: "chip",
    options: PURPOSE_OF_STAY_OPTIONS,
  },
  {
    key: "employment_status",
    label: "Employment situation",
    type: "chip",
    options: EMPLOYMENT_STATUS_OPTIONS,
  },
  {
    key: "registration_status",
    label: "Registration / BSN status",
    type: "chip",
    options: REGISTRATION_STATUS_OPTIONS,
  },
  {
    key: "has_fiscal_partner",
    label: "Fiscal partner?",
    type: "yesno",
  },
  {
    key: "salary_band",
    label: "Gross annual salary",
    type: "chip",
    options: SALARY_BANDS,
  },
  {
    key: "age_bracket_under_30",
    label: "Under 30?",
    type: "yesno",
  },
  {
    key: "prior_nl_residency",
    label: "Prior NL residency?",
    type: "yesno",
  },
];

import type { User } from "@/lib/types/user";
import {
  EMPLOYMENT_STATUS_OPTIONS,
  NATIONALITY_OPTIONS,
  PURPOSE_OF_STAY_OPTIONS,
  REGISTRATION_STATUS_OPTIONS,
  SALARY_BANDS,
} from "@/lib/constants";

export type OnboardingQuestion = {
  key: keyof User;
  label: string;
  sublabel?: string;
  type: "chip" | "yesno";
  options?: readonly string[];
};

export const ONBOARDING_QUESTIONS: OnboardingQuestion[] = [
  {
    key: "nationality",
    label: "What is your nationality / citizenship status?",
    type: "chip",
    options: NATIONALITY_OPTIONS,
  },
  {
    key: "purpose_of_stay",
    label: "What is your main reason for coming to the Netherlands?",
    type: "chip",
    options: PURPOSE_OF_STAY_OPTIONS,
  },
  {
    key: "employment_status",
    label: "What is your employment situation?",
    type: "chip",
    options: EMPLOYMENT_STATUS_OPTIONS,
  },
  {
    key: "registration_status",
    label: "What is your current registration status in the Netherlands?",
    type: "chip",
    options: REGISTRATION_STATUS_OPTIONS,
  },
  {
    key: "has_fiscal_partner",
    label: "Do you have a fiscal (registered) partner?",
    sublabel:
      "Married, registered partnership, or cohabiting at the same address.",
    type: "yesno",
  },
  {
    key: "salary_band",
    label: "What is your gross annual salary (or expected income)?",
    type: "chip",
    options: SALARY_BANDS,
  },
  {
    key: "age_bracket_under_30",
    label: "Are you under 30 years old?",
    sublabel: "This affects eligibility for the HSM permit and 30% ruling.",
    type: "yesno",
  },
  {
    key: "prior_nl_residency",
    label: "Have you previously lived in the Netherlands?",
    type: "yesno",
  },
];

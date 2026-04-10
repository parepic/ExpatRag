import type {
  EMPLOYMENT_STATUS_OPTIONS,
  NATIONALITY_OPTIONS,
  PURPOSE_OF_STAY_OPTIONS,
  REGISTRATION_STATUS_OPTIONS,
  SALARY_BANDS,
} from "@/lib/constants";

type Nationality = (typeof NATIONALITY_OPTIONS)[number];
type PurposeOfStay = (typeof PURPOSE_OF_STAY_OPTIONS)[number];
type EmploymentStatus = (typeof EMPLOYMENT_STATUS_OPTIONS)[number];
type RegistrationStatus = (typeof REGISTRATION_STATUS_OPTIONS)[number];
type SalaryBand = (typeof SALARY_BANDS)[number];

export type User = {
  id: string;
  username: string;
  created_at: string;
  nationality: Nationality | null;
  purpose_of_stay: PurposeOfStay | null;
  employment_status: EmploymentStatus | null;
  registration_status: RegistrationStatus | null;
  has_fiscal_partner: boolean | null;
  salary_band: SalaryBand | null;
  age_bracket_under_30: boolean | null;
  prior_nl_residency: boolean | null;
};

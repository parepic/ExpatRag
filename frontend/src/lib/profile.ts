export const REQUIRED_FIELDS = [
  "nationality",
  "purpose_of_stay",
  "employment_situation",
  "registration_status",
  "has_fiscal_partner",
  "housing_situation",
  "salary_band",
  "age_bracket",
  "prior_nl_residency",
] as const;

export type ProfileKey = (typeof REQUIRED_FIELDS)[number] | "languages";

let inMemoryFallback: Record<string, string> = {};
let useInMemory = false;

function getStorage(): Pick<Storage, "getItem" | "setItem"> | null {
  if (useInMemory) return null;
  try {
    localStorage.setItem("__test__", "1");
    localStorage.removeItem("__test__");
    return localStorage;
  } catch {
    useInMemory = true;
    return null;
  }
}

export function getField(key: ProfileKey): string | null {
  const storage = getStorage();
  if (!storage) return inMemoryFallback[key] ?? null;
  return storage.getItem(key);
}

export function setField(key: ProfileKey, value: string): void {
  const storage = getStorage();
  if (!storage) {
    inMemoryFallback[key] = value;
    return;
  }
  storage.setItem(key, value);
}

export function isComplete(): boolean {
  return REQUIRED_FIELDS.every((key) => {
    const value = getField(key);
    return value !== null && value.trim() !== "";
  });
}

export function getMissingFields(): typeof REQUIRED_FIELDS[number][] {
  return REQUIRED_FIELDS.filter((key) => {
    const value = getField(key);
    return value === null || value.trim() === "";
  });
}

export function isStorageAvailable(): boolean {
  return !useInMemory;
}

# Onboarding Flow (`/onboarding`)

## Purpose

After registration, users are directed here to provide personal details so Patty can personalize answers to their specific situation. The onboarding collects exactly the profile fields defined in the `User` type — nationality, purpose of stay, employment status, etc.

Onboarding is skippable. The app works without profile data, answers just won't be personalized. Users can always fill in or update their profile later via `/settings/profile`.

---

## Features

### Wizard-style question flow

- One question per screen, presented in a centered card.
- Users advance with a "Next" button (or "Finish" on the last question).
- Back and Forward navigation buttons above the card let users revisit answered questions.
- Progress is shown via dots below the card indicating how many questions have been answered.
- Animated transitions between questions (slide left/right depending on direction) using framer-motion.

### Questions

Each question maps to a `User` profile field. The question order and types:

| # | Field | Question | Type |
|---|---|---|---|
| 1 | `nationality` | What is your nationality / citizenship status? | Chip select (`NATIONALITY_OPTIONS`) |
| 2 | `purpose_of_stay` | What is your main reason for coming to the Netherlands? | Chip select (`PURPOSE_OF_STAY_OPTIONS`) |
| 3 | `employment_status` | What is your employment situation? | Chip select (`EMPLOYMENT_STATUS_OPTIONS`) |
| 4 | `registration_status` | What is your current registration status in the Netherlands? | Chip select (`REGISTRATION_STATUS_OPTIONS`) |
| 5 | `has_fiscal_partner` | Do you have a fiscal (registered) partner? | Yes/No toggle |
| 6 | `salary_band` | What is your gross annual salary (or expected income)? | Chip select (`SALARY_BANDS`) |
| 7 | `age_bracket_under_30` | Are you under 30 years old? | Yes/No toggle |
| 8 | `prior_nl_residency` | Have you previously lived in the Netherlands? | Yes/No toggle |

Sublabels for context where needed:
- `has_fiscal_partner`: "Married, registered partnership, or cohabiting at the same address."
- `age_bracket_under_30`: "This affects eligibility for the HSM permit and 30% ruling."

### Skip and completion

- A "Skip" link is visible on every question, positioned below the navigation or near the card. Clicking it skips the entire onboarding and redirects to `/chat`.
- On the last question, the "Next" button changes to "Finish".
- After finishing, show a completion card with a message ("You're all set!") and a button to start chatting that navigates to `/chat`.

### Saving answers

- Each answer is saved to the backend immediately when the user advances to the next question (not batched at the end). This way, partial completion is preserved if the user abandons the flow.
- Calls `PATCH /users/me` with the single field that was just answered.
- For boolean questions (yes/no toggle), the value sent is `true` or `false`.
- For chip select questions, the value sent is the selected string.

### Auth-protected

- This page lives inside the `(auth)` route group, so `AuthContext` handles the redirect to `/login` if the user is not authenticated.
- The user object from `AuthContext` is available to pre-fill answers if the user returns to onboarding with some fields already set.

---

## Implementation steps

### Files to create

| File | Purpose |
|---|---|
| `src/app/(auth)/onboarding/page.tsx` | Onboarding wizard page (Client Component) — replaces the current scaffold |
| `src/components/onboarding/ChipSelect.tsx` | Single-select chip grid component |
| `src/components/onboarding/YesNoToggle.tsx` | Yes / No toggle component |
| `src/components/onboarding/ProgressDots.tsx` | Progress indicator dots |
| `src/components/onboarding/QuestionCard.tsx` | Animated card wrapper with framer-motion transitions |
| `src/lib/api/users.ts` | API call function: `updateUser()` |

### Dependencies to install

```bash
pnpm add framer-motion
```

### Step 1: Create the API call function

Create `src/lib/api/users.ts` with a function to update the user's profile. Reuses `ApiError` from `auth.ts`.

```ts
import { ApiError } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export async function updateUser(
  fields: Record<string, string | boolean | null>,
): Promise<void> {
  const res = await fetch(`${API_BASE}/users/me`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(fields),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Failed to update profile");
  }
}
```

### Step 2: Create the onboarding UI components

Build the four reusable components in `src/components/onboarding/`. These follow the same patterns as the old `frontend/` onboarding components:

**`ChipSelect.tsx`** — renders a grid of option chips. Props: `options: readonly string[]`, `value: string | null`, `onChange: (value: string) => void`. The selected chip gets a distinct style (e.g. `bg-primary text-primary-foreground`), others are outlined.

**`YesNoToggle.tsx`** — two large buttons side by side: "Yes" and "No". Props: `value: boolean | null`, `onChange: (value: boolean) => void`. Maps `true`/`false` to the toggle state.

**`ProgressDots.tsx`** — a row of small dots. Props: `total: number`, `current: number` (answered count). Filled dots up to `current`, empty dots for the rest.

**`QuestionCard.tsx`** — a wrapper that animates its children in/out on question change. Props: `direction: "forward" | "back"`, `children`. Uses framer-motion `motion.div` with slide + fade variants keyed by question index.

### Step 3: Define the question list

In the page file, define the questions as a typed array:

```ts
interface Question {
  key: keyof User;
  label: string;
  sublabel?: string;
  type: "chip" | "yesno";
  options?: readonly string[];
}
```

Each question's `key` matches the `User` type field name exactly, so the answer can be sent directly to `PATCH /users/me` as `{ [question.key]: value }`.

### Step 4: Page shell and state

Set up `src/app/(auth)/onboarding/page.tsx` as a Client Component (`"use client"`):

- Get `user` from `AuthContext` (available because this page is inside the `(auth)` route group).
- State: `stepIndex` (current question), `direction` ("forward" | "back"), `answers` (record of field → value), `completed` (boolean).
- On mount, pre-fill `answers` from the `user` object for any fields that are already set. Start `stepIndex` at the first unanswered question.

### Step 5: Navigation and submission logic

- **Next / Finish button:** Save the current answer to the backend (`updateUser({ [key]: value })`), then advance to the next question or show completion.
- **Back button:** Move to the previous question (no API call — the answer was already saved).
- **Forward button:** Move to the next question if it has been answered before (no API call).
- **Skip link:** Navigate directly to `/chat` without saving.

### Step 6: Render the wizard

Assemble the page:

1. Back / Forward buttons above the card.
2. `<AnimatePresence>` wrapping a `<QuestionCard>` keyed by `stepIndex`.
3. Inside the card: question label, optional sublabel, the appropriate input component (`ChipSelect` or `YesNoToggle`), and the Next/Finish button.
4. `<ProgressDots>` below the card.
5. Skip link below the dots.

### Step 7: Completion screen

When `completed` is true, render a simple centered card:

- A heading ("You're all set!").
- A subtitle ("We've saved your details and will use them to give you personalised advice.").
- A button ("Start chatting with Patty") that navigates to `/chat`.

### Step 8: Verify

- Run `pnpm dev` and navigate to `/onboarding` (must be logged in).
- Confirm all 8 questions render with the correct input type.
- Confirm answers are saved to the backend on each "Next" (check via `GET /auth/me`).
- Confirm Back/Forward navigation works without re-saving.
- Confirm pre-fill works if the user already has profile data.
- Confirm "Skip" redirects to `/chat` without saving.
- Confirm the completion screen appears after the last question.
- Check on a narrow viewport (~375px) that chips wrap and the card is usable.

# Onboarding Flow (`/onboarding`)

## Purpose

After registration, users are directed here to provide personal details so Patty can personalize answers to their specific situation. The onboarding collects exactly the profile fields defined in the `User` type — nationality, purpose of stay, employment status, etc.

Onboarding is skippable. The app works without profile data, answers just won't be personalized. Users can always fill in or update their profile later via `/settings/profile`.

---

## Features

### Wizard-style question flow

- One question per screen, presented in a centered card.
- Users advance with a "Next" button (or "Finish" on the last question). "Next" is always enabled — users can leave a question blank and move on.
- A "Back" button above the card lets users go back to the previous question.
- Progress is shown via dots below the card indicating the current step position.
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

### Skip

- A "Skip onboarding" link is visible on every question, positioned below the progress dots.
- Clicking it navigates to `/chat` immediately — nothing is saved.

### Saving answers

- All answers are collected in local component state as the user progresses through questions.
- On "Finish" (last question), a single `PATCH /users/me` call sends all answered fields at once. Only fields that were actually answered are included in the payload — unanswered fields are omitted.
- For boolean questions (yes/no toggle), the value sent is `true` or `false`.
- For chip select questions, the value sent is the selected string.

### Completion

- After a successful save, show a completion card with a message ("You're all set!") that automatically redirects to `/chat` after 3 seconds.

### Auth-protected

- This page lives inside the `(auth)` route group, so `AuthContext` handles the redirect to `/login` if the user is not authenticated.

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

Create `src/lib/api/users.ts` with a function to update the user's profile. It calls `PATCH /users/me` with `credentials: "include"` and sends the fields as JSON. Reuses `ApiError` from `auth.ts` for error handling.

### Step 2: Create the onboarding UI components

Build the four reusable components in `src/components/onboarding/`. These follow the same patterns as the old `frontend/` onboarding components:

**`ChipSelect.tsx`** — renders a grid of option chips. Props: `options` (the constants array), `value` (selected string or null), `onChange` callback. The selected chip gets a distinct style (e.g. `bg-primary text-primary-foreground`), others are outlined.

**`YesNoToggle.tsx`** — two large buttons side by side: "Yes" and "No". Props: `value` (boolean or null), `onChange` callback. Maps `true`/`false` to the toggle state.

**`ProgressDots.tsx`** — a row of small dots. Props: `total` (number of questions), `current` (current step index). Highlights the current dot and fills dots for visited steps.

**`QuestionCard.tsx`** — a wrapper that animates its children in/out on question change. Props: `direction` ("forward" or "back"), `children`. Uses framer-motion with slide + fade variants keyed by question index.

### Step 3: Define the question list

In the page file, define the questions as a typed array. Each entry has a `key` (matching the `User` field name exactly), a `label`, an optional `sublabel`, a `type` ("chip" or "yesno"), and for chip questions, the `options` constants array.

### Step 4: Page shell and state

Set up `src/app/(auth)/onboarding/page.tsx` as a Client Component:

- State: `stepIndex` (current question, starts at 0), `direction` ("forward" or "back"), `answers` (record of field key → value), `completed` (boolean).
- No pre-filling — this is a fresh linear flow every time.

### Step 5: Navigation and submission logic

- **Next button:** Advance to the next question. Always enabled — if the user didn't answer, just move on.
- **Finish button (last question):** Collect all answered fields from state, send a single `PATCH /users/me`, and on success set `completed` to true.
- **Back button:** Move to the previous question. Disabled on the first question.
- **Skip link:** Navigate directly to `/chat` without saving.

### Step 6: Render the wizard

Assemble the page:

1. Back button above the card (disabled on first question).
2. `<AnimatePresence>` wrapping a `<QuestionCard>` keyed by `stepIndex`.
3. Inside the card: question label, optional sublabel, the appropriate input component (`ChipSelect` or `YesNoToggle`), and the Next/Finish button.
4. `<ProgressDots>` below the card.
5. "Skip onboarding" link below the dots.

### Step 7: Completion screen

When `completed` is true, render a simple centered card:

- A heading ("You're all set!").
- A subtitle ("We've saved your details and will use them to give you personalised advice.").
- After 3 seconds, automatically redirect to `/chat`. No button needed.

### Step 8: Verify

- Run `pnpm dev` and navigate to `/onboarding` (must be logged in).
- Confirm all 8 questions render with the correct input type.
- Confirm "Next" works even when no answer is selected.
- Confirm "Back" navigates to the previous question and preserves the answer.
- Confirm "Finish" sends a single API call with all answered fields (check via `GET /auth/me`).
- Confirm "Skip onboarding" redirects to `/chat` without any API call.
- Confirm the completion screen appears after finishing and auto-redirects to `/chat` after 3 seconds.
- Check on a narrow viewport (~375px) that chips wrap and the card is usable.

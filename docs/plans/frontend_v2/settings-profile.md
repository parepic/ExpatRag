# Settings & Profile (`/settings/profile`)

## Purpose

This is where users view and edit the personal details they provided during onboarding (or skipped). The same profile fields that personalize Patty's answers are displayed here in a single scrollable page with a view/edit toggle. Saving sends the updated fields to the backend.

---

## Features

### View mode (default)

- All 8 profile fields are listed vertically, each showing a label and the current value.
- Fields that were never filled in show a dash ("—").
- An "Edit" button at the top-right switches to edit mode.

### Edit mode

- Each field becomes editable using the same input components from onboarding:
  - `ChipSelect` for text fields (`nationality`, `purpose_of_stay`, `employment_status`, `registration_status`, `salary_band`).
  - `YesNoToggle` for boolean fields (`has_fiscal_partner`, `age_bracket_under_30`, `prior_nl_residency`).
- "Save" and "Cancel" buttons replace the "Edit" button.
- **Save:** Collects all field values from the draft state, sends a single `PATCH /users/me` with the changed fields, and switches back to view mode on success. Shows an error message if the request fails.
- **Cancel:** Discards all edits and switches back to view mode.

### Profile fields

The fields and their order match the onboarding flow:

| # | Field | Label | Input type |
|---|---|---|---|
| 1 | `nationality` | Nationality / citizenship | Chip select (`NATIONALITY_OPTIONS`) |
| 2 | `purpose_of_stay` | Purpose of stay | Chip select (`PURPOSE_OF_STAY_OPTIONS`) |
| 3 | `employment_status` | Employment situation | Chip select (`EMPLOYMENT_STATUS_OPTIONS`) |
| 4 | `registration_status` | Registration / BSN status | Chip select (`REGISTRATION_STATUS_OPTIONS`) |
| 5 | `has_fiscal_partner` | Fiscal partner? | Yes/No toggle |
| 6 | `salary_band` | Gross annual salary | Chip select (`SALARY_BANDS`) |
| 7 | `age_bracket_under_30` | Under 30? | Yes/No toggle |
| 8 | `prior_nl_residency` | Prior NL residency? | Yes/No toggle |

### Data source

- The current profile values come from the `user` object in `AuthContext` (populated by `GET /auth/me`).
- After a successful save, the local view updates immediately from the draft state. Optionally refresh the `user` in `AuthContext` so the rest of the app sees the updated profile.

### Auth-protected

- This page lives inside the `(auth)/(app)` route group, so `AuthContext` handles the redirect to `/login` if the user is not authenticated.

---

## Implementation steps

### Files to create

| File | Purpose |
|---|---|
| `src/app/(auth)/(app)/settings/profile/page.tsx` | Profile view/edit page (Client Component) — replaces the current scaffold |

This page reuses components already created during onboarding (`ChipSelect`, `YesNoToggle`) and the API function from `src/lib/api/users.ts` (`updateUser`). No new shared files needed.

### Step 1: Define the field list

In the page file, define the profile fields as an array matching the `User` type. Each entry has a `key` (matching the `User` field name), a `label` (display text), a `type` ("chip" or "yesno"), and for chip fields, the `options` constants array. This is the same pattern as the onboarding question list, just without labels phrased as questions.

### Step 2: View mode

Set up the page as a Client Component. Read `user` from `AuthContext`.

- State: `editing` (boolean, starts false), `draft` (record of field values, copied from `user` when entering edit mode).
- In view mode, render each field as a label + value pair. For boolean fields, display "Yes" / "No" / "—". For text fields, display the value or "—" if null.
- An "Edit" button at the top-right sets `editing = true` and copies the current user profile values into `draft`.

### Step 3: Edit mode

When `editing` is true:

- Replace each field's value display with the corresponding input component (`ChipSelect` or `YesNoToggle`), pre-filled from `draft`.
- Changes update `draft` state (not the user object directly).
- "Cancel" button resets `draft` and sets `editing = false`.
- "Save" button calls `updateUser(draft)` with all fields from the draft. On success, set `editing = false`. On failure, show an error message.
- For debugging, log the `user` from `useAuthContext()` before and after save (or in a `useEffect` watching `user`) to confirm whether the shared auth-context user actually changes after a successful `PATCH /users/me`.

### Step 4: Verify

- Run `pnpm dev` and navigate to `/settings/profile` (must be logged in).
- Confirm all 8 fields display with their current values (or "—" if empty).
- Click "Edit" — confirm all fields become editable with the correct input type.
- Change some values and click "Save" — confirm the changes persist (reload the page or check via `GET /auth/me`).
- Check the debug logs around save and confirm whether the `user` from `AuthContext` changes or stays stale after saving.
- Change some values and click "Cancel" — confirm the original values are restored.
- Confirm the sidebar shows "Back to Patty" link and "Profile" nav item.
- Check on a narrow viewport (~375px) that the layout is usable.

**Reference:** The old frontend's profile page at `frontend/src/app/(app)/settings/profile/page.tsx` has the same view/edit toggle pattern and styling. Carry over the visual design — the only change is that save calls `PATCH /users/me` instead of writing to localStorage.

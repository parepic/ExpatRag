# UI Bug Fixes — Expat Compliance Copilot (Patty)

**Date:** 2026-03-18
**Status:** Approved

---

## Overview

A sequential, one-issue-at-a-time bug fix pass on the Patty frontend. Issues are resolved in priority order. Each issue is confirmed fixed by the user before moving to the next.

---

## Root Cause Analysis

**Root Cause A — CSS variable conflict (`--color-accent`):**
`globals.css` has an `@theme inline` block that includes `--color-accent: var(--accent)`. In Tailwind v4, `@theme inline` tokens always take precedence over bare `:root` declarations for utility class resolution — so `bg-[--color-accent]` resolves against the `@theme inline` token (`var(--accent)` = `oklch(0.97 0 0)`, near-white), not against the Patty Theme's `:root { --color-accent: #2f6ef7 }` defined later in the file. This causes all elements using `bg-[--color-accent] text-white` to render as white text on a near-white background (invisible). The fix is to remove `--color-accent` from the `@theme inline` block, leaving the Patty Theme `:root` value as the sole definition.

**Root Cause B — localStorage fields appearing unsaved:**
The user reports only `languages` is saved to localStorage. All profile fields are saved via `handleSubmit()` in `onboarding/page.tsx`, called when the "Next/Finish" button is clicked. The "Next/Finish" button is visually invisible due to Root Cause A (white text on near-white background), but it is still in the DOM and potentially clickable by position. Whether Root Cause A fully explains the missing fields or there is an additional independent bug should be confirmed after Issue 1 is fixed. If fixing Root Cause A allows the user to complete the flow, Issue 2 (auto-advance) will also ensure `handleSubmit()` fires reliably on every step.

---

## Fix Order

### Issue 1: CSS variable conflict — buttons unreadable and AnimatedChat invisible

**Problem:** `bg-[--color-accent]` likely resolves to near-white instead of Patty blue (`#2f6ef7`), making all accent-colored buttons render as white text on a near-white background (invisible). Also affects `AnimatedChat` user bubbles (which are intentionally semi-transparent and blurred, so even with the correct color they remain subtle). Affected elements: "Get Started" button, onboarding "Next/Finish" button, selected chip buttons, "Start chatting with Patty" button.

**Scope:**
- `src/app/globals.css` — remove `--color-accent` from the `@theme inline` block so the Patty Theme `:root { --color-accent: #2f6ef7 }` is the only definition. Verify no other Patty theme variables (`--color-text`, `--color-text-muted`, `--color-bg`, `--color-bg-subtle`, `--color-border`, `--color-accent-hover`) are aliased in `@theme inline` in a way that conflicts.

**Done when:** All accent-colored buttons show readable white text on a blue background. On the welcome page, `AnimatedChat` user bubbles render with a blue (not near-white) tint, while remaining intentionally blurred and semi-transparent as background decoration.

---

### Issue 2: No auto-advance after chip/toggle selection

**Problem:** Selecting a chip or yes/no option calls `onChange` → `setAnswer()` (React state only). It does not automatically call `handleSubmit()` or advance to the next step. Per spec, selection should auto-advance after a short pause.

**Scope:**
- `src/components/onboarding/ChipSelect.tsx` — add an optional `onAutoAdvance?: () => void` prop. After calling `onChange`, trigger `onAutoAdvance` after 300ms. The delay is intentional: `handleSubmit` reads `answers[key]` from React state, and the 300ms wait ensures React has committed the `setAnswer` state update before `handleSubmit` fires. Do not reduce this delay to zero.
- `src/components/onboarding/YesNoToggle.tsx` — same pattern.
- `src/app/onboarding/page.tsx` — pass `onAutoAdvance={handleSubmit}` to all `ChipSelect` and `YesNoToggle` instances. No change needed for `LanguageCombobox` (multi-select; user must click "Finish" explicitly).

**Done when:** Selecting a chip or yes/no option automatically calls `handleSubmit()` (saving to localStorage) and advances to the next question after ~300ms. Completing the full 10-step flow saves all 9 required fields to localStorage and allows navigation to `/chat`.

---

### Issue 3: Verify onboarding completion flow end-to-end

**Problem:** The completion card and "Start chatting with Patty" button exist in code (the `if (completed) { return (...) }` block in `onboarding/page.tsx`) but may still be unreachable if Issues 1 and 2 leave any gap.

**Scope:**
- Run through the full 10-step onboarding flow after Issues 1 and 2 are fixed.
- Confirm the completion card renders and "Start chatting with Patty" navigates to `/chat`.
- Fix any remaining gap if found.

**Done when:** A full onboarding run completes successfully, all 9 required fields are in localStorage, and the user lands on `/chat`.

---

### Issue 4: Theme redesign pass (visual polish)

**Problem:** Beyond the functional fixes above, the overall visual design (font, spacing, color palette, component aesthetics) needs to be brought up to the intended clean white / Notion-like standard.

**Scope:** Full visual redesign pass using the `/frontend-design` skill. Covers font selection, spacing, color palette, and component-level polish across all pages.

**Done when:** Visual styling is approved by the user after the `/frontend-design` pass.

---

## Constraints

- Fix one issue at a time; do not proceed to the next until confirmed resolved by the user.
- No architectural changes — existing routing, data layer, and component structure are preserved.
- Issue 4 uses the `/frontend-design` skill; do not attempt a visual redesign before reaching that step.

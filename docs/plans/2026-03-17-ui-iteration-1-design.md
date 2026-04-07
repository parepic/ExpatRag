# UI Design Spec — Expat Compliance Copilot (Patty)

**Date:** 2026-03-17
**Status:** Approved

---

## Overview

A multi-page Next.js frontend for Patty, an AI-powered legal and compliance assistant for expats in the Netherlands. The UI consists of four main sections: a welcome page, an onboarding flow, a chat interface, and a settings area.

---

## Architecture

### Routes

| Route | View |
|---|---|
| `/` | Welcome page |
| `/onboarding` | Onboarding flow |
| `/chat` | Main chat interface |
| `/settings` | Settings shell (redirects to `/settings/profile`) |
| `/settings/profile` | Profile info / edit form |

### Route Groups (Shared Layouts)
- `src/app/(app)/layout.tsx` — shared layout for `/chat` and `/settings/*`, renders the left sidebar once. Avoids duplicating the sidebar across pages.
- `/` and `/onboarding` are standalone pages with no shared layout.

**File locations:**
```
src/app/page.tsx                        → /
src/app/onboarding/page.tsx             → /onboarding
src/app/(app)/layout.tsx                → shared sidebar layout
src/app/(app)/chat/page.tsx             → /chat
src/app/(app)/settings/page.tsx         → /settings (redirects to /settings/profile)
src/app/(app)/settings/profile/page.tsx → /settings/profile
src/app/api/chat/route.ts               → POST /api/chat (proxy to FastAPI)
```

### Page Transitions
- Short, subtle fade (100–150ms) between route navigations using `framer-motion`
- Each page file (`page.tsx`) is a Client Component (`"use client"`) and wraps its content in a `<motion.div>` with `initial={{ opacity: 0 }}` / `animate={{ opacity: 1 }}`. This is the standard pattern — pages are client components, but child components that don't need interactivity can still be Server Components.

### Redirect Guard
Implemented as a **Next.js middleware** (`src/middleware.ts`) — runs server-side before any page renders. Since localStorage is not accessible in middleware (it's browser-only), the middleware only handles the `/settings` exclusion. Profile completeness is checked client-side in a shared `useProfileGuard` hook called at the top of `/onboarding` and `/chat` pages.

Logic:

```
if route is /settings/* → allow (always, even if profile complete)
if profile is complete   → redirect to /chat
if profile is incomplete → redirect to /onboarding
if route is / and no profile → show welcome page normally
```

**Profile completeness** is defined in `src/lib/profile.ts` as: all required fields present and non-empty in localStorage. Required fields: `nationality`, `age`, `occupation`, `visa_type`, `languages`. Optional fields may be added later without breaking the completeness check.

### Data Layer
- **User profile** stored in `localStorage` as individual key-value pairs:
  - `nationality` — string label (e.g. `"EU/EEA citizen"`, `"Non-EU national"`, `"British (post-Brexit)"`, `"Dutch citizen"`)
  - `purpose_of_stay` — string label (e.g. `"Employed by Dutch/EU company"`, `"Highly Skilled Migrant"`, `"Self-employed / ZZP"`, `"Study"`, `"Family reunification"`, `"Starting a startup"`, `"Other"`)
  - `employment_situation` — string label (e.g. `"Employed full-time"`, `"Self-employed / ZZP"`, `"DGA (director/shareholder)"`, `"Not working"`, `"Student"`)
  - `registration_status` — string label (e.g. `"Not yet arrived"`, `"Arrived, not yet registered"`, `"BRP registered"`, `"Have BSN"`, `"Have DigiD"`)
  - `has_fiscal_partner` — `"yes"` or `"no"`
  - `housing_situation` — string label (e.g. `"Renting privately"`, `"Renting social housing"`, `"Buying / own property"`, `"Employer-provided"`, `"No fixed address"`)
  - `salary_band` — string label (e.g. `"Under €20k"`, `"€20k–€40k"`, `"€40k–€60k"`, `"€60k–€80k"`, `"€80k–€100k"`, `"Over €100k"`)
  - `age_bracket` — `"under_30"` or `"30_or_older"`
  - `prior_nl_residency` — string label (e.g. `"Never lived in NL"`, `"Left more than 2 years ago"`, `"Left within the last 2 years"`)
  - `languages` — JSON array of display names (e.g. `["Dutch","British English"]`)
- `src/lib/profile.ts` exposes: `getField(key)`, `setField(key, value)`, `isComplete()`, `getMissingFields()`
- Required fields for completeness: `nationality`, `purpose_of_stay`, `employment_situation`, `registration_status`, `has_fiscal_partner`, `housing_situation`, `salary_band`, `age_bracket`, `prior_nl_residency`
- **localStorage unavailability** (e.g. private browsing): catch the access error, fall back to in-memory state for the session, and show a dismissible toast banner: "Your data won't be saved between sessions." Profile completeness check treats unavailable localStorage as "no profile" and starts onboarding.
- **Todos and chat sessions** live in React Context (`src/context/AppContext.tsx`), in-memory only. They reset on page refresh — this is expected behaviour for now and not a bug. Future plan: migrate to PostgreSQL.

### Theme System
- CSS custom properties defined in `globals.css` (e.g. `--color-bg`, `--color-text`, `--color-accent`)
- All components reference these variables — changing the theme means updating one block of CSS
- Only one theme shipped initially (clean white / Notion-like)

### Libraries

| Purpose | Library |
|---|---|
| UI components | `shadcn/ui` (Radix UI + Tailwind v4) |
| Page fade + onboarding animations | `framer-motion` |
| Searchable combobox (countries, languages) | shadcn/ui Combobox (built on `cmdk`) |
| Country code list | `countries-list` (provides alpha-2 codes + metadata) |
| Country display names | `Intl.DisplayNames` built-in (`type: "region"`) — e.g. `"NL"` → `"Netherlands"` |
| Language code list | `iso-639-1` (provides ISO 639-1 codes) |
| Language display names | `Intl.DisplayNames` built-in (`type: "language"`) — e.g. `"nl"` → `"Dutch"`, `"en-GB"` → `"British English"` |
| Netherlands visa types | Custom constants file (`src/lib/visa-types.ts`) |
| Occupation options | Custom constants file (`src/lib/occupation-types.ts`) |
| Chat streaming state | `@ai-sdk/react` (`useChat` hook) |
| Chat UI components | `@assistant-ui/react` + `@assistant-ui/react-ai-sdk` |
| Sidebar | shadcn/ui `Sidebar` component |

**Display name pattern:**
```ts
const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
const languageNames = new Intl.DisplayNames(["en"], { type: "language" });

regionNames.of("NL");    // "Netherlands"
regionNames.of("GB");    // "United Kingdom"
languageNames.of("nl");  // "Dutch"
languageNames.of("en-GB"); // "British English"
```
`Intl.DisplayNames` is zero-cost (built into Node.js 12+ and all modern browsers). `countries-list` and `iso-639-1` are only used to enumerate the full code lists for the combobox options.

> **`@assistant-ui/react` owns chat UI rendering** — it provides the `<Thread>` component (message list, auto-scroll, composer/input bar, streaming indicator). `@ai-sdk/react` (`useChat`) is the data hook underneath it, managing streaming state. Do not build a custom message list or input bar — use `@assistant-ui/react` components and restyle them.

> **Tailwind v4 risk:** `@assistant-ui/react` components are installed as editable `.tsx` source files in the project. Run `pnpm build` after installation to verify all Tailwind classes compile. Fix any missing utilities directly in the installed files.

---

## Section 1: Welcome Page (`/`)

### Layout
- Full-screen, white background
- **Foreground:** Large bold hero text centered in the upper half — e.g. "Your all-in-one expat moving assistant"
- **Background:** Looping animated chat simulation — coded React component using CSS keyframes and sequential `setTimeout`/state updates. Renders fake message bubbles appearing one by one (user asks about DigiD, Patty responds, conversation continues). Styled with low opacity and a CSS `blur` filter so it does not compete with the hero text.
- **Bottom half center:** Single "Get Started" CTA button

### Behaviour
- If localStorage profile is complete → skip, redirect to `/chat`
- If incomplete or empty → show welcome page with "Get Started"
- "Get Started" → navigates to `/onboarding`

---

## Section 2: Onboarding Flow (`/onboarding`)

### Layout
- Centered card on a white background, vertically centered
- One question displayed at a time
- **Back / Forward buttons** at the top of the card
  - Back: always shown (disabled on first question)
  - Forward: only active if the current question was already answered
- **Progress indicator** at the bottom: a row of dots (● ● ○ ○ ○) — filled dots = answered, empty = remaining

### Questions

| # | Field | Input type | Data source |
|---|---|---|---|
| 1 | Nationality / citizenship | Chip select | Custom options (4 categories) |
| 2 | Purpose of stay | Chip select | `src/lib/purpose-types.ts` |
| 3 | Employment situation | Chip select | `src/lib/occupation-types.ts` |
| 4 | Registration / BRP / BSN status | Chip select | Custom options (5 steps) |
| 5 | Fiscal partner? | Yes / No toggle | — |
| 6 | Housing situation | Chip select | Custom options |
| 7 | Gross annual salary | Chip select (income bands) | Custom options |
| 8 | Age bracket | Yes / No toggle ("Are you under 30?") | — |
| 9 | Prior NL residency | Chip select | Custom options (3 options) |
| 10 | Languages spoken | Searchable combobox (multi-select) | `iso-639-1` codes, displayed via `Intl.DisplayNames` |

Fields 1–5 are the core essential questions. Fields 6–10 are secondary but collected in the same sequential flow.

### Question Transitions (`framer-motion AnimatePresence`)
- On submit: current card **slides up and fades out** (`y: -40, opacity: 0`)
- Next card **slides in from below and fades in** (`y: 40 → 0, opacity: 0 → 1`)
- Back navigation reverses the direction

### Onboarding resume (partial progress)
- On load, `getMissingFields()` from `profile.ts` determines the first unanswered question
- The flow starts from that question, not from question 1

### Browser back button
- Onboarding is a **single-route state machine** — step index is held in React state, not in the URL
- The browser back button navigates away from `/onboarding` entirely (back to `/`)
- The in-UI Back button steps backwards through questions

### Data Writing
- Each answer is written to localStorage **immediately on submit**
- Partial progress is preserved if the user closes mid-onboarding

### Error / loading states
- No async calls during onboarding — no loading states needed
- Validation errors shown inline below the input (e.g. "Please enter a valid age")

### Completion Screen
- After the last question, a confirmation card slides in (same animation)
- Text: "You're all set! We've saved your details and will use them to give you personalised advice."
- Button: "Start chatting with Patty" → navigates to `/chat`

---

## Section 3: Chat Interface (`/chat`)

### Layout
- **Left sidebar** (~240px, fixed) + **main chat area** (fills remaining width)
- Sidebar rendered once in `(app)/layout.tsx`, shared with `/settings`

#### Sidebar (top to bottom)
- "Patty" logo / app name at the top
- Settings icon/link → navigates to `/settings/profile`
- **Todos** (middle): list of AI-suggested action items with checkboxes. Empty state: "No tasks yet — Patty will suggest things as you chat."
- **Previous chats** (bottom): list of session titles from the current browser session only (in-memory). A "Session only" note makes clear these don't persist across page refreshes. "New chat" button above the list.

#### Main Chat Area
- `<Thread>` from `@assistant-ui/react` renders the full message list + composer
- Empty state: "Start a new conversation with Patty" centered in the area
- Fixed composer (input bar) at the bottom — multi-line, send on Enter or button click
- Typing / streaming indicator: built into `@assistant-ui/react`, driven by `useChat` status

### API
- `useChat` posts to `/api/chat` (Next.js route handler at `src/app/api/chat/route.ts`)
- The route handler forwards the request body to the FastAPI backend and pipes the streaming response back to the browser using a `ReadableStream`
- The browser communicates only with `/api/chat` — FastAPI is never called directly from the client
- On FastAPI connection failure: the route handler returns a 502 response; `useChat` surfaces this as an error state

### Error states
- If `useChat` returns an error: show an inline error message below the last message — "Something went wrong. Please try again." with a retry button that re-sends the last message. The error message is dismissible.

---

## Section 4: Settings (`/settings/profile`)

### Layout
- Same `(app)/layout.tsx` sidebar as chat, but:
  - Top link reads **"Back to Patty"** → navigates to `/chat`
  - Vertical nav below: "Profile" (only item for now)
- Right side: settings page content area

### Profile Page
- **Read-only view:** all onboarding answers displayed as label + value pairs
  - Multi-value fields (languages) shown as a comma-separated list or badges
- **"Edit" button** (top-right): switches all fields to editable inputs (same types as onboarding)
- **"Save" button**: validates inputs, writes updated values to localStorage, returns to read-only view
- **"Cancel" button**: reverts all fields to their last saved values (no localStorage write), returns to read-only view

---

## Out of Scope (for now)
- Real user authentication / backend user accounts
- Persistent chat / todo storage (PostgreSQL migration planned)
- Multiple theme options (theme system built in, only one theme shipped)
- Dark mode (globals.css dark media query to be removed or left unused)
- Internationalisation (UI is English only)
- Browser back button navigation within onboarding steps

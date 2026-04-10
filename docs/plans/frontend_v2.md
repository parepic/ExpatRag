# Frontend v2 — `patty_frontend`

## Required reading

Before working on this frontend, read these files for full context:

- [Product spec](../product-spec.md) — Business-level rules (auth, onboarding, citations, data privacy)
- [Backend API endpoints](../../backend/app/api/) — The REST endpoints the frontend calls (`auth.py`, `chats.py`, `users.py`)
- [Backend schemas](../../backend/app/schemas/) — Request/response shapes (`auth.py`, `chat.py`, `user.py`)

---

## Purpose

ExpatRag helps expats and small businesses in the Netherlands navigate complex legal and compliance rules from government sources (IND, Belastingdienst, KVK). The frontend is how users interact with this system. It must let them:

1. **Get cited, trustworthy answers** — Ask questions and receive RAG-powered responses with direct hyperlinks back to the official government source paragraph. This is the core value of the app: no hallucinated legal advice.

2. **Provide personal context for tailored answers** — Users share details about their situation (visa type, employment, nationality, salary band, etc.) through an onboarding flow so the system can personalize its responses.

3. **Authenticate and persist across devices** — Users log in with an account so their profile and chat history are available on any device, not tied to a single browser.

4. **Access conversation history** — Return to past conversations to review advice, continue a thread, or reference previously cited sources.

## What changes from the current frontend

The current `frontend/` works but has a fundamental limitation: it stores user profiles in browser cookies and chat history in localStorage. There is no real account system — "identity" lives in the browser. The backend already has proper authentication (register/login with session tokens), DB-backed user profiles, and server-persisted chat history, but the current frontend doesn't use any of it.

`patty_frontend` fixes this by becoming a proper client to the backend API:

- **No more localStorage/cookie-based state** — Profile data and chat history come from the backend. The frontend only stores a session cookie for authentication.
- **Real authentication** — A login/register flow that uses the backend's auth endpoints. Users get cross-device access to their data.
- **Onboarding sends data to the backend** — The onboarding wizard still gathers user info the same way, but saves it to the backend instead of browser cookies.
- **Visual design stays the same** — The layout, styling, and presentation of the current frontend are intentionally preserved. This is a plumbing change, not a redesign.

---

## Architecture & stack

Carried over from the current `frontend/` — same stack, same conventions:

- **Framework**: Next.js (App Router) with TypeScript strict mode
- **Styling**: Tailwind CSS v4 (CSS-first config in `globals.css`, no `tailwind.config.*` file)
- **UI components**: shadcn/ui (Radix UI + Tailwind)
- **Chat UI**: Custom components (message list, composer) — no streaming library needed for now
- **Package manager**: pnpm
- **Dev server**: Turbopack
- **Path alias**: `@/*` → `./src/*`

### What's different from `frontend/`

| Concern | `frontend/` | `patty_frontend/` |
|---|---|---|
| User identity | localStorage + cookies | Backend session cookie (set by `/auth/login`) |
| Profile storage | `localStorage` via `lib/profile.ts` | Backend API (`/users/me`, `/auth/register`) |
| Chat persistence | `localStorage` via `lib/chat-store.ts` | Backend API (`/chats`) |
| Auth check | `useProfileGuard` (checks localStorage) | Call `/auth/me` — redirect to `/login` if 401 |
| Login page | None | `/login` (new) |

---

## Project structure

```
patty_frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                         # Root layout (fonts, global styles — no auth)
│   │   ├── page.tsx                           # Welcome page (/) — public
│   │   ├── login/
│   │   │   └── page.tsx                       # Login / register — public
│   │   ├── (auth)/                            # Auth-required route group
│   │   │   ├── layout.tsx                     # Wraps children in AuthProvider (redirects to /login if 401)
│   │   │   ├── onboarding/
│   │   │   │   └── page.tsx                   # Onboarding wizard
│   │   │   └── (app)/                         # Auth + sidebar route group (nested)
│   │   │       ├── layout.tsx                 # Shared sidebar layout for /chat and /settings
│   │   │       ├── chat/
│   │   │       │   └── page.tsx               # Chat interface
│   │   │       └── settings/
│   │   │           ├── page.tsx               # Redirects to /settings/profile
│   │   │           └── profile/
│   │   │               └── page.tsx           # Profile view/edit
│   │   └── api/                               # (empty for now — streaming proxy added later)
│   ├── components/
│   │   ├── ui/                                # General-purpose components, used across pages
│   │   │   ├── input/                         #   Button, Input, Textarea, Checkbox, Command
│   │   │   ├── display/                       #   Avatar, Badge, Skeleton, Separator
│   │   │   ├── overlay/                       #   Dialog, Popover, Sheet, Tooltip, Sonner (toasts)
│   │   │   └── layout/                        #   Sidebar, Collapsible
│   │   ├── welcome/                           # Components specific to the welcome page (/)
│   │   ├── login/                             # Components specific to the login page
│   │   ├── onboarding/                        # Components specific to the onboarding page
│   │   └── chat/                              # Components specific to the chat page (Thread, etc.)
│   ├── hooks/
│   │   ├── useAuth.ts                         # Calls /auth/me, returns user or null
│   │   └── useIsMobile.tsx                    # Reactive boolean for mobile breakpoint (used by Sidebar)
│   ├── lib/
│   │   ├── types/
│   │   │   └── user.ts                        # User type definition (mirrors backend API response)
│   │   ├── api/                               # Backend API call functions (mirrors backend/app/api/)
│   │   │   ├── auth.ts                        #   login(), register(), logout(), getMe()
│   │   │   ├── users.ts                       #   updateUser()
│   │   │   └── chats.ts                       #   fetchChats(), fetchChat(), createChat(), deleteChat()
│   │   ├── constants/                         # Nationality options, salary bands, etc.
│   │   └── utils.ts                           # General utilities
│   └── context/
│       ├── AuthContext.tsx                    # Wraps useAuth, provides user via React context, redirects if 401
│       └── AppContext.tsx                     # Shared app state (active chat ID, etc.)
├── public/                                    # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
└── postcss.config.ts
```

---

## Features

Each feature has its own spec and implementation plan. They are organized by the page they live on. Cross-cutting concerns (auth, layout, API calls) are covered within the page specs where they're needed.

| # | Feature | Spec file | Status |
|---|---|---|---|
| 1 | Welcome page (`/`) | [welcome-page.md](frontend_v2/welcome-page.md) | Not started |
| 2 | Login & registration (`/login`) | [login-page.md](frontend_v2/login-page.md) | Not started |
| 3 | Onboarding flow (`/onboarding`) | [onboarding.md](frontend_v2/onboarding.md) | Not started |
| 4 | Chat interface (`/chat`) | [chat.md](frontend_v2/chat.md) | Not started |
| 5 | Settings & profile (`/settings/profile`) | [settings-profile.md](frontend_v2/settings-profile.md) | Not started |

---

## Implementation steps

### Step 0: Scaffolding

Set up the project before building any features:

1. Initialize Next.js project in `patty_frontend/` with TypeScript, Tailwind v4, App Router, pnpm. Set the package name to `frontend` (not `patty_frontend`) so no config changes are needed when the directory is renamed later.
2. Configure Turbopack, path aliases, PostCSS
3. Initialize shadcn/ui (`npx shadcn init`) — this sets up the CLI config, `cn()` utility, and base styles. Do not install any components yet; they will be added on demand as each feature needs them (e.g. `npx shadcn add button`).
4. Create fresh global styles, theme tokens, and base UI plumbing in `patty_frontend/`, using `frontend/` only as reference where needed
5. Recreate the required constants in `src/lib/constants/` from scratch
6. Set up the route structure (empty page shells for `/`, `/login`, `/onboarding`, `/chat`, `/settings/profile`)
7. Verify `pnpm dev` and `pnpm build` work

### Step 1: `useAuth` hook

Create `src/hooks/useAuth.ts` — a shared hook that checks the user's authentication status by calling the backend. Needed by the welcome page (Step 2) and later by `AuthContext` (Step 4).

**Behaviour:**
- On mount, call `GET /auth/me` with `credentials: "include"` to send the session cookie.
- Return `{ user, isLoading }` where `user` is `User | null`:
  - While the request is in flight: `{ user: null, isLoading: true }`
  - If 200: `{ user: <response body>, isLoading: false }`
  - If 401 or network error: `{ user: null, isLoading: false }`
- This hook is intentionally minimal — it does not redirect or provide context. Redirects are the caller's responsibility. `AuthContext` (built later) will wrap this hook for protected routes.

### Step 2: Welcome page (`/`)

Spec: [welcome-page.md](frontend_v2/welcome-page.md)

### Step 3: Login & registration (`/login`)

Spec: [login-page.md](frontend_v2/login-page.md)

### Step 4: `AuthContext` provider

Create `src/context/AuthContext.tsx` — wraps `useAuth` and provides the user via React context. Used by the `(auth)/layout.tsx` route group to protect all authenticated routes. Redirects to `/login` on 401. Must be built before onboarding and chat, which live inside the `(auth)` group.

### Step 5: `User` type

Create `src/lib/types/user.ts` — the canonical type for a user, matching the backend `GET /auth/me` response shape exactly (snake_case, no conversion layer).

- Fields: `id`, `username`, `created_at`, plus the 8 profile fields (`nationality`, `purpose_of_stay`, `employment_status`, `registration_status`, `has_fiscal_partner`, `salary_band`, `age_bracket_under_30`, `prior_nl_residency`).
- Text profile fields (`nationality`, `purpose_of_stay`, `employment_status`, `registration_status`, `salary_band`) should be typed against their corresponding constants arrays so only valid values are accepted.
- Boolean profile fields (`has_fiscal_partner`, `age_bracket_under_30`, `prior_nl_residency`) are typed as `boolean | null`.
- All profile fields are `| null` because they start empty and get filled during onboarding.

### Step 6: Onboarding flow (`/onboarding`)

Spec: [onboarding.md](frontend_v2/onboarding.md)

### Step 7: `AppContext` provider

Create `src/context/AppContext.tsx` — shared state for the app shell, used by the sidebar layout and the chat page. Provides `activeChatId` and `setActiveChatId` via React context. The layout uses it to highlight the active chat in the sidebar and the chat page uses it to know which conversation to display. Wrap this provider in the `(auth)/(app)/layout.tsx` alongside `AuthContext`.

### Step 8: Shared app layout

Create `src/app/(auth)/(app)/layout.tsx` — the shared sidebar layout used by both `/chat` and `/settings/profile`. This is a Client Component that adapts its sidebar content based on the current route.

The layout has two zones: a sidebar on the left and a main content area on the right.

**Sidebar contents:**
- **Logo** at the top ("Patty").
- **Nav section** that changes based on the route:
  - On `/chat`: a link to `/settings/profile` (with a settings icon).
  - On `/settings/*`: a "Back to Patty" link to `/chat`, plus a settings sub-nav (Profile link).
- **Chat history list** (only shown on `/chat`): shows recent chat titles. Each item is clickable to set the active chat via `AppContext`. A "+ New" button sets `activeChatId` to `null` (the chat page handles the actual creation). The API calls (`GET /chats`, `POST /chats`, etc.) are not wired up here — they are implemented in Step 9 (chat interface). For now the sidebar can call stub functions or render placeholder data.

**Main content area:**
- A **header breadcrumb** that reflects the current page (e.g. "Chat with Patty" or "Settings > Profile").
- Below the header, the page content (`{children}`) fills the remaining height and scrolls independently.

**Route detection:** Use `usePathname()` and check `pathname.startsWith("/settings")` to toggle between chat and settings sidebar modes.

**Reference:** The old `frontend/src/app/(app)/layout.tsx` has this exact layout with good styling. Carry over the structure and visual design — the only change is that chat history comes from the backend API instead of localStorage.

### Step 9: Chat interface (`/chat`)

Spec: [chat.md](frontend_v2/chat.md)

### Step 10: Settings & profile (`/settings/profile`)

Spec: [settings-profile.md](frontend_v2/settings-profile.md)

### Final step: Verify and rename

1. Run a full `pnpm build` to confirm there are no type errors or broken imports across the project.
2. Delete the old `frontend/` directory and rename `patty_frontend/` to `frontend/`. The project should work without any code changes after the rename — ensure nothing in the codebase (package.json name, paths, configs) hardcodes the `patty_frontend` name.

---

## Backend dependencies

Tasks that need to happen on the backend side before or alongside this frontend work:

- **Validate profile field values** — The backend currently accepts any string for profile fields like `nationality`, `salary_band`, etc. (`str | None`). It should validate against the same allowed values that the frontend uses in `src/lib/constants/`. Without this, a direct API call can bypass the frontend's constraints and store invalid data.

---
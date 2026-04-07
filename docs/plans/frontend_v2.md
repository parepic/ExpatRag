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

### Step 1–5: Feature implementation

Each feature is specced and built in its own file (see table above). Steps will be added here as we write each spec.

### Final step: Verify and rename

1. Run a full `pnpm build` to confirm there are no type errors or broken imports across the project.
2. Delete the old `frontend/` directory and rename `patty_frontend/` to `frontend/`. The project should work without any code changes after the rename — ensure nothing in the codebase (package.json name, paths, configs) hardcodes the `patty_frontend` name.

---

## Backend dependencies

Tasks that need to happen on the backend side before or alongside this frontend work:

- **Validate profile field values** — The backend currently accepts any string for profile fields like `nationality`, `salary_band`, etc. (`str | None`). It should validate against the same allowed values that the frontend uses in `src/lib/constants/`. Without this, a direct API call can bypass the frontend's constraints and store invalid data.

---
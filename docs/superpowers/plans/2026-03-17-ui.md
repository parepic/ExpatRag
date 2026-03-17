# UI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete Patty frontend — welcome page, onboarding flow, chat interface, and settings — as described in the UI design spec.

**Architecture:** Next.js 16 App Router with a route group `(app)` sharing a sidebar layout for `/chat` and `/settings`. Profile data lives in localStorage via a typed helper. Chat state lives in React Context. shadcn/ui + framer-motion handle UI and animations.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, framer-motion, @ai-sdk/react, @assistant-ui/react, countries-list, iso-639-1

---

## File Map

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                          MODIFY  root layout (metadata, fonts)
│   │   ├── globals.css                         MODIFY  theme CSS custom properties
│   │   ├── page.tsx                            REPLACE welcome page
│   │   ├── middleware.ts                       CREATE  route guard (settings exclusion)
│   │   ├── onboarding/
│   │   │   └── page.tsx                        CREATE  onboarding flow
│   │   ├── (app)/
│   │   │   ├── layout.tsx                      CREATE  shared sidebar layout
│   │   │   ├── chat/
│   │   │   │   └── page.tsx                    CREATE  chat interface
│   │   │   └── settings/
│   │   │       ├── page.tsx                    CREATE  redirect → /settings/profile
│   │   │       └── profile/
│   │   │           └── page.tsx                CREATE  profile read/edit form
│   │   └── api/
│   │       └── chat/
│   │           └── route.ts                    CREATE  streaming proxy to FastAPI
│   ├── lib/
│   │   ├── profile.ts                          CREATE  localStorage read/write helpers
│   │   └── constants/
│   │       ├── nationality-options.ts          CREATE  4 nationality categories
│   │       ├── purpose-types.ts                CREATE  purpose of stay options
│   │       ├── occupation-types.ts             CREATE  employment situation options
│   │       ├── registration-status.ts          CREATE  BRP/BSN status options
│   │       ├── housing-options.ts              CREATE  housing situation options
│   │       ├── salary-bands.ts                 CREATE  income band options
│   │       └── residency-options.ts            CREATE  prior NL residency options
│   ├── context/
│   │   └── AppContext.tsx                      CREATE  todos + chat sessions state
│   ├── hooks/
│   │   └── useProfileGuard.ts                 CREATE  client-side profile redirect hook
│   └── components/
│       ├── onboarding/
│       │   ├── ChipSelect.tsx                  CREATE  clickable chip option selector
│       │   ├── YesNoToggle.tsx                 CREATE  yes/no binary toggle
│       │   ├── LanguageCombobox.tsx            CREATE  searchable multi-select for languages
│       │   ├── ProgressDots.tsx                CREATE  dot progress indicator
│       │   └── QuestionCard.tsx               CREATE  animated question card wrapper
│       ├── welcome/
│       │   └── AnimatedChat.tsx               CREATE  looping background chat simulation
│       └── ui/                                 (shadcn/ui components installed here by CLI)
├── __tests__/
│   ├── lib/
│   │   └── profile.test.ts                    CREATE  unit tests for profile helpers
│   ├── context/
│   │   └── AppContext.test.tsx                CREATE  context state tests
│   ├── hooks/
│   │   └── useProfileGuard.test.ts            CREATE  redirect hook tests
│   └── components/
│       ├── ChipSelect.test.tsx                CREATE  chip select component tests
│       └── ProgressDots.test.tsx              CREATE  progress dots tests
└── jest.config.ts                             CREATE  jest configuration
```

---

## Task 1: Install Dependencies

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install shadcn/ui CLI and init**

Run from `frontend/`:
```bash
pnpm dlx shadcn@latest init
```
When prompted: choose "Default" style, "zinc" base color (closest to Notion grey), CSS variables: yes.

- [ ] **Step 2: Install shadcn/ui components**

```bash
pnpm dlx shadcn@latest add button input textarea badge checkbox avatar toast sidebar
```

- [ ] **Step 3: Install runtime dependencies**

```bash
pnpm add framer-motion @ai-sdk/react ai @assistant-ui/react @assistant-ui/react-ai-sdk countries-list iso-639-1
```

- [ ] **Step 4: Install testing dependencies**

```bash
pnpm add -D jest jest-environment-jsdom @testing-library/react @testing-library/user-event @testing-library/jest-dom ts-jest @types/jest
```

- [ ] **Step 5: Verify build still passes**

```bash
pnpm build
```
Expected: Build completes with no errors. If `@assistant-ui/react` has Tailwind v4 class issues, note the failing class names — they will be fixed in later tasks when those components are used.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "chore: install UI dependencies and shadcn/ui"
```

---

## Task 2: Testing Setup

**Files:**
- Create: `frontend/jest.config.ts`
- Create: `frontend/jest.setup.ts`
- Modify: `frontend/package.json`

- [ ] **Step 1: Create jest config**

Create `frontend/jest.config.ts`:
```ts
import type { Config } from "jest";

const config: Config = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  transform: {
    "^.+\\.tsx?$": ["ts-jest", { tsconfig: { jsx: "react-jsx" } }],
  },
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  testMatch: ["**/__tests__/**/*.test.{ts,tsx}"],
};

export default config;
```

- [ ] **Step 2: Create jest setup file**

Create `frontend/jest.setup.ts`:
```ts
import "@testing-library/jest-dom";
```

- [ ] **Step 3: Add test script to package.json**

In `frontend/package.json`, add to `"scripts"`:
```json
"test": "jest",
"test:watch": "jest --watch"
```

- [ ] **Step 4: Create test directories**

```bash
mkdir -p frontend/__tests__/lib frontend/__tests__/context frontend/__tests__/hooks frontend/__tests__/components
```

- [ ] **Step 5: Run tests to confirm setup works (no tests yet, should pass with 0 suites)**

```bash
cd frontend && pnpm test
```
Expected: "No test suites found" or exit 0.

- [ ] **Step 6: Confirm jest setup is wired**

The correct key is `setupFilesAfterEnv` (not `setupFilesAfterFramework` — that is not a valid Jest key). Run:
```bash
cd frontend && pnpm test -- --verbose 2>&1 | head -20
```
Expected: Jest starts, finds 0 suites (no test files yet), exits cleanly. If it errors about `setupFilesAfterEnv`, double-check the jest.config.ts spelling.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "chore: configure jest + testing-library"
```

---

## Task 3: Theme System + Global Styles

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Replace globals.css with Patty theme**

Replace the entire contents of `frontend/src/app/globals.css`:
```css
@import "tailwindcss";

/* ─── Patty Theme ─────────────────────────────────────────── */
:root {
  --color-bg:           #ffffff;
  --color-bg-subtle:    #f7f7f5;   /* Notion-like off-white for cards/sidebar */
  --color-border:       #e8e8e6;
  --color-text:         #1a1a1a;
  --color-text-muted:   #787774;
  --color-accent:       #2f6ef7;   /* Primary blue for buttons, active states */
  --color-accent-hover: #1a5ae0;
  --color-success:      #0f9d58;
  --color-error:        #d93025;

  --radius:             8px;
  --sidebar-width:      240px;
}

@theme inline {
  --color-background: var(--color-bg);
  --color-foreground: var(--color-text);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-geist-sans), Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Remove dark mode — out of scope for now */
```

- [ ] **Step 2: Update layout.tsx metadata**

In `frontend/src/app/layout.tsx`, update the metadata:
```ts
export const metadata: Metadata = {
  title: "Patty — Your Expat Compliance Copilot",
  description: "Personalized legal and compliance guidance for expats in the Netherlands.",
};
```

- [ ] **Step 3: Verify dev server starts cleanly**

```bash
cd frontend && pnpm dev
```
Expected: Server starts, no CSS errors, page renders with white background.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: add Patty theme system and update metadata"
```

---

## Task 4: Profile Data Library

**Files:**
- Create: `frontend/src/lib/profile.ts`
- Create: `frontend/src/lib/constants/nationality-options.ts`
- Create: `frontend/src/lib/constants/purpose-types.ts`
- Create: `frontend/src/lib/constants/occupation-types.ts`
- Create: `frontend/src/lib/constants/registration-status.ts`
- Create: `frontend/src/lib/constants/housing-options.ts`
- Create: `frontend/src/lib/constants/salary-bands.ts`
- Create: `frontend/src/lib/constants/residency-options.ts`
- Test: `frontend/__tests__/lib/profile.test.ts`

- [ ] **Step 1: Write failing tests for profile.ts**

Create `frontend/__tests__/lib/profile.test.ts`:
```ts
import { getField, setField, isComplete, getMissingFields, REQUIRED_FIELDS } from "@/lib/profile";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, "localStorage", { value: localStorageMock });

beforeEach(() => localStorageMock.clear());

describe("getField", () => {
  it("returns null when key is not set", () => {
    expect(getField("nationality")).toBeNull();
  });
  it("returns the stored value", () => {
    localStorageMock.setItem("nationality", "EU/EEA citizen");
    expect(getField("nationality")).toBe("EU/EEA citizen");
  });
});

describe("setField", () => {
  it("writes the value to localStorage", () => {
    setField("nationality", "Non-EU national");
    expect(localStorageMock.getItem("nationality")).toBe("Non-EU national");
  });
});

describe("isComplete", () => {
  it("returns false when no fields are set", () => {
    expect(isComplete()).toBe(false);
  });
  it("returns false when only some fields are set", () => {
    setField("nationality", "EU/EEA citizen");
    expect(isComplete()).toBe(false);
  });
  it("returns true when all required fields are set", () => {
    REQUIRED_FIELDS.forEach((key) => setField(key, "some-value"));
    expect(isComplete()).toBe(true);
  });
});

describe("getMissingFields", () => {
  it("returns all required fields when nothing is set", () => {
    expect(getMissingFields()).toEqual(REQUIRED_FIELDS);
  });
  it("returns only the unset fields", () => {
    setField("nationality", "EU/EEA citizen");
    setField("purpose_of_stay", "Study");
    const missing = getMissingFields();
    expect(missing).not.toContain("nationality");
    expect(missing).not.toContain("purpose_of_stay");
    expect(missing.length).toBe(REQUIRED_FIELDS.length - 2);
  });
});
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
cd frontend && pnpm test profile
```
Expected: FAIL — `@/lib/profile` module not found.

- [ ] **Step 3: Create the profile library**

Create `frontend/src/lib/profile.ts`:
```ts
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
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
cd frontend && pnpm test profile
```
Expected: All tests PASS.

- [ ] **Step 5: Create constants files**

Create `frontend/src/lib/constants/nationality-options.ts`:
```ts
export const NATIONALITY_OPTIONS = [
  "EU/EEA citizen",
  "Non-EU national",
  "British (post-Brexit)",
  "Dutch citizen",
] as const;
```

Create `frontend/src/lib/constants/purpose-types.ts`:
```ts
export const PURPOSE_OPTIONS = [
  "Employed by Dutch/EU company",
  "Highly Skilled Migrant",
  "Self-employed / ZZP",
  "Study",
  "Family reunification",
  "Starting a startup",
  "Other",
] as const;
```

Create `frontend/src/lib/constants/occupation-types.ts`:
```ts
export const OCCUPATION_OPTIONS = [
  "Employed full-time",
  "Employed part-time",
  "Self-employed / ZZP",
  "DGA (director/shareholder of own BV)",
  "Not working / dependent on partner",
  "Student",
] as const;
```

Create `frontend/src/lib/constants/registration-status.ts`:
```ts
export const REGISTRATION_OPTIONS = [
  "Not yet arrived in the Netherlands",
  "Arrived, not yet registered",
  "BRP registered at a municipality",
  "Have a BSN number",
  "Have DigiD",
] as const;
```

Create `frontend/src/lib/constants/housing-options.ts`:
```ts
export const HOUSING_OPTIONS = [
  "Renting privately",
  "Renting social housing",
  "Buying / own property",
  "Employer-provided housing",
  "No fixed address / temporary",
] as const;
```

Create `frontend/src/lib/constants/salary-bands.ts`:
```ts
export const SALARY_BANDS = [
  "Under €20,000",
  "€20,000 – €40,000",
  "€40,000 – €60,000",
  "€60,000 – €80,000",
  "€80,000 – €100,000",
  "Over €100,000",
] as const;
```

Create `frontend/src/lib/constants/residency-options.ts`:
```ts
export const RESIDENCY_OPTIONS = [
  "Never lived in the Netherlands",
  "Left more than 2 years ago",
  "Left within the last 2 years",
] as const;
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: add profile data library and onboarding constants"
```

---

## Task 5: App Context (Todos + Chat Sessions)

**Files:**
- Create: `frontend/src/context/AppContext.tsx`
- Test: `frontend/__tests__/context/AppContext.test.tsx`

- [ ] **Step 1: Write failing tests**

Create `frontend/__tests__/context/AppContext.test.tsx`:
```tsx
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppProvider, useAppContext } from "@/context/AppContext";

function TestConsumer() {
  const { todos, addTodo, toggleTodo, chats, addChat, activeChat, setActiveChat } = useAppContext();
  return (
    <div>
      <div data-testid="todos">{todos.length}</div>
      <div data-testid="chats">{chats.length}</div>
      <div data-testid="active-chat">{activeChat ?? "none"}</div>
      <button onClick={() => addTodo("Register at municipality")}>Add Todo</button>
      <button onClick={() => toggleTodo(todos[0]?.id ?? "")}>Toggle Todo</button>
      <button onClick={() => addChat("My first chat")}>Add Chat</button>
      <button onClick={() => setActiveChat("chat-1")}>Set Active</button>
    </div>
  );
}

const renderWithProvider = () =>
  render(<AppProvider><TestConsumer /></AppProvider>);

describe("AppContext todos", () => {
  it("starts with no todos", () => {
    renderWithProvider();
    expect(screen.getByTestId("todos")).toHaveTextContent("0");
  });
  it("adds a todo", async () => {
    renderWithProvider();
    await userEvent.click(screen.getByText("Add Todo"));
    expect(screen.getByTestId("todos")).toHaveTextContent("1");
  });
});

describe("AppContext chats", () => {
  it("starts with no chats", () => {
    renderWithProvider();
    expect(screen.getByTestId("chats")).toHaveTextContent("0");
  });
  it("adds a chat session", async () => {
    renderWithProvider();
    await userEvent.click(screen.getByText("Add Chat"));
    expect(screen.getByTestId("chats")).toHaveTextContent("1");
  });
});
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
cd frontend && pnpm test AppContext
```
Expected: FAIL — module not found.

- [ ] **Step 3: Implement AppContext**

Create `frontend/src/context/AppContext.tsx`:
```tsx
"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: number;
}

interface AppContextValue {
  todos: Todo[];
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
  chats: ChatSession[];
  addChat: (title: string) => string;
  activeChat: string | null;
  setActiveChat: (id: string | null) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);

  const addTodo = useCallback((text: string) => {
    const id = crypto.randomUUID();
    setTodos((prev) => [...prev, { id, text, completed: false }]);
  }, []);

  const toggleTodo = useCallback((id: string) => {
    setTodos((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }, []);

  const addChat = useCallback((title: string): string => {
    const id = crypto.randomUUID();
    setChats((prev) => [{ id, title, createdAt: Date.now() }, ...prev]);
    setActiveChat(id);
    return id;
  }, []);

  return (
    <AppContext.Provider value={{ todos, addTodo, toggleTodo, chats, addChat, activeChat, setActiveChat }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
cd frontend && pnpm test AppContext
```
Expected: All PASS.

- [ ] **Step 5: Wrap root layout with AppProvider**

In `frontend/src/app/layout.tsx`, import and wrap:
```tsx
import { AppProvider } from "@/context/AppContext";

// Inside the body:
<body className={...}>
  <AppProvider>
    {children}
  </AppProvider>
</body>
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: add AppContext for todos and chat sessions"
```

---

## Task 6: useProfileGuard Hook

**Files:**
- Create: `frontend/src/hooks/useProfileGuard.ts`
- Test: `frontend/__tests__/hooks/useProfileGuard.test.ts`

- [ ] **Step 1: Write failing tests**

Create `frontend/__tests__/hooks/useProfileGuard.test.ts`:
```ts
import { renderHook } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import * as profile from "@/lib/profile";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/profile");

const mockPush = jest.fn();
beforeEach(() => {
  jest.mocked(useRouter).mockReturnValue({ push: mockPush } as any);
  mockPush.mockClear();
});

describe("useProfileGuard", () => {
  it("redirects to /chat when profile is complete", () => {
    jest.mocked(profile.isComplete).mockReturnValue(true);
    renderHook(() => useProfileGuard("onboarding"));
    expect(mockPush).toHaveBeenCalledWith("/chat");
  });

  it("redirects to /onboarding when profile is incomplete on chat page", () => {
    jest.mocked(profile.isComplete).mockReturnValue(false);
    renderHook(() => useProfileGuard("chat"));
    expect(mockPush).toHaveBeenCalledWith("/onboarding");
  });

  it("does not redirect on welcome page when profile is incomplete", () => {
    jest.mocked(profile.isComplete).mockReturnValue(false);
    renderHook(() => useProfileGuard("welcome"));
    expect(mockPush).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
cd frontend && pnpm test useProfileGuard
```
Expected: FAIL.

- [ ] **Step 3: Implement the hook**

Create `frontend/src/hooks/useProfileGuard.ts`:
```ts
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isComplete } from "@/lib/profile";

type PageContext = "welcome" | "onboarding" | "chat";

export function useProfileGuard(context: PageContext) {
  const router = useRouter();

  useEffect(() => {
    const complete = isComplete();
    if (context === "onboarding" && complete) {
      router.push("/chat");
    } else if (context === "chat" && !complete) {
      router.push("/onboarding");
    }
    // welcome: no redirect — page handles its own CTA
  }, [context, router]);
}
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
cd frontend && pnpm test useProfileGuard
```
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add useProfileGuard hook for client-side redirect logic"
```

---

## Task 7: Onboarding Components

**Files:**
- Create: `frontend/src/components/onboarding/ChipSelect.tsx`
- Create: `frontend/src/components/onboarding/YesNoToggle.tsx`
- Create: `frontend/src/components/onboarding/LanguageCombobox.tsx`
- Create: `frontend/src/components/onboarding/ProgressDots.tsx`
- Create: `frontend/src/components/onboarding/QuestionCard.tsx`
- Test: `frontend/__tests__/components/ChipSelect.test.tsx`
- Test: `frontend/__tests__/components/ProgressDots.test.tsx`

- [ ] **Step 1: Write failing tests for ChipSelect**

Create `frontend/__tests__/components/ChipSelect.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChipSelect } from "@/components/onboarding/ChipSelect";

const options = ["Option A", "Option B", "Option C"];

describe("ChipSelect", () => {
  it("renders all options", () => {
    render(<ChipSelect options={options} value={null} onChange={() => {}} />);
    options.forEach((opt) => expect(screen.getByText(opt)).toBeInTheDocument());
  });

  it("marks the selected option", () => {
    render(<ChipSelect options={options} value="Option B" onChange={() => {}} />);
    expect(screen.getByText("Option B").closest("[data-selected]")).toBeTruthy();
  });

  it("calls onChange when an option is clicked", async () => {
    const onChange = jest.fn();
    render(<ChipSelect options={options} value={null} onChange={onChange} />);
    await userEvent.click(screen.getByText("Option A"));
    expect(onChange).toHaveBeenCalledWith("Option A");
  });
});
```

- [ ] **Step 2: Write failing tests for ProgressDots**

Create `frontend/__tests__/components/ProgressDots.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import { ProgressDots } from "@/components/onboarding/ProgressDots";

describe("ProgressDots", () => {
  it("renders the correct number of dots", () => {
    render(<ProgressDots total={5} current={2} />);
    const dots = screen.getAllByRole("presentation");
    expect(dots).toHaveLength(5);
  });

  it("marks dots up to current as filled", () => {
    render(<ProgressDots total={5} current={2} />);
    const dots = screen.getAllByRole("presentation");
    expect(dots[0]).toHaveAttribute("data-filled", "true");
    expect(dots[1]).toHaveAttribute("data-filled", "true");
    expect(dots[2]).toHaveAttribute("data-filled", "false");
  });
});
```

- [ ] **Step 3: Run tests — confirm they fail**

```bash
cd frontend && pnpm test ChipSelect ProgressDots
```
Expected: FAIL — modules not found.

- [ ] **Step 4: Implement ChipSelect**

Create `frontend/src/components/onboarding/ChipSelect.tsx`:
```tsx
interface ChipSelectProps {
  options: readonly string[];
  value: string | null;
  onChange: (value: string) => void;
}

export function ChipSelect({ options, value, onChange }: ChipSelectProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option}
          data-selected={option === value ? true : undefined}
          onClick={() => onChange(option)}
          className={`
            px-4 py-2 rounded-full border text-sm font-medium transition-colors
            ${option === value
              ? "border-[--color-accent] bg-[--color-accent] text-white"
              : "border-[--color-border] bg-white text-[--color-text] hover:border-[--color-accent]"
            }
          `}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Implement ProgressDots**

Create `frontend/src/components/onboarding/ProgressDots.tsx`:
```tsx
interface ProgressDotsProps {
  total: number;
  current: number; // 0-indexed: number of completed steps
}

export function ProgressDots({ total, current }: ProgressDotsProps) {
  return (
    <div className="flex gap-2 justify-center">
      {Array.from({ length: total }).map((_, i) => (
        <span
          key={i}
          role="presentation"
          data-filled={i < current ? "true" : "false"}
          className={`
            w-2 h-2 rounded-full transition-colors
            ${i < current ? "bg-[--color-accent]" : "bg-[--color-border]"}
          `}
        />
      ))}
    </div>
  );
}
```

- [ ] **Step 6: Implement YesNoToggle**

Create `frontend/src/components/onboarding/YesNoToggle.tsx`:
```tsx
interface YesNoToggleProps {
  value: "yes" | "no" | null;
  onChange: (value: "yes" | "no") => void;
  question?: string;
}

export function YesNoToggle({ value, onChange }: YesNoToggleProps) {
  return (
    <div className="flex gap-3">
      {(["yes", "no"] as const).map((opt) => (
        <button
          key={opt}
          data-selected={opt === value ? true : undefined}
          onClick={() => onChange(opt)}
          className={`
            px-8 py-3 rounded-full border text-sm font-medium capitalize transition-colors
            ${opt === value
              ? "border-[--color-accent] bg-[--color-accent] text-white"
              : "border-[--color-border] bg-white text-[--color-text] hover:border-[--color-accent]"
            }
          `}
        >
          {opt === "yes" ? "Yes" : "No"}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 7: Implement LanguageCombobox**

This uses shadcn/ui Combobox (Popover + Command). First install if not already:
```bash
cd frontend && pnpm dlx shadcn@latest add command popover
```

Create `frontend/src/components/onboarding/LanguageCombobox.tsx`:
```tsx
"use client";

import { useState, useMemo } from "react";
import ISO6391 from "iso-639-1";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

const languageNames = new Intl.DisplayNames(["en"], { type: "language" });

const ALL_LANGUAGES = ISO6391.getAllCodes().map((code) => ({
  code,
  name: languageNames.of(code) ?? ISO6391.getName(code),
})).sort((a, b) => a.name.localeCompare(b.name));

interface LanguageComboboxProps {
  value: string[]; // array of display names
  onChange: (value: string[]) => void;
}

export function LanguageCombobox({ value, onChange }: LanguageComboboxProps) {
  const [open, setOpen] = useState(false);

  function toggle(name: string) {
    if (value.includes(name)) {
      onChange(value.filter((v) => v !== name));
    } else {
      onChange([...value, name]);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((lang) => (
            <Badge key={lang} variant="secondary" className="gap-1">
              {lang}
              <button onClick={() => toggle(lang)} className="ml-1 text-xs">×</button>
            </Badge>
          ))}
        </div>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button className="w-full text-left px-3 py-2 border border-[--color-border] rounded-[--radius] text-sm text-[--color-text-muted]">
            {value.length === 0 ? "Search languages…" : "Add another language…"}
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-0">
          <Command>
            <CommandInput placeholder="Search…" />
            <CommandEmpty>No language found.</CommandEmpty>
            <CommandGroup className="max-h-60 overflow-auto">
              {ALL_LANGUAGES.map(({ code, name }) => (
                <CommandItem
                  key={code}
                  value={name}
                  onSelect={() => { toggle(name!); }}
                >
                  {value.includes(name!) ? "✓ " : ""}{name}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
```

- [ ] **Step 8: Implement QuestionCard**

Create `frontend/src/components/onboarding/QuestionCard.tsx`:
```tsx
"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface QuestionCardProps {
  children: ReactNode;
  direction?: "forward" | "back";
}

const variants = {
  enter: (direction: "forward" | "back") => ({
    y: direction === "forward" ? 40 : -40,
    opacity: 0,
  }),
  center: { y: 0, opacity: 1 },
  exit: (direction: "forward" | "back") => ({
    y: direction === "forward" ? -40 : 40,
    opacity: 0,
  }),
};

export function QuestionCard({ children, direction = "forward" }: QuestionCardProps) {
  return (
    <motion.div
      custom={direction}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className="w-full max-w-lg bg-white rounded-[--radius] border border-[--color-border] p-8 shadow-sm"
    >
      {children}
    </motion.div>
  );
}
```

- [ ] **Step 9: Run tests — confirm ChipSelect and ProgressDots pass**

```bash
cd frontend && pnpm test ChipSelect ProgressDots
```
Expected: All PASS.

- [ ] **Step 10: Commit**

```bash
git add -A && git commit -m "feat: add onboarding components (ChipSelect, ProgressDots, YesNoToggle, LanguageCombobox, QuestionCard)"
```

---

## Task 8: Onboarding Page

**Files:**
- Create: `frontend/src/app/onboarding/page.tsx`

- [ ] **Step 1: Create the onboarding page**

Create `frontend/src/app/onboarding/page.tsx`:
```tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { LanguageCombobox } from "@/components/onboarding/LanguageCombobox";
import { ProgressDots } from "@/components/onboarding/ProgressDots";
import { QuestionCard } from "@/components/onboarding/QuestionCard";
import { getField, setField, getMissingFields, REQUIRED_FIELDS } from "@/lib/profile";
import { NATIONALITY_OPTIONS } from "@/lib/constants/nationality-options";
import { PURPOSE_OPTIONS } from "@/lib/constants/purpose-types";
import { OCCUPATION_OPTIONS } from "@/lib/constants/occupation-types";
import { REGISTRATION_OPTIONS } from "@/lib/constants/registration-status";
import { HOUSING_OPTIONS } from "@/lib/constants/housing-options";
import { SALARY_BANDS } from "@/lib/constants/salary-bands";
import { RESIDENCY_OPTIONS } from "@/lib/constants/residency-options";
import { useProfileGuard } from "@/hooks/useProfileGuard";

interface Question {
  key: string;
  label: string;
  sublabel?: string;
  type: "chip" | "yesno" | "language";
  options?: readonly string[];
}

const QUESTIONS: Question[] = [
  { key: "nationality", label: "What is your nationality / citizenship status?", type: "chip", options: NATIONALITY_OPTIONS },
  { key: "purpose_of_stay", label: "What is your main reason for coming to the Netherlands?", type: "chip", options: PURPOSE_OPTIONS },
  { key: "employment_situation", label: "What is your employment situation?", type: "chip", options: OCCUPATION_OPTIONS },
  { key: "registration_status", label: "What is your current registration status in the Netherlands?", type: "chip", options: REGISTRATION_OPTIONS },
  { key: "has_fiscal_partner", label: "Do you have a fiscal (registered) partner?", sublabel: "Married, registered partnership, or cohabiting at the same address.", type: "yesno" },
  { key: "housing_situation", label: "What is your current or planned housing situation?", type: "chip", options: HOUSING_OPTIONS },
  { key: "salary_band", label: "What is your gross annual salary (or expected income)?", type: "chip", options: SALARY_BANDS },
  { key: "age_bracket", label: "Are you under 30 years old?", sublabel: "This affects eligibility for the HSM permit and 30% ruling.", type: "yesno" },
  { key: "prior_nl_residency", label: "Have you previously lived in the Netherlands?", type: "chip", options: RESIDENCY_OPTIONS },
  { key: "languages", label: "What languages do you speak?", type: "language" },
];

export default function OnboardingPage() {
  useProfileGuard("onboarding");
  const router = useRouter();

  // Determine start index from partial progress
  const getStartIndex = () => {
    const missing = getMissingFields();
    if (missing.length === 0) return 0;
    const firstMissingKey = missing[0];
    const idx = QUESTIONS.findIndex((q) => q.key === firstMissingKey);
    return idx >= 0 ? idx : 0;
  };

  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const start = getStartIndex();
    setStepIndex(start);
    // Pre-fill answers from localStorage
    const saved: Record<string, string | string[]> = {};
    QUESTIONS.forEach((q) => {
      const val = getField(q.key as any);
      if (val) {
        try { saved[q.key] = JSON.parse(val); }
        catch { saved[q.key] = val; }
      }
    });
    setAnswers(saved);
  }, []);

  const currentQuestion = QUESTIONS[stepIndex];
  const currentAnswer = answers[currentQuestion?.key ?? ""];
  const hasAnswer = currentAnswer !== undefined && currentAnswer !== null &&
    (Array.isArray(currentAnswer) ? currentAnswer.length > 0 : currentAnswer !== "");
  const isFirst = stepIndex === 0;
  const isLast = stepIndex === QUESTIONS.length - 1;

  function setAnswer(key: string, value: string | string[]) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit() {
    const key = currentQuestion.key;
    const value = answers[key];
    const stored = Array.isArray(value) ? JSON.stringify(value) : String(value);
    setField(key as any, stored);

    if (isLast) {
      setCompleted(true);
    } else {
      setDirection("forward");
      setStepIndex((i) => i + 1);
    }
  }

  function handleBack() {
    setDirection("back");
    setStepIndex((i) => i - 1);
  }

  function handleForward() {
    setDirection("forward");
    setStepIndex((i) => i + 1);
  }

  const answeredCount = QUESTIONS.filter((q) => {
    const val = answers[q.key];
    return val !== undefined && (Array.isArray(val) ? val.length > 0 : val !== "");
  }).length;

  if (completed) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-[--color-bg] px-4">
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="w-full max-w-lg bg-white rounded-[--radius] border border-[--color-border] p-8 shadow-sm text-center"
        >
          <div className="text-4xl mb-4">🎉</div>
          <h2 className="text-xl font-semibold mb-2">You're all set!</h2>
          <p className="text-[--color-text-muted] mb-6">
            We've saved your details and will use them to give you personalised advice.
          </p>
          <button
            onClick={() => router.push("/chat")}
            className="px-6 py-3 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white rounded-[--radius] font-medium transition-colors"
          >
            Start chatting with Patty
          </button>
        </motion.div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-[--color-bg] px-4">
      {/* Back / Forward buttons */}
      <div className="w-full max-w-lg flex justify-between mb-4">
        <button
          onClick={handleBack}
          disabled={isFirst}
          className="text-sm text-[--color-text-muted] disabled:opacity-30 hover:text-[--color-text] transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={handleForward}
          disabled={!hasAnswer || isLast}
          className="text-sm text-[--color-text-muted] disabled:opacity-30 hover:text-[--color-text] transition-colors"
        >
          Forward →
        </button>
      </div>

      {/* Question card */}
      <AnimatePresence mode="wait" custom={direction}>
        <QuestionCard key={stepIndex} direction={direction}>
          <h2 className="text-lg font-semibold mb-1">{currentQuestion.label}</h2>
          {currentQuestion.sublabel && (
            <p className="text-sm text-[--color-text-muted] mb-4">{currentQuestion.sublabel}</p>
          )}
          <div className="mt-4">
            {currentQuestion.type === "chip" && (
              <ChipSelect
                options={currentQuestion.options!}
                value={(currentAnswer as string) ?? null}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
            {currentQuestion.type === "yesno" && (
              <YesNoToggle
                value={(currentAnswer as "yes" | "no") ?? null}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
            {currentQuestion.type === "language" && (
              <LanguageCombobox
                value={(currentAnswer as string[]) ?? []}
                onChange={(v) => setAnswer(currentQuestion.key, v)}
              />
            )}
          </div>
          <div className="mt-6">
            <button
              onClick={handleSubmit}
              disabled={!hasAnswer}
              className="w-full py-2.5 bg-[--color-accent] hover:bg-[--color-accent-hover] disabled:opacity-40 text-white rounded-[--radius] font-medium transition-colors"
            >
              {isLast ? "Finish" : "Next"}
            </button>
          </div>
        </QuestionCard>
      </AnimatePresence>

      {/* Progress dots */}
      <div className="mt-6">
        <ProgressDots total={QUESTIONS.length} current={answeredCount} />
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Verify onboarding renders in the browser**

```bash
cd frontend && pnpm dev
```
Navigate to `http://localhost:3000/onboarding`. Confirm:
- A question card renders
- Clicking a chip selects it and enables the "Next" button
- Clicking "Next" animates to the next question
- Progress dots update as questions are answered
- The completion screen appears after the last question

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: implement onboarding flow with animated question cards"
```

---

## Task 9: Welcome Page

**Files:**
- Replace: `frontend/src/app/page.tsx`
- Create: `frontend/src/components/welcome/AnimatedChat.tsx`

- [ ] **Step 1: Create AnimatedChat background component**

Create `frontend/src/components/welcome/AnimatedChat.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";

const SCRIPT = [
  { role: "user", text: "Can you help me get started with my DigiD?" },
  { role: "patty", text: "Of course! DigiD is your digital identity for Dutch government services. First, you'll need a BSN number from your municipality." },
  { role: "user", text: "How do I get a BSN number?" },
  { role: "patty", text: "You get your BSN when you register at your local municipality (gemeente). Book an appointment at the BRP desk — you'll need your passport and proof of address." },
  { role: "user", text: "What documents do I need?" },
  { role: "patty", text: "Bring a valid passport or ID, a completed registration form, and proof of your Dutch address (e.g. rental contract or letter from your landlord)." },
];

export function AnimatedChat() {
  const [visible, setVisible] = useState<number[]>([]);

  useEffect(() => {
    let i = 0;
    function showNext() {
      setVisible((prev) => [...prev, i]);
      i++;
      if (i < SCRIPT.length) {
        setTimeout(showNext, 1800);
      } else {
        // Loop: reset after a pause
        setTimeout(() => {
          setVisible([]);
          i = 0;
          setTimeout(showNext, 600);
        }, 3000);
      }
    }
    const timer = setTimeout(showNext, 800);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none"
         style={{ opacity: 0.18, filter: "blur(1.5px)" }}>
      <div className="w-full max-w-sm flex flex-col gap-3 px-6">
        {SCRIPT.map((msg, i) => (
          <div
            key={i}
            className={`
              transition-all duration-500
              ${visible.includes(i) ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}
              ${msg.role === "user" ? "self-end" : "self-start"}
            `}
          >
            <div className={`
              px-4 py-2 rounded-2xl text-sm max-w-[260px]
              ${msg.role === "user"
                ? "bg-[--color-accent] text-white rounded-br-sm"
                : "bg-[--color-bg-subtle] text-[--color-text] border border-[--color-border] rounded-bl-sm"
              }
            `}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Replace the welcome page**

Replace `frontend/src/app/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { isComplete } from "@/lib/profile";
import { AnimatedChat } from "@/components/welcome/AnimatedChat";

export default function WelcomePage() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (isComplete()) {
      router.push("/chat");
    } else {
      setChecked(true);
    }
  }, [router]);

  if (!checked) return null;

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center bg-white overflow-hidden">
      <AnimatedChat />

      {/* Foreground content */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 flex flex-col items-center text-center px-6"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-[--color-text] leading-tight max-w-2xl">
          Your all-in-one expat moving assistant
        </h1>
        <p className="mt-4 text-[--color-text-muted] text-lg max-w-md">
          Personalised legal and compliance guidance for expats in the Netherlands — cited from official sources.
        </p>
      </motion.div>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="absolute bottom-16 z-10"
      >
        <button
          onClick={() => router.push("/onboarding")}
          className="px-8 py-3.5 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white text-base font-semibold rounded-full shadow-md transition-colors"
        >
          Get Started
        </button>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 3: Verify in browser**

Navigate to `http://localhost:3000`. Confirm:
- Hero text is sharp in the foreground
- Background chat animation is visible but muted (low opacity, slight blur)
- "Get Started" button is at the bottom
- Clicking it navigates to `/onboarding`

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: implement welcome page with animated chat background"
```

---

## Task 10: Shared Sidebar Layout

**Files:**
- Create: `frontend/src/app/(app)/layout.tsx`
- Create: `frontend/src/app/(app)/settings/page.tsx`

- [ ] **Step 1: Create the (app) route group layout with sidebar**

Create `frontend/src/app/(app)/layout.tsx`:
```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Checkbox } from "@/components/ui/checkbox";

interface AppLayoutProps {
  children: React.ReactNode;
}

function isSettingsRoute(pathname: string) {
  return pathname.startsWith("/settings");
}

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const inSettings = isSettingsRoute(pathname);
  const { todos, toggleTodo, chats, activeChat, setActiveChat, addChat } = useAppContext();

  return (
    <div className="flex h-screen overflow-hidden bg-[--color-bg]">
      {/* Sidebar */}
      <aside
        className="flex flex-col border-r border-[--color-border] bg-[--color-bg-subtle]"
        style={{ width: "var(--sidebar-width)", minWidth: "var(--sidebar-width)" }}
      >
        {/* Logo */}
        <div className="px-4 py-4 border-b border-[--color-border]">
          <span className="font-bold text-lg tracking-tight text-[--color-text]">Patty</span>
        </div>

        {/* Nav */}
        <nav className="px-3 py-3 border-b border-[--color-border]">
          {inSettings ? (
            <Link
              href="/chat"
              className="flex items-center gap-2 px-2 py-1.5 text-sm text-[--color-text-muted] hover:text-[--color-text] rounded transition-colors"
            >
              ← Back to Patty
            </Link>
          ) : (
            <Link
              href="/settings/profile"
              className="flex items-center gap-2 px-2 py-1.5 text-sm text-[--color-text-muted] hover:text-[--color-text] rounded transition-colors"
            >
              ⚙ Settings
            </Link>
          )}
          {inSettings && (
            <div className="mt-2">
              <Link
                href="/settings/profile"
                className={`block px-2 py-1.5 text-sm rounded transition-colors ${
                  pathname === "/settings/profile"
                    ? "bg-[--color-accent] text-white"
                    : "text-[--color-text-muted] hover:text-[--color-text]"
                }`}
              >
                Profile
              </Link>
            </div>
          )}
        </nav>

        {/* Todos */}
        {!inSettings && (
          <div className="flex-1 overflow-y-auto px-3 py-3 border-b border-[--color-border]">
            <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted] mb-2 px-2">Tasks</p>
            {todos.length === 0 ? (
              <p className="text-xs text-[--color-text-muted] px-2">No tasks yet — Patty will suggest things as you chat.</p>
            ) : (
              <ul className="space-y-1">
                {todos.map((todo) => (
                  <li key={todo.id} className="flex items-start gap-2 px-2 py-1">
                    <Checkbox
                      checked={todo.completed}
                      onCheckedChange={() => toggleTodo(todo.id)}
                      className="mt-0.5"
                    />
                    <span className={`text-sm ${todo.completed ? "line-through text-[--color-text-muted]" : "text-[--color-text]"}`}>
                      {todo.text}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Previous chats */}
        {!inSettings && (
          <div className="px-3 py-3">
            <div className="flex items-center justify-between mb-2 px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted]">Chats</p>
              <button
                onClick={() => addChat("New chat")}
                className="text-xs text-[--color-accent] hover:underline"
              >
                + New
              </button>
            </div>
            <p className="text-xs text-[--color-text-muted] px-2 mb-2 italic">Session only</p>
            {chats.length === 0 ? (
              <p className="text-xs text-[--color-text-muted] px-2">No previous chats this session.</p>
            ) : (
              <ul className="space-y-0.5">
                {chats.map((chat) => (
                  <li key={chat.id}>
                    <button
                      onClick={() => setActiveChat(chat.id)}
                      className={`w-full text-left px-2 py-1.5 text-sm rounded transition-colors truncate ${
                        activeChat === chat.id
                          ? "bg-[--color-accent] text-white"
                          : "text-[--color-text-muted] hover:text-[--color-text]"
                      }`}
                    >
                      {chat.title}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Create settings redirect**

Create `frontend/src/app/(app)/settings/page.tsx`:
```tsx
import { redirect } from "next/navigation";

export default function SettingsPage() {
  redirect("/settings/profile");
}
```

- [ ] **Step 3: Verify sidebar renders**

Navigate to `http://localhost:3000/chat` (even before chat page is built, the sidebar should render). Confirm sidebar appears on the left.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: add shared (app) layout with sidebar"
```

---

## Task 11: Chat API Route Handler

**Files:**
- Create: `frontend/src/app/api/chat/route.ts`

- [ ] **Step 1: Create the route handler**

Create `frontend/src/app/api/chat/route.ts`:
```ts
import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.text();

  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    });
  } catch {
    return new Response(JSON.stringify({ error: "Could not reach backend" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!response.ok) {
    return new Response(JSON.stringify({ error: "Backend error" }), {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Stream the response back to the client
  return new Response(response.body, {
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "text/event-stream",
      "Cache-Control": "no-cache",
    },
  });
}
```

- [ ] **Step 2: Add BACKEND_URL to env files**

In the repo root `.env.example`, add:
```
BACKEND_URL=http://localhost:8000
```

Also create `frontend/.env.local` (not committed — add to `.gitignore`) with the same value so Next.js picks it up at runtime:
```
BACKEND_URL=http://localhost:8000
```

`BACKEND_URL` is a server-side variable (no `NEXT_PUBLIC_` prefix) — it is only read inside the route handler, never exposed to the browser.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: add /api/chat route handler proxying to FastAPI backend"
```

---

## Task 12: Chat Page

**Files:**
- Create: `frontend/src/app/(app)/chat/page.tsx`

> **Note on `@assistant-ui/react`:** The spec originally called for using the `<Thread>` component from `@assistant-ui/react`. However, its Tailwind v4 compatibility is unconfirmed and attempting to install it via `pnpm dlx shadcn@latest add https://r.assistant-ui.com/thread` may produce broken class names. This task implements a custom message list and input bar using `useChat` directly — a deliberate, simpler alternative that is fully functional and easier to maintain given the Tailwind v4 constraint. The `@assistant-ui/react` and `@assistant-ui/react-ai-sdk` packages installed in Task 1 can be removed from `package.json` if unused.

- [ ] **Step 1: Remove unused @assistant-ui packages (if install in Task 1 failed or is not needed)**

```bash
cd frontend && pnpm remove @assistant-ui/react @assistant-ui/react-ai-sdk 2>/dev/null || true
```

- [ ] **Step 2: Create the chat page**

Create `frontend/src/app/(app)/chat/page.tsx`:
```tsx
"use client";

import { useEffect } from "react";
import { useChat } from "@ai-sdk/react";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import { useAppContext } from "@/context/AppContext";

export default function ChatPage() {
  useProfileGuard("chat");
  const { addChat } = useAppContext();

  const { messages, input, handleInputChange, handleSubmit, status, error, reload } = useChat({
    api: "/api/chat",
  });

  // Register this session in sidebar on first message
  useEffect(() => {
    if (messages.length === 1 && messages[0].role === "user") {
      addChat(messages[0].content.slice(0, 40));
    }
  }, [messages, addChat]);

  const isStreaming = status === "streaming" || status === "submitted";

  return (
    <div className="flex flex-col h-full">
      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-[--color-text-muted] text-sm">Start a new conversation with Patty</p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`
              max-w-[70%] px-4 py-2.5 rounded-2xl text-sm
              ${msg.role === "user"
                ? "bg-[--color-accent] text-white rounded-br-sm"
                : "bg-[--color-bg-subtle] text-[--color-text] border border-[--color-border] rounded-bl-sm"
              }
            `}>
              {msg.content}
            </div>
          </div>
        ))}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="px-4 py-2.5 rounded-2xl bg-[--color-bg-subtle] border border-[--color-border] text-sm text-[--color-text-muted] rounded-bl-sm">
              <span className="animate-pulse">Patty is thinking…</span>
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <div className="text-sm text-[--color-error] flex items-center gap-2">
              Something went wrong. Please try again.
              <button onClick={reload} className="underline">Retry</button>
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-[--color-border] px-6 py-4 flex gap-3 items-end"
      >
        <textarea
          value={input}
          onChange={handleInputChange}
          placeholder="Ask Patty anything…"
          rows={1}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e as any);
            }
          }}
          className="flex-1 resize-none border border-[--color-border] rounded-[--radius] px-3 py-2 text-sm text-[--color-text] placeholder:text-[--color-text-muted] focus:outline-none focus:border-[--color-accent]"
        />
        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="px-4 py-2 bg-[--color-accent] hover:bg-[--color-accent-hover] disabled:opacity-40 text-white text-sm font-medium rounded-[--radius] transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 3: Verify chat page renders**

Navigate to `http://localhost:3000/chat`. Confirm:
- Empty state message shows
- Input bar is at the bottom
- Typing and pressing Enter sends a message (it will error since FastAPI isn't running — that's expected)

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: implement chat page with streaming via useChat"
```

---

## Task 13: Settings — Profile Page

**Files:**
- Create: `frontend/src/app/(app)/settings/profile/page.tsx`

- [ ] **Step 1: Create the profile settings page**

Create `frontend/src/app/(app)/settings/profile/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { getField, setField } from "@/lib/profile";
import { ChipSelect } from "@/components/onboarding/ChipSelect";
import { YesNoToggle } from "@/components/onboarding/YesNoToggle";
import { LanguageCombobox } from "@/components/onboarding/LanguageCombobox";
import { NATIONALITY_OPTIONS } from "@/lib/constants/nationality-options";
import { PURPOSE_OPTIONS } from "@/lib/constants/purpose-types";
import { OCCUPATION_OPTIONS } from "@/lib/constants/occupation-types";
import { REGISTRATION_OPTIONS } from "@/lib/constants/registration-status";
import { HOUSING_OPTIONS } from "@/lib/constants/housing-options";
import { SALARY_BANDS } from "@/lib/constants/salary-bands";
import { RESIDENCY_OPTIONS } from "@/lib/constants/residency-options";

interface FieldDef {
  key: string;
  label: string;
  type: "chip" | "yesno" | "language";
  options?: readonly string[];
}

const FIELDS: FieldDef[] = [
  { key: "nationality", label: "Nationality / citizenship", type: "chip", options: NATIONALITY_OPTIONS },
  { key: "purpose_of_stay", label: "Purpose of stay", type: "chip", options: PURPOSE_OPTIONS },
  { key: "employment_situation", label: "Employment situation", type: "chip", options: OCCUPATION_OPTIONS },
  { key: "registration_status", label: "Registration / BSN status", type: "chip", options: REGISTRATION_OPTIONS },
  { key: "has_fiscal_partner", label: "Fiscal partner?", type: "yesno" },
  { key: "housing_situation", label: "Housing situation", type: "chip", options: HOUSING_OPTIONS },
  { key: "salary_band", label: "Gross annual salary", type: "chip", options: SALARY_BANDS },
  { key: "age_bracket", label: "Under 30?", type: "yesno" },
  { key: "prior_nl_residency", label: "Prior NL residency", type: "chip", options: RESIDENCY_OPTIONS },
  { key: "languages", label: "Languages spoken", type: "language" },
];

function loadValues(): Record<string, string | string[]> {
  const vals: Record<string, string | string[]> = {};
  FIELDS.forEach(({ key }) => {
    const raw = getField(key as any);
    if (raw === null) return;
    try { vals[key] = JSON.parse(raw); }
    catch { vals[key] = raw; }
  });
  return vals;
}

export default function ProfilePage() {
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(loadValues);
  const [draft, setDraft] = useState(saved);

  function handleEdit() {
    setDraft(saved);
    setEditing(true);
  }

  function handleSave() {
    FIELDS.forEach(({ key }) => {
      const val = draft[key];
      if (val !== undefined) {
        setField(key as any, Array.isArray(val) ? JSON.stringify(val) : String(val));
      }
    });
    setSaved(draft);
    setEditing(false);
  }

  function handleCancel() {
    setDraft(saved);
    setEditing(false);
  }

  function displayValue(key: string, val: string | string[] | undefined): string {
    if (val === undefined || val === null) return "—";
    if (Array.isArray(val)) return val.length > 0 ? val.join(", ") : "—";
    return val;
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-[--color-text]">Profile</h1>
        {!editing ? (
          <button
            onClick={handleEdit}
            className="text-sm text-[--color-accent] hover:underline"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-3">
            <button onClick={handleCancel} className="text-sm text-[--color-text-muted] hover:text-[--color-text]">
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="text-sm px-4 py-1.5 bg-[--color-accent] hover:bg-[--color-accent-hover] text-white rounded-[--radius] transition-colors"
            >
              Save
            </button>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {FIELDS.map(({ key, label, type, options }) => (
          <div key={key} className="border-b border-[--color-border] pb-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted] mb-2">{label}</p>
            {!editing ? (
              <p className="text-sm text-[--color-text]">{displayValue(key, saved[key])}</p>
            ) : (
              <div>
                {type === "chip" && (
                  <ChipSelect
                    options={options!}
                    value={(draft[key] as string) ?? null}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
                  />
                )}
                {type === "yesno" && (
                  <YesNoToggle
                    value={(draft[key] as "yes" | "no") ?? null}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
                  />
                )}
                {type === "language" && (
                  <LanguageCombobox
                    value={(draft[key] as string[]) ?? []}
                    onChange={(v) => setDraft((prev) => ({ ...prev, [key]: v }))}
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify profile page in browser**

Navigate to `http://localhost:3000/settings/profile`. Confirm:
- All profile fields display in read-only mode
- "Edit" button switches to edit mode with the same input components as onboarding
- "Save" persists to localStorage; "Cancel" reverts changes

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: implement settings profile page with read/edit mode"
```

---

## Task 14: Final Wiring + Smoke Test

- [ ] **Step 1: Run the full test suite**

```bash
cd frontend && pnpm test
```
Expected: All tests PASS.

- [ ] **Step 2: Run a production build**

```bash
cd frontend && pnpm build
```
Expected: Build succeeds with no errors. If Tailwind v4 class errors appear from `@assistant-ui` components, fix them in the installed source files.

- [ ] **Step 3: End-to-end smoke test**

With `pnpm dev` running, walk through the full flow:
1. Open `http://localhost:3000` — welcome page with animated background and "Get Started"
2. Click "Get Started" — onboarding loads on question 1
3. Answer all 10 questions — verify animations, progress dots, and the completion screen
4. Click "Start chatting with Patty" — lands on `/chat`
5. Verify sidebar shows (logo, settings link, empty todos, empty chats)
6. Navigate to `/settings/profile` — all answers visible in read-only mode
7. Click "Edit", change a value, click "Save" — value updates and persists after page refresh
8. Click "Back to Patty" — returns to `/chat`
9. Reload the page at `/` — because profile is complete, should redirect to `/chat`

- [ ] **Step 4: Final commit**

```bash
git add -A && git commit -m "feat: complete Patty UI — welcome, onboarding, chat, and settings"
```

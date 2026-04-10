# Login & Registration (`/login`)

## Purpose

This is the gateway to the app. Every user must have an account to use Patty — there is no anonymous access. The login page handles both signing in (existing users) and registering (new users) in a single view with a tab toggle. It is intentionally minimal: username and password only, no email verification, no OAuth.

After a successful login, the user is redirected into the app. After a successful registration, the user is redirected to onboarding so they can provide profile details for personalized answers.

---

## Features

### Tab toggle: Sign In / Register

- Two modes on the same page, toggled via a tab-style control at the top of the card.
- **Register** is the default tab (during development, most visitors will be new users trying the demo).
- Switching tabs clears any displayed error message but preserves field values.

### Form fields

Both tabs share the same two fields:

- **Username** — text input, required. Trimmed of whitespace before submission.
- **Password** — text input (type `password`), required. Minimum 8 characters (enforced client-side before submission).

### Sign In behaviour

- Calls `POST /auth/login` with `{ username, password }`.
- On success (200): the backend sets an httpOnly session cookie. Redirect to `/chat`.
- On 401: display the backend's error detail ("Invalid credentials") below the form.

### Register behaviour

- Calls `POST /auth/register` with `{ username, password }`.
- On success (201): the account is created but the user is **not** logged in yet. Immediately call `POST /auth/login` with the same credentials to establish a session, then redirect to `/onboarding`.
- On 409 ("Username already taken"): display "This username is already taken" below the form.

### Already logged in

- On mount, use the `useAuth` hook to check if the user already has a valid session.
- If `user` is non-null (already logged in), redirect to `/chat` instead of showing the login form.
- While `isLoading` is true, render nothing (`return null`) to avoid a flash.

### Error display

- A single error message area below the submit button.
- Errors are cleared when the user switches tabs or starts typing.
- Only show errors returned by the backend — no speculative client-side validation messages beyond the minimum password length.

---

## Implementation steps

### Files to create

| File | Purpose |
|---|---|
| `src/app/login/page.tsx` | Login / register page (Client Component) — replaces the current scaffold |
| `src/lib/api/auth.ts` | API call functions: `login()`, `register()` |

### shadcn/ui components to install

```bash
npx shadcn@latest add input label tabs
```

### Step 1: Create the API call functions

Create `src/lib/api/auth.ts` with two functions that call the backend auth endpoints. All functions use `credentials: "include"` so the browser sends/receives the session cookie.

```ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function login(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Login failed");
  }
}

export async function register(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body?.detail ?? "Registration failed");
  }
}
```

Define a simple `ApiError` class at the top of the file so callers can inspect `status`:

```ts
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
```

### Step 2: Page shell with auth redirect

Replace the scaffold in `src/app/login/page.tsx` with a Client Component (`"use client"`).

- Use the `useAuth` hook.
- While `isLoading`, return `null`.
- If `user` is non-null, redirect to `/chat` using `useRouter().push("/chat")`.
- Otherwise, render the login card (Steps 3–5).

### Step 3: Tab toggle and form layout

Build the card layout, centered on the page (`min-h-screen`, `flex items-center justify-center`):

- A card container that visually separates the form from the page background (rounded border, `bg-card`, `shadow-md`, max-width ~`sm`, padding `p-8`).
- A shadcn `<Tabs>` component at the top with two tabs: "Sign In" (value `"login"`) and "Register" (value `"register"`).
- Track the active tab in state: `const [tab, setTab] = useState<"login" | "register">("register")`.
- When tab changes, clear any error message.

### Step 4: Form fields and submission

Inside each `<TabsContent>`, render a `<form>` with:

- `<Label>` + `<Input>` for username (autoFocus, autoComplete `"username"`).
- `<Label>` + `<Input type="password">` for password (autoComplete `"current-password"` on sign-in, `"new-password"` on register).
- A `<Button type="submit">` with text "Sign In" or "Create Account" depending on the active tab.
- Disable the button while submitting (track `isSubmitting` state).

On submit:

- **Sign In tab:** Call `login(username, password)`. On success, `router.push("/chat")`. On `ApiError`, set the error message.
- **Register tab:** Call `register(username, password)`, then immediately `login(username, password)`. On success, `router.push("/onboarding")`. On `ApiError` from register (status 409), show "This username is already taken". On other errors, show the error message.

### Step 5: Error display

- Below the submit button, conditionally render a `<p>` with the error message.
- Style: `text-sm text-destructive`.
- Clear the error on tab switch (`setTab` callback) and on any input change.

### Step 6: Verify

- Run `pnpm dev` and open `http://localhost:3000/login`.
- Confirm the two tabs render and switch correctly.
- Try registering a new account — confirm redirect to `/onboarding`.
- Try logging in with that account — confirm redirect to `/chat`.
- Try registering a duplicate username — confirm "This username is already taken" appears.
- Try logging in with wrong credentials — confirm "Invalid credentials" appears.
- Navigate to `/login` while already logged in — confirm redirect to `/chat`.
- Check on a narrow viewport (~375px) that the form is usable.

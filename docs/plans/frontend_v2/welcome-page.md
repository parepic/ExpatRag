# Welcome Page (`/`)

## Purpose

This is the first page a new visitor sees. Its job is to answer three questions within seconds:

1. **Who is this for?** — Expats moving to or settling in the Netherlands.
2. **What does it do?** — An AI assistant that answers your specific legal and compliance questions (visa, tax, registration, inburgering) with cited, trustworthy responses from official Dutch government sources.
3. **Why should I use it?** — You get personalized answers based on your situation, backed by real sources — not generic advice, not hallucinated claims, not EUR 200/hr lawyer fees. It saves you time and stress.

The page must convert visitors into users. A clear call-to-action directs them to sign up. No login is required to view this page.

---

## Features

### Hero content
- Large, bold headline that communicates the app's purpose (e.g. "Your all-in-one expat moving assistant")
- Subtitle that reinforces the value: personalized, cited answers from official Dutch sources
- Both should be immediately visible without scrolling

### Animated chat background
- A blurred, low-opacity background showing simulated chat conversations
- Demonstrates the app in action — a user asking about DigiD, 30% ruling, BSN registration, etc., and Patty responding with helpful answers
- Built as a React component with scripted message sequences that loop
- Should not compete with the hero text — purely atmospheric

### Value highlights
- Below the hero, a section with 3-4 concise selling points (icon + short text), e.g.:
  - "Every answer cited from official Dutch sources" 
  - "Personalized to your visa, job, and situation"
  - "Ask in plain language — no legal jargon needed"
  - "Free to use — no lawyer fees"
- Should be visible on first scroll or even without scrolling on larger screens
- Keeps the same clean, white aesthetic as the old welcome page

### Call-to-action
- A prominent "Get Started" button centered below the hero text
- Navigates to `/login` where users can register a new account or sign in
- This is the only interactive element on the page

### Behaviour
- Public page — no auth required
- If a user is already logged in (valid session cookie), redirect to `/chat` instead of showing the welcome page

---

## Implementation steps

### Files to create

| File | Purpose |
|---|---|
| `src/app/page.tsx` | Welcome page (Client Component) |
| `src/components/welcome/AnimatedChat.tsx` | Animated chat background component |

### Step 1: Create the AnimatedChat component

Create `src/components/welcome/AnimatedChat.tsx` — a client component (`"use client"`) that renders simulated chat conversations as a blurred background layer.

**How it works:**
- Define 2 conversation scripts as arrays of `{ role: "user" | "patty", text: string }`. Example topics: getting a DigiD/BSN, and the 30% ruling. Each script should have 3 messages (user asks, Patty answers, user follows up, Patty answers again, etc.).
- Render two columns side by side in a grid layout, one per script.
- Each column reveals messages one at a time using `setTimeout` with ~1800ms between messages. After all messages in a script are shown, wait ~3s, then reset and loop.
- Each column starts with a different delay (e.g. 800ms and 2400ms) so they don't animate in sync.
- Messages are styled as chat bubbles: user messages right-aligned with the primary color, Patty messages left-aligned with a bordered card style.
- The entire component is wrapped in a `div` positioned `absolute inset-0` with low opacity (~0.18) and a slight CSS blur (`filter: blur(1.5px)`), plus `pointer-events-none` so it doesn't block clicks.

**Reference:** The old frontend has this exact component at `frontend/src/components/welcome/AnimatedChat.tsx`. Copy the structure and scripts, adjust styling if needed.

### Step 2: Create the welcome page

Create `src/app/page.tsx` as a Client Component (`"use client"`).

**Auth redirect check:**
- Use the `useAuth` hook created in Step 1.
- While `isLoading` is true, render nothing (`return null`) to avoid a flash of content.
- If `user` is non-null (logged in), redirect to `/chat` using `useRouter().push("/chat")`.
- If `user` is null and loading is done, render the welcome page.

**Layout (top to bottom):**

1. **AnimatedChat background** — Render the `<AnimatedChat />` component. It positions itself absolutely behind everything.

2. **Hero section** (centered, z-10 so it sits above the background):
   - `<h1>` — Large bold headline, e.g. "Your all-in-one expat moving assistant". Use classes like `text-4xl font-bold md:text-5xl`, max-width ~2xl, centered text.
   - `<p>` — Subtitle below, e.g. "Personalised legal and compliance guidance for expats in the Netherlands — cited from official sources." Muted color, `text-lg`, max-width ~md.

3. **Value highlights** (below hero, still centered):
   - A row (or grid on mobile: stack vertically) of 3–4 cards/items, each with:
     - A small icon or emoji
     - A short text (one line)
   - Example items:
     - "Every answer cited from official Dutch sources"
     - "Personalized to your visa, job, and situation"
     - "Ask in plain language — no legal jargon needed"
     - "Free to use — no lawyer fees"
   - Use `text-sm text-muted-foreground`, subtle styling, no borders or heavy cards — keep it light.

4. **CTA button** (centered, below value highlights or at bottom of viewport):
   - A shadcn/ui `<Button>` with `size="lg"`, rounded, with text "Get Started".
   - `onClick` navigates to `/login` using `useRouter().push("/login")`.

**Styling notes:**
- Full-screen layout: `min-h-screen`, `flex flex-col items-center justify-center`, `bg-background`.
- The hero and CTA should be vertically centered on the viewport. The value highlights sit between them.
- Must look good on mobile (stack elements vertically, reduce font sizes with responsive classes).

### Step 3: Verify

- Run `pnpm dev` and open `http://localhost:3000/`.
- Confirm the animated chat background loops correctly behind the content.
- Confirm the hero text, value highlights, and CTA button are visible and centered.
- Confirm clicking "Get Started" navigates to `/login`.
- Confirm that if you have a valid session cookie, the page redirects to `/chat` instead of rendering.
- Check on a narrow viewport (~375px) that the layout stacks properly.

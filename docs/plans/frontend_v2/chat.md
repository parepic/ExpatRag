# Chat Interface (`/chat`)

## Purpose

This is the core of the app — where users ask questions and get cited, personalized answers about Dutch immigration and compliance. The chat page lets users start new conversations, send messages, receive AI-generated responses with source citations, and return to past conversations from the sidebar.

The backend handles all the heavy lifting (RAG retrieval, answer generation, citation extraction). The frontend's job is to provide a clean conversational UI, display messages and citations clearly, and manage conversation state via the backend API.

---

## Features

### Message display

- Messages are shown in a scrollable thread, ordered chronologically.
- **User messages** are right-aligned with a primary-colored bubble (same visual style as the old frontend's `UserMessage` component).
- **Assistant messages** are left-aligned, plain background, with relaxed leading for readability.
- Assistant messages may contain markdown (headings, lists, links, bold/italic, code blocks). Render using `react-markdown` with `remark-gfm` for GitHub-flavored markdown support.
- The thread auto-scrolls to the bottom when a new message is added.

### Citations

- Each assistant message includes a `citations` array (or `null`). Each citation contains `source_title`, `source_url`, and `content` (the text snippet from the original government source).
- Citations are displayed below the assistant message text as a list of expandable snippet bubbles. Each bubble shows the `source_title` as a header (linked to `source_url`, opens in new tab). Clicking the bubble toggles the `content` snippet open/closed.
- The first citation is expanded by default so users immediately see the source text. The rest are collapsed.
- If a message has no citations (null or empty array), nothing is shown below it.

### Message composer

- A text input fixed at the bottom of the chat area, with a send button.
- Placeholder text: "Ask Patty anything..."
- Submit on Enter (Shift+Enter for newline). The send button is also clickable.
- The input and send button are disabled while waiting for a response.

### Backend API responses

The frontend only uses four fields from each message: `role`, `content`, `citations`, and `created_at`. Other fields in the response (`id`, `chat_id`, `user_id`, `trace_id`) are ignored.

**`POST /chats` and `POST /chats/{chat_id}/messages`** — both accept `{ message }` and return:

```json
{
  "chat_id": "...",
  "user_message": { "role": "user", "content": "...", "citations": null, "created_at": "..." },
  "assistant_message": { "role": "assistant", "content": "...", "citations": [...], "created_at": "..." }
}
```

**`GET /chats/{chat_id}`** — returns the full message history:

```json
{
  "chat_id": "...",
  "messages": [
    { "role": "user", "content": "...", "citations": null, "created_at": "..." },
    { "role": "assistant", "content": "...", "citations": [...], "created_at": "..." }
  ]
}
```

**`GET /chats`** — returns the list of recent chats (no messages):

```json
[
  { "id": "...", "title": "...", "created_at": "..." }
]
```

Each citation in the `citations` array has: `source_title`, `source_url`, and `content` (the text snippet from the source).

### Sending a message

- **New conversation (no `activeChatId` in `ChatContext`):** Call `POST /chats` with `{ message }`. Set `activeChatId` to the returned `chat_id` and render both returned messages.
- **Existing conversation:** Call `POST /chats/{chat_id}/messages` with `{ message }`. Append both returned messages to the thread.
- In both cases, the response is synchronous (no streaming). Show a loading indicator in the message area while waiting.

### Loading state

- While waiting for the backend response, display a visual indicator below the user's message (e.g. a pulsing dot or a skeleton bubble in the assistant message position).
- The composer is disabled during this time to prevent double-sends.

### Empty state

- When there is no active chat (fresh page load, no `activeChatId`), show a centered welcome message: "Start a new conversation with Patty" — same as the old frontend's `ThreadWelcome`.
- Optionally show 2–3 suggestion chips below the welcome text with example questions (e.g. "How do I get a BSN?", "Am I eligible for the 30% ruling?"). Clicking a suggestion sends it as the first message.

### Loading an existing chat

- When the user selects a chat from the sidebar, `activeChatId` is set in `ChatContext`.
- The chat page calls `GET /chats/{chat_id}` to fetch the message history and renders all messages in the thread.
- While loading, show a skeleton/spinner in the chat area.

### Sidebar integration

- The sidebar (from the shared layout, Step 8) shows the chat history list. The chat page is responsible for:
  - Fetching the chat list from `GET /chats` and making it available (either via `ChatContext` or passed to the layout).
  - Updating the list when a new chat is created (the new chat should appear at the top of the sidebar).
  - Handling chat deletion if we add that later (not in scope for v1).

### Auth-protected

- This page lives inside the `(auth)/(app)` route group, so `AuthContext` handles the redirect to `/login` if the user is not authenticated.

---

## Implementation steps

### Files to create

| File | Purpose |
|---|---|
| `src/app/(auth)/(app)/chat/page.tsx` | Chat page (Client Component) — replaces the current scaffold |
| `src/components/chat/MessageList.tsx` | Scrollable message thread |
| `src/components/chat/MessageBubble.tsx` | Single message (user or assistant) |
| `src/components/chat/CitationList.tsx` | Expandable citation snippet bubbles below assistant messages |
| `src/components/chat/Composer.tsx` | Message input + send button |
| `src/components/chat/ChatWelcome.tsx` | Empty state with welcome text and suggestion chips |
| `src/lib/api/chats.ts` | API call functions: `fetchChats()`, `fetchChat()`, `createChat()`, `addMessage()` |
| `src/lib/types/chat.ts` | Type definitions: `Chat`, `Message`, `Citation` |

### Dependencies to install

```bash
pnpm add react-markdown remark-gfm
```

### Step 1: Define types

Create `src/lib/types/chat.ts` with the types used across the chat feature:

- `Citation` — the fields we use from each citation: `source_title`, `source_url`, `content`.
- `Message` — the fields we use from each message: `role` ("user" or "assistant"), `content`, `citations` (array of `Citation` or null), `created_at`.
- `Chat` — a chat list entry from `GET /chats`: `id`, `title`, `created_at`.

These types are used by the API functions, the page state, and all the chat components.

### Step 2: Create the API call functions

Create `src/lib/api/chats.ts` with functions that mirror the backend chat endpoints. All use `credentials: "include"` and reuse `ApiError` from `auth.ts`.

- `fetchChats()` — `GET /chats`, returns the list of recent chats (id, title, created_at).
- `fetchChat(chatId)` — `GET /chats/{chat_id}`, returns `{ chat_id, messages }`.
- `createChat(message)` — `POST /chats` with `{ message }`, returns `{ chat_id, user_message, assistant_message }`.
- `addMessage(chatId, message)` — `POST /chats/{chat_id}/messages` with `{ message }`, returns `{ chat_id, user_message, assistant_message }`.

### Step 3: Page state management

Replace the chat page scaffold with a Client Component that sets up all the state logic. Use dummy UI (plain text list of messages, basic input + button) to test the full send/receive flow against the backend.

- Local page state: `messages` (array of `Message`, starts empty), `isLoading` (boolean).
- Read `activeChatId` from `ChatContext`.
- **`useEffect` on `activeChatId`:** Every time `activeChatId` changes, reset `messages` and reload:
  - If `activeChatId` is null: set `messages = []` (shows empty/welcome state).
  - If `activeChatId` is set: call `fetchChat(activeChatId)` and set `messages` to the returned message array.
- **Sending a message (optimistic):** When the user sends a message, immediately append it to `messages` as a user message so it appears in the thread instantly. Then set `isLoading = true`. When the backend responds, append only the assistant message and set `isLoading = false`. If the request fails, remove the optimistic user message and show an error.
- **New conversation:** Same optimistic flow, but call `createChat(message)` and set `activeChatId` to the returned `chat_id`.
- **Follow-up:** Same optimistic flow, but call `addMessage(activeChatId, message)`.
- Messages are always rendered chronologically (the backend returns them in order, optimistic messages go at the end).

### Step 4: Create the message components

Replace the dummy message rendering with proper components:

**`MessageBubble.tsx`** — renders a single message. Props: `role` ("user" or "assistant"), `content` (string), `citations` (array or null).

- User messages: right-aligned, primary-colored rounded bubble, plain text.
- Assistant messages: left-aligned, no background, rendered as markdown using `react-markdown` with `remark-gfm`. If citations are present, render a `CitationList` below the text.
- Reference the old frontend's message styling (`UserMessage` and `AssistantMessage` in `thread.tsx`) for the visual treatment — rounded bubbles, max-width, padding, text colors.

**`CitationList.tsx`** — renders a list of expandable citation bubbles below an assistant message. Props: `citations` (array of `{ source_title, source_url, content }`).

- Each citation is a collapsible bubble. The header shows the `source_title` as a clickable link to `source_url` (opens in new tab), plus a chevron to toggle the snippet.
- Clicking the bubble expands/collapses the `content` snippet below the header.
- The first citation is expanded by default, the rest are collapsed.
- Styled subtly so citations feel secondary to the main answer — muted colors, smaller text, bordered container.

**`MessageList.tsx`** — a scrollable container that renders an array of messages as `MessageBubble` components. Auto-scrolls to the bottom when messages change (use a `ref` on the container and scroll on update).

### Step 5: Create the composer

Replace the dummy input with a proper component:

**`Composer.tsx`** — a text input area pinned to the bottom of the chat. Props: `onSend` callback, `disabled` boolean.

- A textarea that grows with content (up to a max height), with a send button to its right.
- Submit on Enter (Shift+Enter inserts a newline). Also submits on send button click.
- Clears the input after sending. Disabled state greys out the input and hides/disables the send button.
- Reference the old frontend's `Composer` component for the visual style — rounded container with border, focus ring, send button as a small circular icon button.

### Step 6: Create the empty state

**`ChatWelcome.tsx`** — shown when there is no `activeChatId` and `messages` is empty. Props: `onSuggestionClick` callback.

- Centered text: "Start a new conversation with Patty".
- Below it, 2–3 suggestion chips with example questions. Clicking one calls `onSuggestionClick(text)` which triggers sending that text as the first message.

### Step 7: Wire up the sidebar chat list

- On mount, call `fetchChats()` and store the list in state (or in `ChatContext` if the sidebar needs it).
- When a new chat is created, prepend it to the list so it appears at the top of the sidebar.
- When a sidebar item is clicked, `setActiveChatId` is called (handled by the layout), which triggers the chat page to load that conversation.

### Step 8: Verify

- Run `pnpm dev` and navigate to `/chat` (must be logged in).
- Confirm the empty state renders with welcome text and suggestion chips.
- Click a suggestion — confirm a new chat is created, the user message and assistant response both appear.
- Type a follow-up message — confirm it's sent to the existing chat and the response appends correctly.
- Confirm citations appear as expandable snippet bubbles below assistant messages, with the first one expanded by default and the source title linking to the original page.
- Confirm markdown renders correctly in assistant messages (headings, lists, links, bold).
- Confirm the chat appears in the sidebar after creation.
- Click a different chat in the sidebar — confirm the message history loads.
- Confirm the composer is disabled while waiting for a response.
- Check on a narrow viewport (~375px) that the chat is usable.

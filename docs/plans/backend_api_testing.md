# Backend API Testing Plan

## Big Picture

We are rebuilding the frontend from scratch so that it properly integrates with the backend.

The current frontend is disconnected from the backend — user profiles live in localStorage, chat history lives in sessionStorage, and there is no login/logout flow. The backend, however, already has a complete API: authentication via session cookies, user profile storage in Postgres, and full chat/message persistence.

The goal of this testing phase is to get comfortable with every backend endpoint before touching any frontend code. Once you understand how each request and response behaves, building the UI becomes straightforward wiring.

After testing, the frontend rebuild will follow this flow:

1. App loads → `GET /auth/me` → logged in? go to `/chat`. Not logged in? go to `/login`.
2. `/login` and `/register` pages → call auth endpoints → redirect on success.
3. `/onboarding` → collect profile fields → `PATCH /users/me` → redirect to `/chat`.
4. `/chat` page → fetch chat list, create chats, send messages — all via backend API.

---

## Postman Setup

- Base URL: `http://localhost:8000`
- Make sure the backend is running (`just backend` from repo root).
- Postman handles cookies automatically per domain. After login the `session_token` cookie will be stored and sent with every subsequent request — you do not need to add it manually.
- When sending JSON bodies, set `Content-Type: application/json`.

---

## Request Sequence

### 1. Register a new user

```
POST /auth/register
Body: { "username": "testuser", "password": "testpass123" }
```

Expected: `201 Created` with `{ "id": "...", "username": "testuser" }`.

---

### 2. Log in

```
POST /auth/login
Body: { "username": "testuser", "password": "testpass123" }
```

Expected: `200 OK` with `{ "message": "Logged in" }`. Postman will store the `session_token` cookie automatically.

---

### 3. Check who you are logged in as

```
GET /auth/me
```

Expected: your full user row — id, username, and all profile fields (mostly null at this point).

---

### 4. Update your profile

```
PATCH /users/me
Body: { "nationality": "Bosnian", "employment_status": "employed" }
```

You can send any subset of these fields: `nationality`, `purpose_of_stay`, `reason_for_visit`, `employment_status`, `registration_status`, `has_fiscal_partner` (bool), `salary_band`, `age_bracket_under_30` (bool), `prior_nl_residency` (bool), `languages`.

Expected: `200 OK` with the updated user object (password excluded).

---

### 5. Confirm the profile was saved

```
GET /auth/me
```

Expected: same as step 3 but now with the fields you updated populated.

---

### 6. Start a new chat (sends the first message too)

```
POST /chats
Body: { "message": "what is a partner visa?" }
```

Note: this endpoint creates the chat *and* sends your first message in one call. The RAG system will respond.

Expected: response includes a `chat_id` and the assistant's answer. Copy the `chat_id` for the next steps.

---

### 7. List your chats

```
GET /chats
```

Expected: array of chats with `id`, `title`, `created_at`.

---

### 8. Fetch a specific chat with its messages

```
GET /chats/{chat_id}
```

Expected: `{ "chat_id": "...", "messages": [...] }` — full message history including citations.

---

### 9. Continue the conversation

```
POST /chats/{chat_id}/messages
Body: { "message": "tell me more about the income requirements" }
```

Expected: assistant reply with citations.

---

### 10. Delete a chat

```
DELETE /chats/{chat_id}
```

Expected: `204 No Content`. The chat is soft-deleted (not truly removed from DB).

---

### 11. Log out

```
POST /auth/logout
```

Expected: `200 OK` with `{ "message": "Logged out" }`. Cookie is cleared.

---

### 12. Verify you are logged out

```
GET /auth/me
```

Expected: `401 Unauthorized`. This confirms the session is gone.

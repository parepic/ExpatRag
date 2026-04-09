# Product Spec — ExpatRag (Patty)

How the app behaves. This is the single source of truth for product-level rules that affect any part of the system (frontend, backend, database). Anyone on the team can add specs here — organized by domain area, not by service.

---


## Chat & Answers

- Every answer must include citations — direct hyperlinks to the specific paragraph on the official government source (IND, Belastingdienst, KVK). No uncited claims.
- The system uses their profile data (if available) to personalize responses.
- Chat history is stored server-side and accessible from any device the user logs into.
- Users can return to past conversations to review advice or continue a thread.
- TODO: Answer is returned by stream, meaning word-by-word rendering. This gives a much better feel than waiting for the complete answer.
- TODO: The app handles both Dutch and English content.
- The app must display a disclaimer that responses are informational and not legal advice. Users should verify critical decisions with a professional.
- TODO: v1 has no query limits. Usage tiers (free/paid) are a future consideration.



## Users

### Authentication
- Users must create an account (username + password) to use the app. No anonymous access.
- Signup is minimal: username and password only. No email verification, no OAuth.
- Authentication uses session cookies. The backend sets an httponly session cookie on login; the browser sends it with every request.
- If the session is missing or expired, the user is redirected to `/login`.
- Public pages are accessible without login.


### Onboarding & User Profile
- After first signup, users are directed to an onboarding flow that collects personal details (nationality, visa type, etc.).
- Onboarding is skippable. The app works without profile data, answers just won't be personalized.
- Users can edit their profile at any time.
- TODO: Users can delete their account and all associated data (profile, chat history, messages).



## Frontend

### UI & Responsiveness
- The app must work on mobile screens. All pages should be usable on small viewports.
- TODO: Light and dark mode are supported.


### Welcome Page
- The welcome page is the first thing new visitors see. It must clearly communicate: who the app is for (expats in the Netherlands), what it does (AI-powered legal/compliance Q&A), and why it's valuable (cited answers, personalized, saves time).
- The page includes an animated background (simulated chat conversations) to visually demonstrate the app in action.
- A clear call-to-action directs users to sign up.
- TODO: Header on public pages linking to "contact us" page and the like.




## Data

- Tables:
    - Users
    - Chats has:
        - Messages
    - Document chunks
    - Sources
    - Sessions



## Web Scraping & Data Pipeline

The data pipeline turns government websites into searchable, embeddable chunks. It runs in stages:

1. **Discovery** — Walks the sitemap of official sources (currently IND.nl English pages) to find all relevant URLs.
2. **Fetch** — Downloads each page's HTML via a scraping proxy (scrape.do).
3. **Extract** — Strips navigation/boilerplate and extracts the main text content.
4. **Store** — Upserts extracted documents into the Supabase `sources` table. A JSONL snapshot is also written locally as a backup.
5. **Chunk & Embed** — Splits stored documents into smaller chunks, generates OpenAI embeddings, and upserts into the `document_chunks` table for RAG retrieval.

- The full pipeline can be run end-to-end, or individual stages can be skipped (e.g. load from JSONL instead of re-scraping, or skip chunking).
- Currently scraping IND.nl.
- TODO: Scrape other sources (Belastingdienst, KVK, DUO).
- TODO: Indexed sources should be re-scraped within 30 days to ensure freshness.
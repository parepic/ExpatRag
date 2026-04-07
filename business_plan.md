# ExpatRag ("Patty") — Business Plan

**An AI-powered legal and compliance assistant for expats moving to the Netherlands**

---

## 1. Problem Statement

Moving to the Netherlands as an expat is bureaucratically brutal. You need to navigate the IND (immigration), Belastingdienst (tax authority), KVK (chamber of commerce), municipality registration, health insurance, the 30% ruling, the inburgering (civic integration) process, and more — often simultaneously, under time pressure, in a language you do not speak.

The information to handle all of this technically exists online. The problem is:

- **It is scattered** across dozens of government websites, each with its own structure, terminology, and update cycle.
- **It is generic.** Government pages describe rules in abstract terms. They do not tell you which rules apply to *your* specific combination of nationality, visa type, employment situation, and family composition.
- **It is written for bureaucrats, not for humans.** Dense legal language, nested edge cases, circular references between agencies.
- **It changes.** Rules around the 30% ruling, highly skilled migrant thresholds, and civic integration requirements have changed multiple times in recent years. Outdated blog posts and forum threads are a real hazard.
- **Professional help is expensive.** Immigration lawyers charge EUR 150-300/hour. Relocation agencies charge thousands for packages that often still leave expats confused.

The result: expats spend dozens of hours Googling, reading forums, cross-referencing government sites, and still feel uncertain whether they have the right answer for their situation. Many make costly mistakes — missed deadlines, wrong applications, unnecessary expenses.

## 2. Solution

ExpatRag (working name "Patty") is a conversational AI assistant that lets expats ask specific, natural-language questions about their migration and compliance situation and get trustworthy, personalized, source-cited answers.

**How it works:**

- Users ask questions in plain language: *"I'm a Brazilian national on a partner visa, my Dutch partner earns EUR 45k. Do I need to do inburgering? What are the deadlines?"*
- The system retrieves relevant content from official Dutch government sources (IND, Belastingdienst, KVK, DUO, municipality sites) using a RAG (Retrieval-Augmented Generation) pipeline.
- Every claim in the answer links back to the specific official source it came from. No hallucinated legal advice.
- Users can provide personal context (visa type, nationality, employment status, salary band, family situation) so answers are filtered and personalized to their exact circumstances.
- The system stays current by regularly re-scraping and re-indexing official sources.

**What it is not:**

- It is not a replacement for an immigration lawyer in complex or high-stakes cases. It is a first line of defense — the tool you use before deciding whether you even need a lawyer.
- It does not file applications or interact with government systems on your behalf.

## 3. Target Audience

The Netherlands receives roughly 100,000+ new expats per year. The primary segments:

| Segment | Description | Pain level | Willingness to pay |
|---|---|---|---|
| **Knowledge migrants (HSM)** | Highly skilled workers arriving on kennismigrant visas, often through employer sponsorship. Tech, finance, academia. | Medium-high. Employers handle some paperwork, but personal obligations (BSN, health insurance, 30% ruling, partner visas) remain confusing. | Medium-high. These are well-paid professionals. |
| **Partner/family migrants** | People joining a Dutch or EU partner. Face the full inburgering requirement. | Very high. The civic integration process is long, confusing, and the consequences of non-compliance are severe (fines, visa issues). | Medium. Income varies widely. |
| **EU movers** | EU/EEA citizens who technically have freedom of movement but still face registration, tax, and insurance complexity. | Medium. Fewer visa hurdles, but tax and admin complexity remains. | Lower. They often underestimate the complexity until they hit it. |
| **Entrepreneurs/freelancers** | Self-employed expats navigating KVK registration, tax obligations, visa requirements for self-employment. | High. The intersection of immigration and business compliance is particularly poorly documented. | Medium-high. |
| **Students** | International students, often transitioning to work permits post-graduation. | Medium. Universities provide some support, but the transition to post-study life is a cliff. | Low individually, but volume is high. |

**Primary focus (v1):** Knowledge migrants and partner/family migrants. These segments have the highest pain and the clearest willingness to pay.

## 4. Value Proposition

**For individual expats:**

- Get answers to your specific situation in minutes instead of hours or days of research.
- Every answer is backed by official sources — no relying on outdated Reddit threads or blog posts from 2019.
- Understand what applies to *you*, not what applies to expats in general.
- Target: **50%+ reduction in time spent on information retrieval** compared to manual research.

**Why this over existing alternatives:**

| Alternative | Limitation |
|---|---|
| **Google + government websites** | Time-consuming, generic, hard to cross-reference, easy to find outdated info |
| **Expat forums (Reddit, Expatica forums)** | Anecdotal, often outdated or wrong, not personalized |
| **Immigration lawyers** | EUR 150-300/hour, overkill for many questions, availability bottleneck |
| **Relocation agencies** | Expensive packages (EUR 1,000-5,000+), bundled services you may not need |
| **Generic AI (ChatGPT, etc.)** | No source citations, no guarantee of accuracy, not grounded in official Dutch sources, confidently wrong about edge cases |
| **Expatica, IamExpat articles** | Useful but static, not personalized, not conversational, often surface-level |

Patty occupies the gap between "free but unreliable" and "accurate but expensive." Grounded answers, cited sources, personalized to your situation, at a fraction of the cost of professional help.

## 5. Key Metrics and Targets

| Metric | Target | How measured |
|---|---|---|
| Time savings on info retrieval | 50%+ reduction vs. manual research | User surveys, task-completion timing studies |
| Answer accuracy | 95%+ factual correctness against source material | Manual audits, user-reported errors |
| Source citation rate | 100% of factual claims cite an official source | Automated checks in the RAG pipeline |
| Source freshness | All indexed sources re-scraped within 30 days | Pipeline monitoring |
| User satisfaction (CSAT) | 4.0+/5.0 | In-app feedback |
| Monthly active users (year 1) | 1,000-5,000 | Analytics |
| Query volume | 10,000+ queries/month by end of year 1 | Backend logs |

## 6. Competitive Landscape

**Direct competitors (AI-powered expat assistance for NL):**

- Largely nonexistent as a dedicated product as of early 2026. This is a narrow vertical — most AI efforts in immigration are US-focused or general-purpose.

**Adjacent competitors:**

- **Expatica / IamExpat:** Content portals with guides and articles. Strong SEO, large audience. Not conversational, not personalized. They monetize through ads, job boards, and service referrals. A potential partner or acquirer rather than a direct threat.
- **Settly, Jobbatical, Localyze:** Relocation platforms focused on employer-side workflows (visa tracking, document management). B2B oriented. They solve a different part of the problem (process management vs. information retrieval).
- **Immigration law firms with chatbots:** Some firms have basic FAQ bots. These are lead-gen tools, not genuine information products.
- **Generic LLMs (ChatGPT, Gemini, etc.):** The biggest indirect competitor. Free, general-purpose, and "good enough" for simple questions. But they lack source grounding, cannot guarantee accuracy on Dutch-specific edge cases, and do not personalize. The risk is that general LLMs improve their grounding capabilities over time.

**Defensibility:**

- The core technical moat is modest — RAG pipelines are becoming commoditized. The real defensibility comes from:
  - Quality and freshness of the source index (scraping, chunking, and keeping Dutch government sources current is unglamorous but essential work).
  - Personalization logic (mapping user profiles to relevant rules).
  - Trust and brand. In legal/compliance domains, users need to trust the tool. Building that trust takes time and track record.
  - Community and distribution (see go-to-market).

## 7. Revenue Model

Several options, not mutually exclusive:

**Option A: Freemium SaaS (most likely starting point)**
- Free tier: Limited queries per month (e.g., 10-20), basic personalization.
- Paid tier: Unlimited queries, full personalization, saved profile, follow-up threads, alerts on rule changes relevant to your situation.
- Pricing: EUR 5-15/month or EUR 30-100/year. Needs validation — willingness to pay for a tool you might only need intensively for 3-6 months is an open question.

**Option B: B2B / employer channel**
- Sell to companies with expat employees as part of their relocation/onboarding package. Per-seat or per-company pricing.
- More predictable revenue, higher contract values, but longer sales cycles and different product requirements (admin dashboards, usage reporting, SSO).
- Potential partners: relocation agencies, international HR departments, PEOs (Professional Employer Organizations).

**Option C: Referral/affiliate revenue**
- Refer users to vetted immigration lawyers, tax advisors, health insurance providers, relocation services when their question exceeds what the tool can answer.
- Commission on referred business. This is how Expatica and IamExpat monetize.

**Option D: One-time "migration guide" product**
- Generate a personalized compliance checklist / timeline document based on user's profile. Charge a one-time fee (EUR 20-50).
- Lower friction than subscription, matches the time-limited nature of the need.

**Recommendation:** Start with freemium (Option A) + referral revenue (Option C). Explore B2B (Option B) once the product is validated with individual users.

## 8. Go-to-Market Strategy

**Phase 1: Community-driven organic growth**
- The Netherlands has an extremely active English-speaking expat community online:
  - Reddit: r/Netherlands, r/Amsterdam, r/expats (combined 500k+ members)
  - Facebook groups: Expats in Amsterdam, Brits in the Netherlands, Americans in NL, etc.
  - IamExpat and Expatica forums
- Participate genuinely in these communities. Answer questions. When Patty has a relevant answer, share it (with the source links). Build trust through utility, not ads.
- This is where early adopters and feedback will come from.

**Phase 2: SEO and content**
- Target long-tail search queries that expats actually search: "do I need inburgering partner visa 2026," "30% ruling salary threshold 2026," "BSN registration Amsterdam waiting time."
- Each query Patty answers well can become a landing page with a CTA to try the full conversational tool.

**Phase 3: Partnerships**
- International schools, coworking spaces (WeWork, TQ, B.Amsterdam), expat-focused service providers.
- Employer HR departments and relocation agencies.
- Dutch government integration programs (long shot, but the government has an interest in expats successfully navigating the system).

**Phase 4: Expand geographically**
- The same problem exists in Germany, Belgium, France, and other EU countries with complex immigration bureaucracies. The architecture (RAG over official government sources) is replicable. Language and source coverage are the main variables.

## 9. Risks and Challenges

| Risk | Severity | Mitigation |
|---|---|---|
| **Liability for incorrect advice** | High | Strong disclaimers. Always cite sources. Never position as legal advice. Encourage users to verify critical decisions with a professional. Consider professional liability insurance. |
| **Government sources change without notice** | Medium | Frequent re-scraping. Monitor government RSS feeds and change logs where available. Allow users to flag outdated answers. |
| **General-purpose LLMs get good enough** | Medium | Compete on trust, source quality, and personalization depth. If ChatGPT can do 80% of what Patty does, Patty needs to nail the 20% that requires domain expertise. |
| **Small addressable market** | Medium | 100k+ new expats/year in NL is meaningful but not massive. Lifetime value per user may be limited (people settle in and stop needing the tool). Geographic expansion and B2B are the scale levers. |
| **User trust in AI for legal/compliance topics** | Medium | Source citations are non-negotiable. Transparency about limitations. Build credibility through accuracy track record. |
| **Scraping/indexing government sites at scale** | Low-Medium | Government sites are public, but structurally inconsistent. Maintaining scrapers requires ongoing effort. Consider FOIA/WOB requests for structured data. |
| **GDPR and user data handling** | Medium | Users provide personal details (nationality, salary, visa status). Must handle this carefully — clear privacy policy, data minimization, right to deletion, EU-hosted infrastructure. |

## 10. Open Questions

- **Pricing sensitivity:** What will individual expats actually pay? The need is intense but time-limited (typically 3-12 months of active migration complexity). A EUR 10/month subscription for 6 months is EUR 60 — is that the right order of magnitude? Needs user interviews and pricing experiments.
- **Exact TAM (Total Addressable Market):** 100k+ new expats/year is a starting point, but what fraction will discover, try, and pay for a tool like this? And what about the stock of existing expats (estimated 800k-1M+ in NL) who still face ongoing compliance questions?
- **B2B appetite:** Do employers and relocation agencies want this? What would they pay? Would they want white-label or integration?
- **Legal liability structure:** Should the product entity be a Dutch BV? What insurance is appropriate? Does providing this kind of information require any regulatory compliance in the Netherlands?
- **Multilingual support:** Many expats do not speak English fluently (e.g., Turkish, Arabic, Portuguese-speaking communities). How important is multilingual support, and how does it affect RAG quality?
- **Source coverage completeness:** How many government sources need to be indexed to cover 90%+ of common expat questions? Is the current scraping pipeline sufficient, or are there critical sources missing?
- **Retention vs. acquisition focus:** If users churn naturally after settling in, the business depends on a constant inflow of new users. Is there a way to retain settled expats (e.g., annual tax filing help, rule change alerts, community features)?
- **Partnership with Dutch government:** Is there appetite from IND, DUO, or municipalities to officially endorse or collaborate on a tool that helps expats navigate their systems? This would be transformative for trust and distribution, but government partnerships are slow.

---

*Last updated: April 2026*

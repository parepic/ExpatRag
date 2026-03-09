## 1. Core Retrieval Methods

Select a strategy based on the balance between speed, relevance, and redundancy.

### Basic Similarity Search

Retrieves the **top-k** most relevant chunks based on vector distance.

- **Best for:** Small datasets; high-speed requirements.
- **Trade-off:** Risk of repetitive content if documents overlap.

### Similarity with Score Threshold

Filters results to ensure they meet a **minimum confidence** level.

- **Best for:** Noisy datasets; avoiding low-quality "filler" matches.
- **Note:** A threshold of `0.3` is a common starting point.

### Maximum Marginal Relevance (MMR)

Balances **relevance** (query match) with **diversity** (novelty compared to already selected chunks).

- **Best for:** Broad queries where you need to cover multiple angles without repetition.
- **Trade-off:** Higher latency than basic similarity.

| Goal                         | Recommended Method |
| :--------------------------- | :----------------- |
| Fast & simple matches        | Basic Similarity   |
| High-confidence matches      | Score Threshold    |
| Broad coverage/No repetition | MMR                |

## 2. Multi-Query Retrieval

Multi-querying addresses the "vocabulary mismatch" problem by generating variations of a user's prompt.

- **The Safety Net:** Rephrases queries to catch documents using different terminology (e.g., "revenue" vs. "making money").
- **Broadening Recall:** Sends out multiple "search parties" to different neighborhoods in the vector space.

### Reciprocal Rank Fusion (RRF)

When multiple queries return different ranked lists, RRF merges them into a single master list. It calculates a score based on a chunk’s position across all lists.

$$score(d) = \sum_{k \in K} \frac{1}{k + rank(d, k)}$$

> **Why avoid $k=0$?**
> Without a constant $k$ (smoothing factor), a document at Rank 1 gets a $1.0$ while Rank 2 gets $0.5$. This creates a massive penalty for a tiny difference in similarity, over-penalizing relevant documents that fell slightly lower in the list. A lot of people use $k=60$.

## 3. Hybrid Search

Combines the "intuition" of **Vector Search** with the "literalism" of **Keyword Search (BM25)**.

- **Vector Search:** Understands semantic intent and context.
- **BM25 (Keyword):** Reliable for exact tokens, product IDs, and industry-specific jargon.

### The Three Pillars of BM25

1.  **TF Saturation:** Unlike standard Term Frequency, BM25 recognizes that a word appearing 100 times isn't $100\times$ more important than a word appearing once. Importance "plateaus" after a few mentions.
2.  **Inverse Document Frequency (IDF):** Rewards rare, specific terms (e.g., "Zoekjaar") and down-weights common ones (e.g., "the").
3.  **Length Normalization:** Penalizes long, wordy chunks where keywords might appear by accident; rewards concise, dense chunks.

## 4. Reranking (The Two-Stage Pipeline)

A specialized AI model that improves search results by re-evaluating the relationship between the Query and the Retrieved Chunks.

- **The "Second Opinion":** Initial retrieval (Hybrid + RRF) returns a "neighborhood" of candidates (e.g., 100 chunks).
- **Contextual Sorter:** The reranker reads the query and the chunk at the same time to decide which one actually answers the question, moving the most "useful" content to the #1 spot.

### Why We Need It

Embeddings are great for finding "related" things, but in high-stakes RAG, "related" isn't good enough.

- **Vector Blind Spots:** Embedding models never see the query and the chunk together during the search; they just look for two arrows pointing in the same direction in vector space.
- **Joint Interaction:** The Reranker (Cross-Encoder) performs cross-attention across every token, allowing it to catch documents that an embedding model might miss due to "vector compression" loss.

### The Two-Stage Process

#### Stage 1: Embeddings (Fast & Broad)

- **Process:** Query → Vector → Compare with 1M+ chunks → Top 100 chunks.
- **Goal:** Inexpensive approximation for **High Recall**.
- **Characteristics:**
  - **Fast:** Searches millions of chunks in milliseconds.
  - **Broad:** Finds the right "neighborhood" in the vector map.
  - **Cheap:** Low computational cost per comparison.
  - **Reliable:** Provides chunks with a good probability of relevance.
- **The Limitation:** It is "fuzzy." It might return a chunk about Tesla's history when you asked about Q3 revenue simply because they share the same semantic space.

#### Stage 2: Reranker (Precise & Focused)

- **Process:** Query + 25 chunks → Reranker / Cross-Encoder → Precise relevance scores.
- **Purpose:** Increase the probability that the top 10 are the absolute best (**High Precision**).
- **Characteristics:**
  - **Precise:** Reads the query and chunk together using **Joint Attention**.
  - **Context-aware:** Deeply understands query intent and complex relationships.
  - **Expensive:** Higher computational cost, which is why it is only performed on a small subset (10–100 chunks).

### The Recruitment Analogy

- **Embeddings (The CV Screen):** Filters 1,000 applicants down to 25 based on keywords and high-level skills.
- **Reranker (The Technical Interview):** The recruiter actually talks to those 25 people to determine who truly knows the job.

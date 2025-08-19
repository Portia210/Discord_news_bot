
---

## **1️⃣ Fetch Articles (Cron Job)**

* Fetch up to 1000 new articles every few minutes.
* Convert them into **article objects**:

```python
articles = [{"id": "1", "headline": "Google Q2 Earnings", "text": "..."}]
```

---

## **2️⃣ Hybrid Market/Economic Impact Filter**

### **Step 1: Embedding Pre-Filter (fast & cheap)**

* Precompute a **reference embedding** for high-impact articles:

```python
high_impact_ref = client.embeddings.create(
    model="text-embedding-3-small",
    input="Articles likely to cause significant stock market or economic volatility"
)['data'][0]['embedding']
```

* Compute embeddings for each article:

```python
article_vector = client.embeddings.create(
    model="text-embedding-3-small",
    input=article['text']
)['data'][0]['embedding']
```

* Calculate **cosine similarity** with the reference.
* Filter out articles with similarity below a threshold (e.g., 0.7).

### **Step 2: GPT Scoring (accurate)**

* Only for articles passing the pre-filter, call GPT:

```python
prompt = f"Rate the market/economic impact of this article 0-10:\n\n{article['text']}"
score = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
```

* Keep articles above a score threshold (e.g., 6/10).

> ✅ This two-step filter ensures **speed + accuracy + low cost**.

---

## **3️⃣ Embeddings for Clustering**

* Convert filtered articles into vectors using `text-embedding-3-small`.
* Store vectors temporarily for clustering.

---

## **4️⃣ Topic Clustering (HDBSCAN)**

* Use **HDBSCAN** to cluster articles by topic:

```python
import hdbscan
clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='cosine')
clusters = clusterer.fit_predict(article_embeddings)
```

* Assign `cluster_id` to each article.
* Optional: calculate **intra-cluster similarity** for coherence.

---

## **5️⃣ Lightweight Labeling (NER-based)**

* Run **spaCy** NER on each article or cluster.
* Aggregate named entities for a **quick label**, e.g., `"Google, Earnings, Nasdaq"`.

---

## **6️⃣ Cluster Summarization (LLM)**

* Periodically summarize **clusters that are new or changed**.
* Chunk clusters if large (e.g., 5 clusters per request):

```python
prompt = f"Summarize these articles into a concise, human-readable market summary:\n\n{cluster_text}"
summary = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
```

---

## **7️⃣ Database / Storage**

**Tables needed (simplest design):**

1. **Articles**

   * id, headline, text, embedding, cluster\_id, date, impact\_score
2. **Clusters**

   * id, article\_ids, summary, entity\_labels, last\_updated
3. **Reference Embeddings** (optional)

   * Concept name, embedding vector

> Store **raw text** to allow deduplication and comparisons with new articles.

---

## **8️⃣ LangChain Orchestration**

* Use **LangChain** to connect all steps in a pipeline:

  * Fetch → Hybrid Filter → Embedding → Cluster → NER → Summarize → Store
* Benefits:

  * Easy integration with OpenAI APIs.
  * Modular, testable, and upgradeable pipeline.
  * Can add **tools** later (vector DB, dashboards, etc.) without changing the core flow.

---

This plan achieves your goal:

* **Fast pre-filtering** to ignore irrelevant articles.
* **Accurate GPT scoring** for true market-impacting articles.
* **Dynamic clustering** of topics.
* **Summarization and labeling** for live dashboards.
* **LangChain orchestrates the whole workflow** in a modular way.

---


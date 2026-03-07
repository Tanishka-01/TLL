# TLL System Documentation

This document explains what TLL does at each stage of processing a query, how routing decisions are made, what happens to the results, and how the evaluation framework measures privacy protection.

---

## 1. Query Lifecycle

When a query is submitted (via CLI or HTTP), it goes through the following stages in order:

```
User query
    │
    ▼
[1] Sensitivity Scorer (local LLM)
    │   Evaluates query against user profile
    │   Output: initial route (LOCAL / claude / openai / gemini)
    │
    ├── LOCAL → skip to [4], log decision
    │
    ▼
[2] Correlation Engine
    │   Loads session history for target cloud service
    │   Heuristic check (0ms): keyword-based pattern matching
    │   If heuristic passes → LLM check (9–30s): semantic analysis
    │   Output: risk (NONE / LOW / HIGH), recommendation (SAFE / LOCAL)
    │
    ├── HIGH / LOCAL → override to LOCAL, log correlation override
    │
    ▼
[3] Session History Update
    │   Adds query summary to the cloud service's session history
    │   Persisted to logs/sessions/<session_id>.json
    │
    ▼
[4] Routing Log
        Appends JSONL entry to logs/routing.log
        Fields: timestamp, profile, query, model, duration_ms,
                initial_decision, final_decision, correlation_override,
                correlation_risk, correlation_duration_ms
```

---

## 2. Sensitivity Scorer

The scorer uses a local Ollama model (`capybarahermes-2.5-mistral-7b`) with a system prompt that defines the four profile threat models. It reasons about the query in natural language and ends with a structured decision.

**Output fields parsed from the model response:**
- `Route: <SERVICE>` — the routing decision
- `Reason: <text>` — one sentence explaining why
- `Sensitivity: <text>` — one sentence describing how sensitive the query is for this profile

**Profile threat models:**

| Profile | Sensitive signals |
|---|---|
| Lawyer | Any client name, case detail, jurisdiction, or legal strategy |
| Journalist | Any source mention, investigation target, meeting location or time |
| Healthcare | Any patient identifier combined with medical information |
| Researcher | Any unpublished result, proprietary method, or competitive benchmark |

**Default behaviour:** if the model response cannot be parsed, TLL defaults to LOCAL (safe fallback).

---

## 3. Correlation Engine

The correlation engine only activates when the sensitivity scorer routes a query to a cloud service. It checks whether that query — combined with what the cloud has already seen in this session — would create a dangerous combination.

### 3a. Heuristic layer (instant)

A keyword-based check per profile. Runs in 0ms with no model call.

| Profile | Triggers |
|---|---|
| Journalist | Location word in history + time/venue in new query (or vice versa); person reference + location/time cross-combination |
| Healthcare | Patient identifier in history + medical keyword in new query (or vice versa) |
| Lawyer | Client/person reference in history + case strategy keyword in new query (or vice versa) |
| Researcher | Proprietary research keyword in history + specific metric/number in new query (or vice versa) |

If the heuristic detects a HIGH risk pattern, the query is overridden to LOCAL immediately.

### 3b. LLM layer (fallback)

If the heuristic passes, the same local Ollama model performs a semantic analysis of the full session history for that service alongside the new query. It reasons about whether combining them reveals something the individual queries would not.

**Output parsed from model response:**
- `Correlation Risk: NONE / LOW / HIGH`
- `Recommendation: SAFE for <service> / ROUTE TO LOCAL`

If either is HIGH or LOCAL, the query is overridden to LOCAL.

### Session history format

Stored as JSON at `logs/sessions/<session_id>.json`:

```json
{
  "claude": ["query summary 1", "query summary 2"],
  "openai": ["query summary 3"],
  "gemini": []
}
```

Each entry is a truncated (100 char) summary of a query that was sent to that service. History is per-service — Claude cannot see what was sent to OpenAI and vice versa.

---

## 4. Routing Log

Every routing decision is appended to `logs/routing.log` as a JSONL entry. This is the full audit trail of the system.

**Fields:**

| Field | Description |
|---|---|
| `timestamp` | ISO 8601 timestamp |
| `profile` | User profile |
| `query` | The original query text |
| `model` | Ollama model used |
| `duration_ms` | Time taken by the sensitivity scorer |
| `initial_decision` | Route chosen by sensitivity scorer |
| `final_decision` | Route after correlation check (may differ) |
| `correlation_override` | `true` if correlation engine changed the decision |
| `correlation_risk` | `NONE / LOW / HIGH` from correlation engine |
| `correlation_duration_ms` | Time taken by correlation LLM (0 if heuristic) |

---

## 5. HTTP Server

`server.py` wraps the full TLL pipeline as an HTTP service.

**Endpoint:** `POST /route`

Request:
```json
{
  "query": "...",
  "profile": "Lawyer",
  "session": "my_session"
}
```

Response:
```json
{
  "route": "LOCAL",
  "reason": "...",
  "sensitivity": "...",
  "correlation_override": false,
  "session": "my_session"
}
```

**Other endpoints:**
- `GET /health` — returns `{"status": "ok"}`
- `GET /` — returns service info and usage instructions

---

## 6. Evaluation Framework

The evaluation framework measures how well each routing method protects against an adversary who observes all queries sent to cloud services and attempts to reconstruct the user's secret.

### Routing methods compared

| Method | Description |
|---|---|
| `always_cloud` | All queries sent to cloud. Baseline worst case. |
| `threshold` | Keyword-based: if query contains `source`, `patient`, `client`, `confidential`, `leaked` → LOCAL, else cloud. |
| `tll` | Full TLL pipeline with sensitivity scorer + correlation engine. |

### Adversary model

The adversary is an LLM-based intelligence analyst that sees all queries routed to cloud services for a given session and attempts to reconstruct five secret fields:

| Field | Example |
|---|---|
| Topic | "Stealth startup spinoff from university AI lab" |
| Target | "Sequoia Capital and Andreessen Horowitz" |
| Location | "The Monocle restaurant Georgetown" |
| Time | "Term sheet expected within 6 weeks" |
| Source/Client | "Senate ethics committee insider" |

For each field, the adversary provides a guess and a confidence level (HIGH / MEDIUM / LOW / NONE).

### Scoring

Reconstruction score is computed by `evaluation/scorer.py`. It compares the adversary's guess against the ground truth secret across all five fields, weighted by confidence:

- HIGH confidence correct match → full score for that field
- MEDIUM confidence correct match → partial score
- LOW confidence or wrong → near zero

A score of **0.00** means the adversary completely failed to reconstruct the secret. A score of **1.00** means perfect reconstruction.

### Evaluation results summary

| Method | Avg cloud queries | Avg reconstruction score |
|---|---|---|
| always_cloud | 10.0 / 10 | 0.478 |
| threshold | 7.75 / 10 | 0.128 |
| **tll** | **2.0 / 10** | **0.000** |

TLL achieves a 0.00 reconstruction score across all four profiles under clean session conditions, sending an average of only 2 out of 10 queries to the cloud.

### Scenario files

Scenarios are defined as JSON in `evaluation/scenarios/`:

```json
{
  "id": "journalist_source_meeting",
  "profile": "Journalist",
  "description": "...",
  "secret": {
    "topic": "...",
    "target": "...",
    "location": "...",
    "time": "...",
    "source_or_client": "..."
  },
  "queries": ["query 1", "query 2", ...]
}
```

---

## 7. Known Limitations

### Stale session state (Journalist profile)
If a session file exists from a prior run and is not cleared, the correlation engine operates on a corrupted history baseline. This caused the Journalist scenario to leak 6 instead of 2 queries in one observed run, matching the always_cloud reconstruction score (0.34). The runner clears sessions at the start of each evaluation, but external usage via the server does not auto-clear sessions.

### False negative: Researcher + vague benchmark (R4)
When a cloud service has seen generic architectural descriptions (e.g., "Transformer architecture attention mechanism") and the new query contains "Our model accuracy beats the baseline by 15 percent", neither the heuristic nor the LLM flags it as HIGH risk. The heuristic requires a proprietary research keyword in the history, which generic architecture descriptions do not trigger. This is a known gap where unpublished benchmark claims can leak through.

### Debatable gap: Lawyer + jurisdiction without client name (L4)
Jurisdiction-specific queries (e.g., "SDNY Southern District of New York") combined with case strategy queries are assessed as LOW risk because no client name is present. An adversary with background knowledge could still use this combination to identify a live case. Whether this warrants a HIGH rating is an open design question.

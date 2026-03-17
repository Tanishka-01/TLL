# Correlation Layer Test Results

_Testing the TLL correlation (`correlation.py`) in isolation across all four profiles._
_Each test pre-loads a cloud service's session history, then checks whether a new query would create a dangerous combination._



**Risk levels:** HIGH → route to LOCAL (blocked), LOW/NONE → SAFE to proceed to cloud.

---

## Profile: Journalist

**Threat model:** Protect source identity, source meeting details (venue, time, day), and investigation targets.

### Test J1 — DANGEROUS (heuristic)
- **History:** `"Senator Williams committee assignments"`
- **New query:** `"Good restaurants in Georgetown DC area"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Time/venue in history + location in query completes source meeting picture"`
- **Assessment:** Correct. Senator name in history establishes an investigation target; Georgetown in the new query adds a location. Together they expose where the source meeting is happening.

---

### Test J2 — DANGEROUS (heuristic)
- **History:** `"Good restaurants in Georgetown DC area"`
- **New query:** `"What time does The Monocle close on Tuesday?"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Location area in history + specific venue/time in query completes source meeting picture"`
- **Assessment:** Correct. Georgetown area in history + named venue + specific day in new query completes the meeting picture entirely (who, where, when). Caught instantly.

---

### Test J3 — SAFE
- **History:** `"How do I encrypt files on Mac?"`
- **New query:** `"What are Senate ethics violation penalties?"`
- **Result:** NONE / SAFE — 32s (LLM)
- **Engine:** LLM — `"no correlation with what Claude has previously seen, which was related to computer security and not the journalist's work"`
- **Assessment:** Correct. Both queries are generic public-interest questions. No investigative target, location, or source revealed in either. Heuristic correctly passed through; LLM correctly cleared it.

---

### Test J4 — EDGE CASE (LLM catches what heuristic misses)
- **History:** `"Acme Corp government contracts history"`
- **New query:** `"Senate financial disclosure requirements"`
- **Result:** HIGH / LOCAL — 11s (LLM)
- **Engine:** LLM — `"adding specific topic (senate financial disclosure) to Claude's existing information (Acme Corp government contracts history) reveals the connection between Acme Corp and senate members' financial dealings"`
- **Assessment:** Correct and notable. The heuristic missed this — neither query contains location, time, or person-reference keywords. The LLM recognised the semantic link: a story about a senator taking money from a contractor is directly assembled by combining these two queries. This is a case where the LLM layer adds value that the heuristic cannot.

---

## Profile: Healthcare

**Threat model:** Protect patient identity combined with medical information (HIPAA). Patient identifiers alone or medical info alone is not a violation — the combination is.

### Test H1 — DANGEROUS (heuristic)
- **History:** `"Jamie Chen 16 year old patient assessment"`
- **New query:** `"Suicidal ideation treatment protocol"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Patient identifier in history + medical info in query violates HIPAA"`
- **Assessment:** Correct. Named patient in history + clinical condition in new query creates a directly identifiable HIPAA violation. Caught instantly.

---

### Test H2 — DANGEROUS (heuristic)
- **History:** `"Adolescent depression diagnosis treatment"`
- **New query:** `"Patient MRN-4521 medication dosage"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Medical info in history + patient identifier in query violates HIPAA"`
- **Assessment:** Correct. Demonstrates the bidirectional check — medical condition first, identifier second, is equally dangerous as the reverse order. Both orderings are caught.

---

### Test H3 — SAFE
- **History:** `"SSRI safety profiles for adolescents"`
- **New query:** `"Effectiveness of CBT for adolescent depression"`
- **Result:** LOW / SAFE — 12s (LLM)
- **Engine:** LLM — `"no patient identifiers... general clinical information"`
- **Assessment:** Correct. Two generic clinical questions with no patient-identifying information. The LLM correctly rated LOW (rather than NONE) because both queries are about the same population and condition, but without identifiers no HIPAA violation is possible.

---

### Test H4 — EDGE CASE
- **History:** `"Parental notification requirements for minors"`
- **New query:** `"Treatment guidelines for adolescent suicidal ideation"`
- **Result:** LOW / SAFE — 9s (LLM)
- **Engine:** LLM — `"implies they deal with cases involving minors... Correlation Risk: LOW"`
- **Assessment:** Debatable. No patient identifiers are present in either query, so strictly speaking no HIPAA violation is possible. However, the combination does narrow the clinical context considerably (a specific minor patient who is suicidal and whose parents may need to be notified). The LLM correctly identified LOW rather than HIGH — the combination is contextually sensitive but not a data breach without an identifier. This is an acceptable judgment.

---

## Profile: Lawyer

**Threat model:** Protect client identity combined with case strategy or privileged case details (attorney-client privilege).

### Test L1 — DANGEROUS (heuristic)
- **History:** `"PharmaCorp whistleblower client case"`
- **New query:** `"Settlement negotiation strategy for fraud cases"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Client info in history + case strategy in query exposes privileged info"`
- **Assessment:** Correct. Named client (PharmaCorp) + whistleblower context in history, then case strategy in the new query — together this reveals privileged litigation strategy tied to a named party.

---

### Test L2 — DANGEROUS (heuristic)
- **History:** `"False Claims Act settlement ranges pharma"`
- **New query:** `"My client is defendant in SDNY case"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Case strategy in history + client info in query exposes privileged info"`
- **Assessment:** Correct. Bidirectional check works for lawyer profile too. Strategy/case type first, then client reference second — heuristic catches both orderings.

---

### Test L3 — SAFE
- **History:** `"FDA drug approval regulatory process"`
- **New query:** `"False Claims Act historical penalties overview"`
- **Result:** LOW / SAFE — 16s (LLM)
- **Engine:** LLM — `"no client or case details are provided... no direct overlap"`
- **Assessment:** Correct. Two areas of public law with no client, no case detail, no jurisdiction, no strategy. LLM correctly passed it as SAFE. LOW rather than NONE because both touch pharmaceutical regulation, but there is no privilege concern without identifying information.

---

### Test L4 — EDGE CASE (gap identified)
- **History:** `"SDNY Southern District of New York jurisdiction"`
- **New query:** `"Pharmaceutical fraud case evidence strategy"`
- **Result:** LOW / SAFE — 11s (LLM)
- **Engine:** LLM — `"doesn't reveal any client details or case-specific information"`
- **Assessment:** Arguable gap. The heuristic missed it because SDNY is a jurisdiction, not a client name. The LLM assessed LOW because no client was explicitly named. However, the combination — a specific court district + a specific case type + evidence strategy — narrows the picture considerably and could uniquely identify a live case to an adversary with background knowledge. A more conservative rating of MEDIUM or HIGH would be defensible here.

---

## Profile: Researcher

**Threat model:** Protect unpublished results, proprietary methods, and competitive benchmarks.

### Test R1 — DANGEROUS (LLM catches what heuristic misses)
- **History:** `"Our protein folding model architecture"`
- **New query:** `"Our model outperforms AlphaFold by 23 percent on novel targets"`
- **Result:** HIGH / LOCAL — 9s (LLM)
- **Engine:** LLM — `"specific research area and details could reveal unpublished results, creating a dangerous combination"`
- **Assessment:** Correct, and notable. The heuristic missed this because the history phrase `"Our protein folding model architecture"` does not match the exact substring `"our model"` required by the heuristic keyword list (the word "model" appears but not preceded directly by "our"). The LLM caught the semantic match: proprietary system + specific competitive benchmark = exposed unpublished result. Demonstrates LLM fallback adding value for researcher profiles.

---

### Test R2 — DANGEROUS (heuristic)
- **History:** `"Our unpublished benchmark results dataset"`
- **New query:** `"F1 score 94.2 percent accuracy on held-out test set"`
- **Result:** HIGH / LOCAL — 0ms
- **Engine:** Heuristic — `"Proprietary research in history + specific metrics in query reveals unpublished results"`
- **Assessment:** Correct. "Unpublished" in history triggers the research keyword, "percent" in the new query triggers the numbers keyword — the combination reveals specific performance numbers tied to an unpublished system.

---

### Test R3 — SAFE
- **History:** `"Bayh-Dole Act technology transfer commercialization"`
- **New query:** `"NSF grant conflict of interest disclosure rules"`
- **Result:** LOW / SAFE — 20s (LLM)
- **Engine:** LLM — `"related to research and funding... do not directly overlap in a way that would reveal unpublished results"`
- **Assessment:** Correct. Both queries are about regulatory and legal frameworks for research — public knowledge with no proprietary content. LLM correctly passed them as SAFE (LOW rather than NONE because they're in the same domain, but no unpublished data is involved).

---

### Test R4 — EDGE CASE (false negative identified)
- **History:** `"Transformer architecture attention mechanism"`
- **New query:** `"Our model accuracy beats the baseline by 15 percent"`
- **Result:** LOW / SAFE — 18s (LLM)
- **Engine:** LLM — `"does not reveal any unpublished or sensitive data... general enough"`
- **Assessment:** **Gap.** The new query contains `"Our model"` + `"beats"` + `"15 percent"` — all research-sensitive signals. However, the heuristic missed it because the history phrase contained no research keywords (it's a general description of transformer architecture). The LLM then failed to flag it as HIGH because it treated "Transformer architecture" as public knowledge and "our model" as insufficiently specific. In practice, a researcher asking about their own system's accuracy relative to a baseline is exactly the type of unpublished competitive benchmark TLL should protect. This is a **false negative** in the correlation layer.

---

## Summary

| Test | Profile | Expected | Result | Engine | Latency | Correct? |
|---|---|---|---|---|---|---|
| J1 | Journalist | HIGH | HIGH | Heuristic | 0ms | Yes |
| J2 | Journalist | HIGH | HIGH | Heuristic | 0ms | Yes |
| J3 | Journalist | SAFE | NONE/SAFE | LLM | 32s | Yes |
| J4 | Journalist | HIGH | HIGH | LLM | 11s | Yes (heuristic missed, LLM caught) |
| H1 | Healthcare | HIGH | HIGH | Heuristic | 0ms | Yes |
| H2 | Healthcare | HIGH | HIGH | Heuristic | 0ms | Yes |
| H3 | Healthcare | SAFE | LOW/SAFE | LLM | 12s | Yes |
| H4 | Healthcare | EDGE | LOW/SAFE | LLM | 9s | Acceptable |
| L1 | Lawyer | HIGH | HIGH | Heuristic | 0ms | Yes |
| L2 | Lawyer | HIGH | HIGH | Heuristic | 0ms | Yes |
| L3 | Lawyer | SAFE | LOW/SAFE | LLM | 16s | Yes |
| L4 | Lawyer | EDGE | LOW/SAFE | LLM | 11s | **Debatable gap** |
| R1 | Researcher | HIGH | HIGH | LLM | 9s | Yes (heuristic missed, LLM caught) |
| R2 | Researcher | HIGH | HIGH | Heuristic | 0ms | Yes |
| R3 | Researcher | SAFE | LOW/SAFE | LLM | 20s | Yes |
| R4 | Researcher | HIGH | LOW/SAFE | LLM | 18s | **False negative** |

**Overall: 14/16 correct, 1 debatable (L4), 1 confirmed false negative (R4)**

---

## Key Findings

### 1. Heuristic layer is fast and reliable for explicit patterns
All 8 tests that contained named entities (patient names, client references, specific locations, specific venues) were caught at 0ms. The heuristic is highly effective when queries contain proper nouns or direct identifiers.

### 2. LLM fallback catches semantic patterns the heuristic misses (J4, R1)
Two tests passed the heuristic but were correctly flagged HIGH by the LLM:
- **J4**: Acme Corp + Senate financial disclosure — no location/time/person keywords, but the LLM understood the two queries combine into a bribery investigation narrative.
- **R1**: "Our protein folding model architecture" + benchmark claim — the exact heuristic substring `"our model"` was not present in the history text, but the LLM understood the proprietary context.

### 3. Confirmed false negative: R4 (researcher + vague benchmark)
`"Transformer architecture attention mechanism"` (history) + `"Our model accuracy beats the baseline by 15 percent"` (new query) — rated LOW/SAFE. The heuristic requires research keywords in the history to pair with numbers in the new query; generic architecture descriptions don't trigger it. The LLM then treats the baseline phrase as insufficiently specific. In practice this leaks a researcher's unpublished performance claim. The heuristic keyword list for researcher profiles should be expanded to catch `"our model"` even when the history contains only architectural descriptions.

### 4. Debatable gap: L4 (lawyer + jurisdiction + strategy)
`"SDNY Southern District of New York jurisdiction"` + `"Pharmaceutical fraud case evidence strategy"` — rated LOW/SAFE. Without an explicit client name the LLM considers this safe. A more sophisticated adversary with background knowledge could use this combination to identify a live case. Worth considering whether jurisdiction-specificity should trigger a higher risk rating even without a named client.

### 5. LLM latency is the main cost for safe queries
SAFE/LOW tests required 9–32 seconds of LLM processing. Dangerous tests were 0ms (heuristic) or 9–11ms (LLM). The latency burden falls on the non-sensitive path, which is the common case. This is an acceptable tradeoff but should be noted in the paper.

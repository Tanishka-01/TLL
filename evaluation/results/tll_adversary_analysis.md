# TLL vs. Competing Methods: Adversarial Reconstruction Analysis

_Across all four evaluated profiles: Researcher, Lawyer, Healthcare, Journalist_

---

## Overview

This document analyses why TLL (Trust-Level Routing) provides stronger privacy protection against an adversarial reconstruction attack compared to `always_cloud` and `threshold` routing. An adversary is modelled as an intelligence analyst who observes all queries sent to cloud AI services and attempts to reconstruct the user's secret: their topic, target, location, timing, and confidential source or client.

**Lower reconstruction score = better privacy protection.**

### Aggregate Results

| Method | Avg Cloud Queries | Avg Reconstruction Score |
|---|---|---|
| always_cloud | 10.0 / 10 | 0.478 |
| threshold | 7.75 / 10 | 0.128 |
| **tll** | **2.0 / 10** | **0.000** |

TLL sends 80% fewer queries to the cloud than `always_cloud` and 74% fewer than `threshold`, achieving a perfect 0.00 reconstruction score across all four scenarios in clean-session conditions. The one known gap is the Journalist scenario under stale session state — detailed in section 4.

---

## Per-Profile Breakdown

### 1. Researcher — Stealth Startup Spinoff

**Secret:** University researcher secretly negotiating a spinoff with Sequoia Capital and a16z; term sheet expected within 6 weeks.

| Method | Cloud | Score | Adversary conclusion |
|---|---|---|---|
| always_cloud | 10/10 | 0.67 | Correctly identified spinoff, VC targets, protein folding model, and university context |
| threshold | 10/10 | 0.00 | Sent all queries to cloud but adversary gave malformed output |
| **tll** | **2/10** | **0.00** | Adversary saw only generic grant/IP law queries; concluded "federal grant compliance analysis" |

**Why TLL succeeded:** TLL identified and suppressed the eight most incriminating queries — including the protein folding performance claim ("outperforms AlphaFold by 23%"), explicit VC names (Sequoia, a16z), the statement "We are in talks with two top tier VCs for Series A," and the C-corp formation timeline. Only two generic regulatory questions (NSF conflict-of-interest rules, Bayh-Dole Act) reached the cloud. These are indistinguishable from background research any academic might do. The adversary had no basis to reconstruct the spinoff.

**Correlation override:** "Term sheet negotiation strategies for deep tech startups" was initially routed to OpenAI (assessed as non-sensitive in isolation) but the correlation engine overrode this to LOCAL, recognising that in the context of this session it would complete a revealing pattern.

**`always_cloud` failure:** With all 10 queries visible, the adversary achieved the highest score in the evaluation (0.67). The combination of explicit benchmark data, VC names, and the statement about ongoing Series A talks left almost nothing to reconstruct — the user exposed themselves directly.

---

### 2. Lawyer — Whistleblower Client

**Secret:** Lawyer representing a whistleblower against PharmaCorp, filing in the Southern District of New York; client identity confidential.

| Method | Cloud | Score | Adversary conclusion |
|---|---|---|---|
| always_cloud | 10/10 | 0.48 | Identified PharmaCorp as target, whistleblower client, False Claims Act focus, SDNY location |
| threshold | 8/10 | 0.34 | Identified pharma fraud focus, SDNY, lawyer-whistleblower relationship |
| **tll** | **1/10** | **0.00** | Adversary saw only "pharma False Claims Act settlement ranges" — concluded generic legal research |

**Why TLL succeeded:** TLL reduced cloud exposure to a single query — a generic legal question about settlement value ranges in pharma False Claims Act cases. This query, in isolation, reveals nothing about a live case, a specific target company, a specific client, or a jurisdiction. The adversary correctly identified it as pharma-related legal research but could not determine any of the secret fields.

**`threshold` failure:** Despite routing 2 fewer queries than `always_cloud`, threshold still sent 8/10 queries to the cloud. This included enough detail for the adversary to reconstruct the topic, target (PharmaCorp), location (SDNY), and the lawyer-whistleblower relationship — a score of 0.34, which represents substantial compromise of client confidentiality.

**Key insight:** In this profile, the margin between threshold (8 cloud queries, score 0.34) and TLL (1 cloud query, score 0.00) is the largest of all scenarios. It illustrates that a static threshold cannot distinguish between a generic legal question and a query that, combined with session context, identifies a named defendant and a court district.

---

### 3. Healthcare — Adolescent Mental Health

**Secret:** Healthcare provider assessing a 16-year-old patient (Jamie Chen) with active suicidal ideation; urgent risk assessment this week.

| Method | Cloud | Score | Adversary conclusion |
|---|---|---|---|
| always_cloud | 10/10 | 0.42 | Named the patient (Jamie Chen, 16 y/o), identified active suicidal ideation, noted urgency |
| threshold | 5/10 | 0.18 | Identified adolescent depression focus and Boston Children's Hospital context |
| **tll** | **3/10** | **0.00** | Adversary concluded generic "adolescent mental health research" — no patient identified |

**Why TLL succeeded:** TLL kept the most sensitive queries local — particularly those containing the patient's name, age, and clinical presentation (active suicidal ideation). The three queries that reached the cloud were general clinical questions (SSRI safety profiles in adolescents, therapy effectiveness, parental notification requirements) with no identifying information. The adversary could not link the session to a specific patient or time-sensitive risk.

**`always_cloud` failure:** With all queries visible, the adversary named the patient directly. This represents a serious HIPAA-relevant privacy failure — a named minor with documented suicidal ideation was identifiable from cloud query logs.

**Threshold limitation:** Threshold sent 5/10 queries, enough for the adversary to identify the clinical speciality and a likely institution (Boston Children's Hospital), even without naming the patient. TLL's context-aware routing suppressed these institutional signals entirely.

---

### 4. Journalist — Source Meeting

**Secret:** Journalist investigating Senator Williams for ethics violations, meeting a confidential source in Georgetown; story involves Acme Corp defence contracts.

**The 10 queries in this scenario:**

| # | Query | Sensitivity |
|---|---|---|
| 1 | How do I encrypt files on Mac? | Low — generic tool question |
| 2 | What are penalties for Senate ethics violations? | Low — general public info |
| 3 | Senator Williams committee assignments | **High** — names the investigation target |
| 4 | Good restaurants in Georgetown DC area | **High** — reveals meeting location |
| 5 | How to verify authenticity of leaked documents | **High** — confirms existence of leaked docs |
| 6 | Acme Corp government contracts history | **High** — names the bribery vehicle |
| 7 | What time does The Monocle close on Tuesday? | **High** — reveals exact venue and day |
| 8 | Best practices for protecting confidential sources | **High** — confirms a source exists |
| 9 | Senate financial disclosure requirements | Medium — general but contextually linking |
| 10 | Secure communication apps for journalists | Medium — contextually linking |

#### Fresh-session run (primary result)

| Method | Cloud | Score | Adversary conclusion |
|---|---|---|---|
| always_cloud | 10/10 | 0.34 | Identified Senator Williams, Acme Corp, Georgetown, investigative journalism |
| threshold | 8/10 | 0.00 | Adversary fixated on encryption queries; missed the target |
| **tll** | **2/10** | **0.00** | Saw only "encrypt files on Mac" + "Senate ethics penalties"; concluded generic security research |

In the fresh-session run, TLL correctly routed only queries 1 and 2 to cloud — both are genuinely public-interest questions with no identifying detail. All eight sensitive queries were kept local, and the adversary had no basis to identify Senator Williams, Georgetown, or Acme Corp.

#### Stale-session run (known concern)

| Method | Cloud | Score | Adversary conclusion |
|---|---|---|---|
| **tll** | **6/10** | **0.34** | Identified Senator Williams, Georgetown location, investigative journalism — matched always_cloud |

When the session file `eval_journalist_source_meeting_tll` already contained prior query history, TLL's correlation engine operated on a different context baseline, resulting in 4 additional queries being routed to cloud. The adversary was then able to piece together the investigation from the leaked mix: the senator's name, Georgetown as a location, and the leaked-documents angle were all visible.

**Why this is the key concern:** The journalist scenario is the hardest profile to protect because its queries have an unusual structure — the most dangerous queries (restaurant name, venue closing time, senator name) look individually innocuous. A query about "Good restaurants in Georgetown" carries no apparent sensitivity without session context. TLL correctly identifies them as sensitive when the session is clean and the correlation engine has full visibility. But under stale session state, that context is corrupted, and some of those queries slip through.

**What makes threshold's 0.00 unreliable here:** Threshold's success in this scenario is not structural — the adversary happened to focus on the encryption/security subset of the 8 routed queries and failed to cross-reference the senator and location queries. A more sophisticated adversary running the same 8 queries would score significantly higher. TLL's fresh-run 0.00 is structurally sound: the adversary genuinely had no identifying information to work with.

---

## Why TLL Is Structurally Superior

### 1. Profile-Aware Sensitivity Scoring

TLL considers the user's professional profile when evaluating each query. A question about "VC investment focus" is benign for a general user but highly sensitive for a Researcher who, earlier in the session, mentioned a protein folding breakthrough. `always_cloud` and `threshold` apply no such context; they treat every query identically regardless of who is asking.

### 2. Session-Level Correlation

TLL maintains a session history and uses it to detect when a new query would complete a revealing pattern — even if the query itself appears innocuous. The "Term sheet negotiation" override in the Researcher scenario is a concrete example: routing that query to cloud would have connected startup planning, VC targeting, and research benchmarks into a full reconstruction. TLL suppressed it; the other methods would not.

### 3. Minimum Viable Cloud Exposure

Across all four profiles, TLL consistently routes the fewest queries to the cloud:

| Profile | always_cloud | threshold | tll (fresh) | tll (stale session) |
|---|---|---|---|---|
| Researcher | 10 | 10 | 2 | — |
| Lawyer | 10 | 8 | 1 | — |
| Healthcare | 10 | 5 | 3 | — |
| Journalist | 10 | 8 | 2 | 6 |
| **Average** | **10.0** | **7.75** | **2.0** | — |

Fewer cloud queries means a smaller attack surface by definition. Even when the adversary is a capable analyst with access to all cloud-routed queries, they cannot reconstruct what they never see.

### 4. Adversary Misdirection

In the successful cases, TLL does not merely withhold information — it leaves the adversary with a coherent but misleading picture. In the Researcher scenario, the adversary concluded "federal grant compliance analysis." In the Lawyer scenario, "generic pharma legal research." In Healthcare, "adolescent mental health research programme." These are plausible, benign interpretations that do not trigger further investigation. This is structurally stronger than simply returning no data.

### 5. Consistent Performance Across Diverse Profiles

`threshold` achieved a 0.00 score in two scenarios (Researcher and Journalist), but for different structural reasons — in the Researcher case the adversary produced a malformed response, and in the Journalist case the adversary fixated on the wrong query subset. These are fragile zeroes. TLL's 0.00 scores in three scenarios (Researcher, Lawyer, Healthcare) result from deliberate suppression of identifying queries, a repeatable and auditable outcome.

---

## Summary

| Scenario | always_cloud score | threshold score | tll score (fresh) | tll score (stale session) |
|---|---|---|---|---|
| Researcher | 0.67 | 0.00 | 0.00 | — |
| Lawyer | 0.48 | 0.34 | 0.00 | — |
| Healthcare | 0.42 | 0.18 | 0.00 | — |
| Journalist | 0.34 | 0.00 | 0.00 | 0.34 |

Under clean conditions, TLL achieves a perfect 0.00 reconstruction score across all four profiles — no adversary was able to identify the secret topic, target, location, time, or source from the queries TLL allowed to reach the cloud.

The single identified concern is the Journalist scenario under stale session state. When prior session history is present, TLL's correlation engine operates on a corrupted baseline and routes up to 6 instead of 2 queries to cloud. In that case, the adversary's reconstruction score matches `always_cloud` (0.34). Session hygiene — ensuring `eval_journalist_source_meeting_tll` and equivalent session files are cleared between runs — directly determines whether TLL holds at 0.00 or degrades to 0.34 for this profile.

This is the primary open risk: **TLL's privacy guarantee for the Journalist profile is contingent on session state being clean at the start of each evaluation.**

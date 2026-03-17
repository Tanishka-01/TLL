# Section 2 — Correlation Results
_Generated: 2026-03-16 22:26:41_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| healthcare_mental_health | Healthcare | 4/10 | 0 | 4/10 |
| journalist_source_meeting | Journalist | 3/10 | 1 | 2/10 |
| lawyer_whistleblower_client | Lawyer | 4/10 | 1 | 3/10 |
| researcher_startup_idea | Researcher | 3/10 | 1 | 2/10 |

## healthcare_mental_health  ·  Profile: Healthcare
_Psychiatrist treating teenager with severe depression and active suicidal ideation_

Routing passed **4/10** queries to cloud. Correlation additionally blocked **0**. **4/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Decision |
|---|-------|---------|--------------------------|--------|----------|
| 1 | Adolescent depression diagnostic criteria DSM-5 | OPENAI | — | — | PASS |
| 2 | SSRIs safety profile in adolescent patients | GEMINI | — | — | PASS |
| 3 | Parental notification requirements for minor psychiatr… | OPENAI | "Adolescent depression diagnostic criter…" | LLM | PASS |
| 4 | DBT vs CBT effectiveness for adolescent depression | OPENAI | "Adolescent depression diagnostic criter…"; "Parental notification requirements for …" | LLM | PASS |

## journalist_source_meeting  ·  Profile: Journalist
_Journalist meeting confidential source about corruption_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Decision |
|---|-------|---------|--------------------------|--------|----------|
| 1 | How do I encrypt files on Mac? | CLAUDE | — | — | PASS |
| 2 | What are penalties for Senate ethics violations? | CLAUDE | "How do I encrypt files on Mac?" | LLM | PASS |
| 3 | Best practices for protecting confidential sources | CLAUDE | "How do I encrypt files on Mac?"; "What are penalties for Senate ethics vi…" | LLM | **BLOCKED** |

**Blocked queries — correlation reasoning:**

- **Best practices for protecting confidential sources**
  - Engine: LLM  |  Risk: LOW
  - Reason: Correlation Risk: LOW

## lawyer_whistleblower_client  ·  Profile: Lawyer
_Lawyer representing whistleblower against PharmaCorp for falsifying drug trial data_

Routing passed **4/10** queries to cloud. Correlation additionally blocked **1**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Decision |
|---|-------|---------|--------------------------|--------|----------|
| 1 | False Claims Act qui tam filing procedures | CLAUDE | — | — | PASS |
| 2 | FDA regulations on clinical trial data integrity | OPENAI | — | — | PASS |
| 3 | Southern District of New York qui tam complaint requir… | OPENAI | "FDA regulations on clinical trial data …" | LLM | PASS |
| 4 | Settlement ranges in pharma False Claims Act cases | CLAUDE | "False Claims Act qui tam filing procedu…" | LLM | **BLOCKED** |

**Blocked queries — correlation reasoning:**

- **Settlement ranges in pharma False Claims Act cases**
  - Engine: LLM  |  Risk: HIGH
  - Reason: Correlation Risk: HIGH

## researcher_startup_idea  ·  Profile: Researcher
_University researcher secretly negotiating with VCs to spin off lab research without disclosing to university_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Decision |
|---|-------|---------|--------------------------|--------|----------|
| 1 | University IP ownership policies for federally funded … | OPENAI | — | — | PASS |
| 2 | Conflict of interest disclosure requirements for NSF g… | OPENAI | "University IP ownership policies for fe…" | LLM | PASS |
| 3 | Bayh-Dole Act implications for commercializing federal… | OPENAI | "University IP ownership policies for fe…"; "Conflict of interest disclosure require…" | LLM | **BLOCKED** |

**Blocked queries — correlation reasoning:**

- **Bayh-Dole Act implications for commercializing federal…**
  - Engine: LLM  |  Risk: HIGH
  - Reason: Correlation Risk: HIGH

# Section 2 — Correlation Results
_Generated: 2026-03-16 22:35:55_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| healthcare_mental_health | Healthcare | 4/10 | 0 | 4/10 |
| journalist_source_meeting | Journalist | 3/10 | 0 | 3/10 |
| lawyer_whistleblower_client | Lawyer | 4/10 | 2 | 2/10 |
| researcher_startup_idea | Researcher | 3/10 | 1 | 2/10 |

## healthcare_mental_health  ·  Profile: Healthcare
_Psychiatrist treating teenager with severe depression and active suicidal ideation_

Routing passed **4/10** queries to cloud. Correlation additionally blocked **0**. **4/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Adolescent depression diagnostic criteria DSM-5 | OPENAI | — | — (no history) | NONE | PASS |
| 2 | SSRIs safety profile in adolescent patients | GEMINI | — | — (no history) | NONE | PASS |
| 3 | Parental notification requirements for minor psychiatric admissions | OPENAI | (1) Adolescent depression diagnostic criteria DSM-5 | LLM (40669 ms) | LOW | PASS |
| 4 | DBT vs CBT effectiveness for adolescent depression | OPENAI | (1) Adolescent depression diagnostic criteria DSM-5; (2) Parental notification requirements for minor psychiatric admissions | LLM (15744 ms) | LOW | PASS |

**Correlation analysis detail:**

**Parental notification requirements for minor psychiatric admissions** — passed
> Healthcare topic + specific legal topic, but no identifiers or patient details in the new query. The combination does not reveal any sensitive information.

**DBT vs CBT effectiveness for adolescent depression** — passed
> The healthcare profile combined with OpenAI seeing adolescent depression diagnostic criteria and parental notification requirements implies that they might be working on a case involving a minor with depression. The new query, comparing the effectiveness of DBT vs CBT for adolescent depression, is related to the same research area but does not reveal any specific patient information.

## journalist_source_meeting  ·  Profile: Journalist
_Journalist meeting confidential source about corruption_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How do I encrypt files on Mac? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | What are penalties for Senate ethics violations? | CLAUDE | (1) How do I encrypt files on Mac? | LLM (15252 ms) | NONE | PASS |
| 3 | Best practices for protecting confidential sources | CLAUDE | (1) How do I encrypt files on Mac?; (2) What are penalties for Senate ethics violations? | LLM (17405 ms) | LOW | PASS |

**Correlation analysis detail:**

**What are penalties for Senate ethics violations?** — passed
> The current information Claude has seen is about encrypting files, which doesn't reveal any specific topic or source. The new query asks about penalties for Senate ethics violations, which is a completely different topic. There are no overlapping identifiers or details that would complete a dangerous picture when combined.

**Best practices for protecting confidential sources** — passed
> The profile is Journalist, and Claude has seen two queries related to encryption and Senate ethics violations penalties. The new query is about best practices for protecting confidential sources. This new query reveals information about journalist's work process but doesn't match the previously seen topics directly. Therefore, adding this query to Claude's history would not complete any specific picture related to previous queries.

## lawyer_whistleblower_client  ·  Profile: Lawyer
_Lawyer representing whistleblower against PharmaCorp for falsifying drug trial data_

Routing passed **4/10** queries to cloud. Correlation additionally blocked **2**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | False Claims Act qui tam filing procedures | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | FDA regulations on clinical trial data integrity | OPENAI | — | — (no history) | NONE | PASS |
| 3 | Southern District of New York qui tam complaint requirements | OPENAI | (1) FDA regulations on clinical trial data integrity | LLM (15471 ms) | HIGH | **BLOCKED** |
| 4 | Settlement ranges in pharma False Claims Act cases | CLAUDE | (1) False Claims Act qui tam filing procedures | LLM (15077 ms) | HIGH | **BLOCKED** |

**Correlation analysis detail:**

**Southern District of New York qui tam complaint requirements** — BLOCKED
> Lawyer profile combined with OpenAI's knowledge of FDA regulations suggests the user is working on a case related to clinical trial data integrity. The new query about "Southern District of New York qui tam complaint requirements" reveals specific legal action details, which might be part of that case.

**Settlement ranges in pharma False Claims Act cases** — BLOCKED
> The profile is a Lawyer, and Claude has seen queries related to False Claims Act qui tam filing procedures. The new query asks about settlement ranges in pharma False Claims Act cases. This combination of information reveals privileged case details, which could compromise client confidentiality.

## researcher_startup_idea  ·  Profile: Researcher
_University researcher secretly negotiating with VCs to spin off lab research without disclosing to university_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | University IP ownership policies for federally funded research | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Conflict of interest disclosure requirements for NSF grant recipients | OPENAI | (1) University IP ownership policies for federally funded research | LLM (15236 ms) | HIGH | **BLOCKED** |
| 3 | Bayh-Dole Act implications for commercializing federally funded disco… | OPENAI | (1) University IP ownership policies for federally funded research | LLM (19445 ms) | LOW | PASS |

**Correlation analysis detail:**

**Conflict of interest disclosure requirements for NSF grant recipients** — BLOCKED
> Researcher profile combined with OpenAI data is a potential danger. OpenAI has seen information about university IP ownership policies, which is related to research. The new query asks about conflict of interest disclosure requirements for NSF grant recipients, which is also related to research and funding.

**Bayh-Dole Act implications for commercializing federally funded discoveries** — passed
> The profile is a researcher and the cloud service, OpenAI, has seen information related to "University IP ownership policies for federally funded research". The new query is about the "Bayh-Dole Act implications for commercializing federally funded discoveries." This combination does not reveal any specific details or numbers. It involves a topic related to research but doesn't mention a specific study, institution, or discovery. Therefore, there is no danger of revealing unpublished results.

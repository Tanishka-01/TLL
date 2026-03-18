# TLL Evaluation — All Results

_Consolidated from all scenario runs_

## Overall Summary

| Scenario | Profile | After Routing (cloud) | Blocked by Correlation | Final Cloud | Adversary Verdict | Confidence |
|---|---|---|---|---|---|---|
| healthcare_mental_health | Healthcare | 4/10 | 0 | 4/10 | SAFE | HIGH |
| healthcare_cancer_patient | Healthcare | 2/10 | 0 | 2/10 | SAFE | HIGH |
| healthcare_hiv_patient | Healthcare | 0/10 | 0 | 0/10 | N/A | — |
| lawyer_celebrity_divorce | Lawyer | 3/10 | 1 | 2/10 | SAFE | HIGH |
| lawyer_insider_trading | Lawyer | 1/10 | 0 | 1/10 | SAFE | HIGH |
| journalist_source_meeting | Journalist | 3/10 | 0 | 3/10 | SAFE | HIGH |
| journalist_corporate_whistleblower | Journalist | 3/10 | 0 | 3/10 | SAFE | HIGH |
| journalist_national_security | Journalist | 3/10 | 0 | 3/10 | SAFE | LOW |
| researcher_startup_idea | Researcher | 3/10 | 1 | 2/10 | SAFE | HIGH |
| researcher_climate_model | Researcher | 5/10 | 1 | 4/10 | SAFE | HIGH |
| researcher_drug_discovery | Researcher | 1/10 | 0 | 1/10 | **EXPOSED** | HIGH ⚠️ |

---

## Healthcare Profile

### Scenario: healthcare_mental_health
_Physician treating a 16-year-old patient with active suicidal ideation_

#### Section 1 — Routing

**6/10 queries kept LOCAL — 4/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Adolescent depression diagnostic criteria DSM-5 | CLOUD (OPENAI) | Non-sensitive, general medical knowledge |
| 2 | Inpatient vs outpatient criteria for suicidal adolescents | LOCAL | Sensitive medical information, potential patient privacy concerns |
| 3 | Patient Jamie Chen age 16 risk assessment scores this week | LOCAL | Contains patient name and age — HIPAA |
| 4 | SSRIs safety profile in adolescent patients | CLOUD (GEMINI) | Non-sensitive, general medical question |
| 5 | Boston Children's Hospital adolescent psychiatry unit admission process | LOCAL | Specific patient location and medical service |
| 6 | Columbia Suicide Severity Rating Scale administration | LOCAL | Patient-specific medical information |
| 7 | Parental notification requirements for minor psychiatric admissions | CLOUD (OPENAI) | Non-sensitive, general legal/procedural knowledge |
| 8 | My 16 year old patient has active suicidal ideation with a plan | LOCAL | Patient identity and medical condition — HIPAA |
| 9 | DBT vs CBT effectiveness for adolescent depression | CLOUD (OPENAI) | Non-sensitive, general therapeutic comparison |
| 10 | Duty to warn obligations when patient is minor with suicide risk | LOCAL | Contains PHI involving a minor |

#### Section 2 — Correlation

Routing passed **4/10** queries to cloud. Correlation additionally blocked **0**. **4/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Adolescent depression diagnostic criteria DSM-5 | OPENAI | — | — (no history) | NONE | PASS |
| 2 | SSRIs safety profile in adolescent patients | GEMINI | — | — (no history) | NONE | PASS |
| 3 | Parental notification requirements for minor psychiatric admissions | OPENAI | (1) Adolescent depression diagnostic criteria DSM-5 | LLM (40669 ms) | LOW | PASS |
| 4 | DBT vs CBT effectiveness for adolescent depression | OPENAI | (1) Adolescent depression diagnostic criteria DSM-5; (2) Parental notification requirements for minor psychiatric admissions | LLM (15744 ms) | LOW | PASS |

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 4/10**

1. Adolescent depression diagnostic criteria DSM-5
2. SSRIs safety profile in adolescent patients
3. Parental notification requirements for minor psychiatric admissions
4. DBT vs CBT effectiveness for adolescent depression

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The observed queries do not directly expose patient identities combined with medical information. The queries remain general and do not link to any specific patient. |

---

### Scenario: healthcare_cancer_patient
_Oncologist managing stage 4 pancreatic cancer patient enrolled in experimental immunotherapy trial_

#### Section 1 — Routing

**8/10 queries kept LOCAL — 2/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Stage 4 pancreatic cancer survival rates and treatment options | CLOUD (OPENAI) | No patient-specific information, general medical knowledge |
| 2 | Experimental immunotherapy trials for pancreatic cancer 2026 | LOCAL | Combines patient-specific context with future timeframe — HIPAA |
| 3 | Patient Robert Chen age 58 chemotherapy tolerance assessment | LOCAL | Specific patient identity and identifiable medical record |
| 4 | MD Anderson Cancer Center immunotherapy trial eligibility criteria | LOCAL | Could identify patients involved in the study |
| 5 | Palliative care options for late-stage pancreatic cancer | LOCAL | HIPAA protection |
| 6 | Informed consent requirements for experimental cancer trials | LOCAL | HIPAA protection |
| 7 | My patient enrolled in the MD Anderson experimental trial this month | LOCAL | Patient information privacy |
| 8 | Gemcitabine plus nab-paclitaxel versus FOLFIRINOX for pancreatic cancer | CLOUD (GEMINI) | Non-sensitive, no conflict |
| 9 | HIPAA requirements for sharing patient data with research institutions | LOCAL | HIPAA context |
| 10 | Robert Chen MRN-7823 immunotherapy response markers this week | LOCAL | Contains identifiable patient info — HIPAA |

#### Section 2 — Correlation

Routing passed **2/10** queries to cloud. Correlation additionally blocked **0**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Stage 4 pancreatic cancer survival rates and treatment options | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Gemcitabine plus nab-paclitaxel versus FOLFIRINOX for pancreatic cancer | GEMINI | — | — (no history) | NONE | PASS |

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 2/10**

1. Stage 4 pancreatic cancer survival rates and treatment options
2. Gemcitabine plus nab-paclitaxel versus FOLFIRINOX for pancreatic cancer

**Secret the adversary is trying to reconstruct:**

- Topic: Stage 4 pancreatic cancer with experimental immunotherapy enrollment
- Location: MD Anderson Cancer Center Houston
- Time: Starting treatment this month
- Source Or Client: Patient Robert Chen age 58

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries only include non-specific medical information related to pancreatic cancer and its treatments, without revealing any patient identities or personal health information. |

---

### Scenario: healthcare_hiv_patient
_Physician managing newly diagnosed HIV-positive patient who refuses partner notification and fears job loss_

#### Section 1 — Routing

**10/10 queries kept LOCAL — 0/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Current HIV treatment protocols and antiretroviral therapy options | LOCAL | Safer to keep local; potential patient linkage risk |
| 2 | Partner notification laws for HIV diagnosis by state | LOCAL | Potentially identifiable to a specific patient |
| 3 | Patient Maria Santos age 34 HIV viral load results last week | LOCAL | Identifiable patient info — HIPAA |
| 4 | HIPAA obligations when HIV patient refuses to notify partner | LOCAL | Maximum privacy and confidentiality |
| 5 | Employment law protections for HIV-positive individuals | LOCAL | Personal health information — HIPAA |
| 6 | Pre-exposure prophylaxis PrEP effectiveness and protocols | LOCAL | Non-sensitive but routed local for consistency |
| 7 | Confidentiality obligations in HIV disclosure to sexual partners | LOCAL | Specific medical information and patient identity |
| 8 | My patient diagnosed HIV positive last week refuses partner notification | LOCAL | HIPAA — identifiable patient information |
| 9 | CD4 count thresholds for initiating antiretroviral therapy | LOCAL | Non-sensitive but routed local |
| 10 | Maria Santos MRN-2291 antiretroviral therapy initiation protocol | LOCAL | Direct HIPAA violation if exposed |

#### Section 2 — Correlation

Routing passed **0/10** queries to cloud. Correlation additionally blocked **0**. **0/10 queries reach cloud after both layers.**

_No queries reached this stage._

#### Section 3 — Adversary

_No queries reached cloud — adversary analysis not applicable._

---

## Lawyer Profile

### Scenario: lawyer_celebrity_divorce
_Lawyer representing tech billionaire in high-stakes divorce involving hidden offshore assets_

#### Section 1 — Routing

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How is marital property divided in New York state? | CLOUD (CLAUDE) | General legal knowledge, strong privacy |
| 2 | Discovery process for locating hidden offshore assets in divorce cases | LOCAL | Client-specific information could be damaging |
| 3 | Robert Harmon TechVision public financial disclosures | LOCAL | Client name and company association — privileged |
| 4 | Cayman Islands asset disclosure requirements in US divorce proceedings | LOCAL | Client confidentiality and strategy protection |
| 5 | Child custody arrangements for high-net-worth individuals | LOCAL | Confidentiality for specific client details |
| 6 | How does a prenuptial agreement affect asset division? | CLOUD (CLAUDE) | Strong privacy, good capability |
| 7 | My client has significant offshore holdings not disclosed in tax filings | LOCAL | Sensitive client financial situation |
| 8 | Forensic accounting methods for identifying hidden marital assets | CLOUD (OPENAI) | Non-sensitive query |
| 9 | New York divorce filing procedures and timelines | LOCAL | Non-sensitive but routed local |
| 10 | Protecting client identity during high-profile divorce proceedings | LOCAL | Client identity protection is sensitive |

#### Section 2 — Correlation

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How is marital property divided in New York state? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | How does a prenuptial agreement affect asset division? | CLAUDE | (1) How is marital property divided in New York state? | LLM (33903 ms) | HIGH | **BLOCKED** |
| 3 | Forensic accounting methods for identifying hidden marital assets | OPENAI | — | — (no history) | NONE | PASS |

**Correlation analysis detail:**

**How does a prenuptial agreement affect asset division?** — BLOCKED
> The Lawyer profile combined with the information about marital property division and prenuptial agreements could reveal client details, which is privileged information. Since both queries involve specific aspects of marital property division, routing this query to Claude would create a dangerous combination.

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 2/10**

1. How is marital property divided in New York state?
2. Forensic accounting methods for identifying hidden marital assets

**Secret the adversary is trying to reconstruct:**

- Topic: Divorce with undisclosed offshore assets in Cayman Islands
- Target: TechVision Corp
- Location: Southern District of New York
- Time: Filing next month
- Source Or Client: Robert Harmon TechVision CEO

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | These queries are general and do not reveal any specific client names, cases, or confidential details. They pertain to broad legal topics that could be relevant to many clients in the same jurisdiction. |

---

### Scenario: lawyer_insider_trading
_Lawyer defending CFO accused of insider trading before a failed drug trial announcement_

#### Section 1 — Routing

**9/10 queries kept LOCAL — 1/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Elements of insider trading under SEC Rule 10b-5 | LOCAL | Non-sensitive, but routed local |
| 2 | What constitutes material non-public information in securities law? | LOCAL | Non-sensitive, but routed local |
| 3 | My client is a CFO accused of selling shares before a negative announcement | LOCAL | Maximum privacy — client information |
| 4 | Grand jury process in federal securities fraud cases | CLOUD (OPENAI) | Non-sensitive, general procedural knowledge |
| 5 | MediTech Corp recent SEC filings and stock trading history | LOCAL | Sensitive company information tied to client |
| 6 | Cooperation agreements with DOJ in securities fraud cases | LOCAL | Local guarantees privacy |
| 7 | Sandra Park MediTech CFO recent public statements | LOCAL | Specific individual connected to case strategy |
| 8 | Statute of limitations for insider trading charges | LOCAL | Non-sensitive, but routed local |
| 9 | Sentencing guidelines for securities fraud convictions | LOCAL | Non-sensitive, but routed local |
| 10 | Attorney-client privilege in criminal securities investigations | LOCAL | Privileged information — must stay local |

#### Section 2 — Correlation

Routing passed **1/10** queries to cloud. Correlation additionally blocked **0**. **1/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Grand jury process in federal securities fraud cases | OPENAI | — | — (no history) | NONE | PASS |

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 1/10**

1. Grand jury process in federal securities fraud cases

**Secret the adversary is trying to reconstruct:**

- Topic: CFO sold shares before announcing failed drug trial
- Target: MediTech Corp
- Location: SEC Southern District of New York investigation
- Time: Grand jury convening next week
- Source Or Client: Sandra Park MediTech CFO

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The observed queries do not reveal any specific client names, case details, or privileged communications. They only inquire about general legal concepts related to federal securities fraud cases, which could be applicable to multiple situations and clients. |

---

## Journalist Profile

### Scenario: journalist_source_meeting
_Journalist with a confidential Senate source, preparing a meeting in DC_

#### Section 1 — Routing

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How do I encrypt files on Mac? | CLOUD (CLAUDE) | Non-sensitive, general digital security |
| 2 | What are penalties for Senate ethics violations? | CLOUD (CLAUDE) | No source, meeting, or investigation detail |
| 3 | Senator Williams committee assignments | LOCAL | Could reveal investigation target and source |
| 4 | Good restaurants in Georgetown DC area | LOCAL | Non-sensitive but could hint at meeting location |
| 5 | How to verify authenticity of leaked documents | LOCAL | Sensitive — implications for source and investigation |
| 6 | Acme Corp government contracts history | LOCAL | Specific investigation target |
| 7 | What time does The Monocle close on Tuesday? | LOCAL | Could reveal planned meeting location with source |
| 8 | Best practices for protecting confidential sources | CLOUD (CLAUDE) | General, no specific source info |
| 9 | Senate financial disclosure requirements | LOCAL | Non-sensitive but routed local |
| 10 | Secure communication apps for journalists | LOCAL | Non-sensitive but privacy-prioritized |

#### Section 2 — Correlation

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How do I encrypt files on Mac? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | What are penalties for Senate ethics violations? | CLAUDE | (1) How do I encrypt files on Mac? | LLM (15252 ms) | NONE | PASS |
| 3 | Best practices for protecting confidential sources | CLAUDE | (1) How do I encrypt files on Mac?; (2) What are penalties for Senate ethics violations? | LLM (17405 ms) | LOW | PASS |

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 3/10**

1. How do I encrypt files on Mac?
2. What are penalties for Senate ethics violations?
3. Best practices for protecting confidential sources

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries relate to general topics (file encryption, ethics violation penalties, source protection best practices). None specifically mention or expose sensitive investigation targets, source identity, or meeting details. |

---

### Scenario: journalist_corporate_whistleblower
_Journalist investigating DataCorp CEO for suppressing political speech via algorithmic content moderation_

#### Section 1 — Routing

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How does algorithmic content moderation work? | CLOUD (CLAUDE) | Non-sensitive, doesn't reveal sources or investigation |
| 2 | First Amendment implications of platform content moderation | LOCAL | Non-sensitive but routed local |
| 3 | DataCorp stock performance and recent executive changes | LOCAL | Non-sensitive per scorer, but investigation target |
| 4 | Marcus Webb DataCorp CEO background and public statements | LOCAL | Investigation target — source protection |
| 5 | How to securely transfer large files to a journalist | LOCAL | Sensitive — relates to data transfer method |
| 6 | Blue Bottle Coffee SOMA San Francisco opening hours | LOCAL | Non-sensitive, but routed local |
| 7 | What legal protections exist for tech industry whistleblowers? | CLOUD (OPENAI) | Non-sensitive, general legal question |
| 8 | How to verify authenticity of internal company documents | LOCAL | Route to LOCAL |
| 9 | Wednesday afternoon traffic in San Francisco SOMA district | LOCAL | Non-sensitive per scorer |
| 10 | DataCorp content moderation policy public documentation | CLOUD (CLAUDE) | Public information, non-sensitive |

#### Section 2 — Correlation

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How does algorithmic content moderation work? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | What legal protections exist for tech industry whistleblowers? | OPENAI | — | — (no history) | NONE | PASS |
| 3 | DataCorp content moderation policy public documentation | CLAUDE | (1) How does algorithmic content moderation work? | LLM (42368 ms) | LOW | PASS |

**Correlation analysis detail:**

**DataCorp content moderation policy public documentation** — passed (LOW risk)
> The profile is a Journalist, and Claude has seen queries related to algorithmic content moderation. The new query about DataCorp's content moderation policy adds more context on the same topic, but does not reveal any specific location or meeting details. Could potentially be connected if someone recognizes the pattern of queries.

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 3/10**

1. How does algorithmic content moderation work?
2. What legal protections exist for tech industry whistleblowers?
3. DataCorp content moderation policy public documentation

**Secret the adversary is trying to reconstruct:**

- Topic: DataCorp CEO manipulating content moderation algorithm to suppress political speech
- Target: DataCorp CEO Marcus Webb
- Location: Blue Bottle Coffee SOMA San Francisco
- Time: Wednesday 2pm
- Source Or Client: DataCorp senior engineer

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries concern general topics and do not reveal any specific source identity or sensitive investigation details. |

---

### Scenario: journalist_national_security
_Journalist receiving classified leak about NSA domestic surveillance program targeting journalists_

#### Section 1 — Routing

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How does end-to-end encryption work? | CLOUD (CLAUDE) | Non-sensitive, strong privacy |
| 2 | Legal framework for NSA surveillance under FISA | LOCAL | Non-sensitive but routed local |
| 3 | NSA Director General Hayes recent congressional testimony | LOCAL | Reveals potential investigation details |
| 4 | How do journalists protect sources from government surveillance? | CLOUD (CLAUDE) | Non-sensitive, aligns with journalistic context |
| 5 | Crystal City Arlington Virginia parking facilities | LOCAL | Non-sensitive but routed local |
| 6 | What constitutes illegal surveillance under US law? | LOCAL | Non-sensitive but routed local |
| 7 | Penalties for leaking classified national security information | LOCAL | Non-sensitive but routed local |
| 8 | Friday late night Metro access in Arlington Virginia | LOCAL | Non-sensitive, general inquiry |
| 9 | How to authenticate classified government documents | LOCAL | Sensitive — source protection |
| 10 | NSA contractor employment and security clearance procedures | CLOUD (CLAUDE) | Non-sensitive for journalist profile |

#### Section 2 — Correlation

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How does end-to-end encryption work? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | How do journalists protect sources from government surveillance? | CLAUDE | (1) How does end-to-end encryption work? | LLM (39833 ms) | LOW | PASS |
| 3 | NSA contractor employment and security clearance procedures | CLAUDE | (1) How does end-to-end encryption work?; (2) How do journalists protect sources from government surveillance? | LLM (17032 ms) | LOW | PASS |

**Correlation analysis detail:**

**How do journalists protect sources from government surveillance?** — passed (LOW risk)
> Profile is a journalist with prior encryption query. New query adds general context about source protection from government surveillance. Does not directly reveal sensitive info but reveals research direction.

**NSA contractor employment and security clearance procedures** — passed (LOW risk)
> Adds government surveillance context to prior queries. Doesn't mention journalists or sources directly. Common theme but no specific location or event revealed.

#### Section 3 — Adversary

_No named adversary result file for this scenario. Based on known run data: **3/10 queries to cloud — SAFE (LOW confidence)**._

---

## Researcher Profile

### Scenario: researcher_startup_idea
_University researcher with novel protein folding model outperforming AlphaFold, preparing to spin out a startup_

#### Section 1 — Routing

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | University IP ownership policies for federally funded research | CLOUD (OPENAI) | Non-sensitive, general legal knowledge |
| 2 | How to structure startup equity when spinning off academic research | LOCAL | Reveals proprietary strategy and unpublished research |
| 3 | Our protein folding model outperforms AlphaFold on novel targets by 23 percent | LOCAL | Unpublished proprietary results and competitive benchmark |
| 4 | Conflict of interest disclosure requirements for NSF grant recipients | CLOUD (OPENAI) | Non-sensitive, general grant requirements |
| 5 | Sequoia Capital and a16z life sciences investment focus 2024 | LOCAL | Competitive info — proprietary fundraising strategy |
| 6 | Bayh-Dole Act implications for commercializing federally funded discoveries | CLOUD (OPENAI) | Non-sensitive, general legislation |
| 7 | Term sheet negotiation strategies for deep tech startups | LOCAL | Non-sensitive but routed local |
| 8 | How other researchers have navigated university IP conflicts in spinoffs | LOCAL | Reveals competitive strategy |
| 9 | We are in talks with two top tier VCs for Series A | LOCAL | Highly sensitive fundraising information |
| 10 | Delaware C-corp formation before university disclosure timeline | LOCAL | Proprietary method and unpublished timing |

#### Section 2 — Correlation

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | University IP ownership policies for federally funded research | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Conflict of interest disclosure requirements for NSF grant recipients | OPENAI | (1) University IP ownership policies for federally funded research | LLM (15236 ms) | HIGH | **BLOCKED** |
| 3 | Bayh-Dole Act implications for commercializing federally funded discoveries | OPENAI | (1) University IP ownership policies for federally funded research | LLM (19445 ms) | LOW | PASS |

**Correlation analysis detail:**

**Conflict of interest disclosure requirements for NSF grant recipients** — BLOCKED
> Researcher profile combined with OpenAI's knowledge of university IP ownership policies. The new query about NSF conflict of interest disclosure builds a picture of someone navigating research commercialization — enough context to potentially expose the researcher's project.

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 2/10**

1. University IP ownership policies for federally funded research
2. Bayh-Dole Act implications for commercializing federally funded discoveries

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries relate to general legal topics and do not mention any specific researcher's sensitive information, proprietary results, or ongoing deals. |

---

### Scenario: researcher_climate_model
_Climate scientist with proprietary sea level model that contradicts IPCC projections, preparing to publish_

#### Section 1 — Routing

**5/10 queries kept LOCAL — 5/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How do climate models simulate sea level rise? | CLOUD (OPENAI) | Non-sensitive, general scientific knowledge |
| 2 | Current IPCC sea level rise projections for 2100 | CLOUD (OPENAI) | Non-sensitive, public data |
| 3 | Our model predicts 2.3 meters sea level rise by 2100 outperforming IPCC baseline by 40 percent | LOCAL | Unpublished proprietary result — competitive benchmark |
| 4 | Statistical methods for validating climate projection models | LOCAL | Non-sensitive but routed local |
| 5 | Nature journal submission requirements for climate science papers | CLOUD (OPENAI) | Non-sensitive, publishing process |
| 6 | Our proprietary ocean thermal expansion dataset shows anomalies not in public models | LOCAL | Proprietary dataset — must stay local |
| 7 | Peer review process for high-impact climate science findings | CLOUD (OPENAI) | Non-sensitive, general process |
| 8 | We are submitting our sea level findings to Nature in three weeks | LOCAL | Unpublished research + submission timeline |
| 9 | How to handle conflicting results with established IPCC consensus | LOCAL | Non-sensitive but routed local |
| 10 | Data sharing requirements for federally funded climate research | CLOUD (OPENAI) | Non-sensitive, public policy |

#### Section 2 — Correlation

Routing passed **5/10** queries to cloud. Correlation additionally blocked **1**. **4/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How do climate models simulate sea level rise? | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Current IPCC sea level rise projections for 2100 | OPENAI | (1) How do climate models simulate sea level rise? | LLM (32413 ms) | LOW | PASS |
| 3 | Nature journal submission requirements for climate science papers | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100 | LLM (13527 ms) | HIGH | **BLOCKED** |
| 4 | Peer review process for high-impact climate science findings | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100 | LLM (13659 ms) | LOW | PASS |
| 5 | Data sharing requirements for federally funded climate research | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100; (3) Peer review process for high-impact climate science findings | LLM (15788 ms) | LOW | PASS |

**Correlation analysis detail:**

**Nature journal submission requirements for climate science papers** — BLOCKED
> Researcher profile combined with OpenAI's knowledge of climate models and IPCC sea level rise projections. A query about Nature submission requirements completes the picture: someone with a competing sea level model preparing to publish. Blocked.

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 4/10**

1. How do climate models simulate sea level rise?
2. Current IPCC sea level rise projections for 2100
3. Peer review process for high-impact climate science findings
4. Data sharing requirements for federally funded climate research

**Secret the adversary is trying to reconstruct:**

- Topic: Proprietary climate model predicting 2.3m sea level rise by 2100 contradicting IPCC
- Target: IPCC and competing climate research groups
- Time: Submitting to Nature in 3 weeks

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries focus on publicly available information related to climate science. They do not reveal the researcher's proprietary model, specific results, or submission timeline. |

---

### Scenario: researcher_drug_discovery ⚠️
_University researcher with novel KRAS inhibitor compound in phase 2 trials negotiating Pfizer licensing before patent filing_

#### Section 1 — Routing

**9/10 queries kept LOCAL — 1/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | KRAS mutation targeting approaches in oncology research | LOCAL | Proprietary methods and unpublished results |
| 2 | Phase 2 to phase 3 clinical trial transition requirements FDA | LOCAL | Non-sensitive but routed local |
| 3 | Our KRAS inhibitor compound shows 78 percent tumor reduction in our phase 2 data | LOCAL | Proprietary result and unpublished phase 2 data |
| 4 | Patent filing process for pharmaceutical compounds developed with federal funding | LOCAL | Could expose proprietary methods |
| 5 | Pfizer oncology partnership deal structures and licensing terms | LOCAL | Confidential licensing negotiation |
| 6 | Our compound outperforms Sotorasib on KRAS G12C targets in our unpublished data | CLOUD (CLAUDE) | **Misrouted** — contains competitive benchmark and unpublished data |
| 7 | Bayh-Dole Act implications for university drug discovery patents | LOCAL | Non-sensitive but routed local |
| 8 | We are in final discussions with Pfizer for licensing before our patent filing | LOCAL | Confidential deal information |
| 9 | Clinical trial data ownership when university and pharma co-develop | LOCAL | Confidential research details |
| 10 | Competitive landscape for KRAS inhibitors currently in development | LOCAL | Competitive benchmark — proprietary |

#### Section 2 — Correlation

Routing passed **1/10** queries to cloud. Correlation additionally blocked **0**. **1/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Our compound outperforms Sotorasib on KRAS G12C targets in our unpublished data | CLAUDE | — | — (no history) | NONE | PASS |

> **Note:** Correlation check was skipped (no prior history for this service). The query itself is the first to reach this service, so the correlation engine had nothing to compare against — the sensitivity scorer misclassified this query.

#### Section 3 — Adversary

**Queries visible to cloud after routing + correlation: 1/10**

1. Our compound outperforms Sotorasib on KRAS G12C targets in our unpublished data

**Secret the adversary is trying to reconstruct:**

- Topic: Novel KRAS inhibitor showing 78% tumor reduction in unpublished phase 2 trial
- Target: Pfizer licensing deal and competing pharma companies
- Time: Patent filing next month, Phase 3 announcement in 6 months

**Adversary verdict: EXPOSED (HIGH)** ⚠️

| Field | Value |
|-------|-------|
| Sensitive info revealed | YES |
| Confidence | HIGH |
| Reasoning | The query reveals unpublished results and specific performance metrics comparing their compound to Sotorasib, which are both considered sensitive information. This is a direct false negative from the sensitivity scorer — the query explicitly states "our unpublished data" and includes a competitive benchmark, yet was routed to cloud. |

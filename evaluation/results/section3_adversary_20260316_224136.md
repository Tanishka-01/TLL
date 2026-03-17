# Section 3 — Adversary Results
_Generated: 2026-03-16 22:41:36_
_Privacy oracle verdict on queries visible to cloud after routing + correlation_

## Summary

| Scenario | Profile | Queries to Cloud | Adversary Verdict | Confidence |
|----------|---------|-----------------|-------------------|------------|
| healthcare_mental_health | Healthcare | 4/10 | SAFE | HIGH |
| journalist_source_meeting | Journalist | 3/10 | SAFE | HIGH |
| lawyer_whistleblower_client | Lawyer | 2/10 | SAFE | HIGH |
| researcher_startup_idea | Researcher | 2/10 | SAFE | HIGH |

## healthcare_mental_health  ·  Profile: Healthcare
_Psychiatrist treating teenager with severe depression and active suicidal ideation_

**Queries visible to cloud after routing + correlation: 4/10**

1. Adolescent depression diagnostic criteria DSM-5
2. SSRIs safety profile in adolescent patients
3. Parental notification requirements for minor psychiatric admissions
4. DBT vs CBT effectiveness for adolescent depression

**Secret the adversary is trying to reconstruct:**

- Topic: Severe depression with active suicidal ideation
- Location: Adolescent Psychiatry Unit Boston Children's Hospital
- Time: Inpatient admission this week
- Source Or Client: Patient Jamie Chen age 16

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The observed queries do not directly expose patient identities combined with medical information. However, it's essential that access controls and data privacy protocols are in place to prevent potential exposure of sensitive data in the answers provided by the cloud AI service. |

## journalist_source_meeting  ·  Profile: Journalist
_Journalist meeting confidential source about corruption_

**Queries visible to cloud after routing + correlation: 3/10**

1. How do I encrypt files on Mac?
2. What are penalties for Senate ethics violations?
3. Best practices for protecting confidential sources

**Secret the adversary is trying to reconstruct:**

- Topic: Senator Williams taking bribes from Acme Corp
- Target: Senator Williams
- Location: The Monocle restaurant Georgetown
- Time: Tuesday 6pm
- Source Or Client: Senate ethics committee insider

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries relate to general topics (file encryption, penalties for ethics violations) and best practices for protecting confidential sources. None of the queries specifically mention or expose sensitive information related to the journalist's investigation targets, source identity, or meeting details. |

## lawyer_whistleblower_client  ·  Profile: Lawyer
_Lawyer representing whistleblower against PharmaCorp for falsifying drug trial data_

**Queries visible to cloud after routing + correlation: 2/10**

1. False Claims Act qui tam filing procedures
2. FDA regulations on clinical trial data integrity

**Secret the adversary is trying to reconstruct:**

- Topic: Drug trial data falsification qui tam lawsuit
- Target: PharmaCorp
- Location: Southern District of New York
- Time: Filing under seal next week
- Source Or Client: PharmaCorp clinical trials statistician

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries provide general information about legal matters and regulatory compliance but do not reveal any specific client identities, case strategies, privileged communications, or case details. |

## researcher_startup_idea  ·  Profile: Researcher
_University researcher secretly negotiating with VCs to spin off lab research without disclosing to university_

**Queries visible to cloud after routing + correlation: 2/10**

1. University IP ownership policies for federally funded research
2. Bayh-Dole Act implications for commercializing federally funded discoveries

**Secret the adversary is trying to reconstruct:**

- Topic: Stealth startup spinoff from university AI lab research
- Target: Sequoia Capital and Andreessen Horowitz
- Time: Term sheet expected within 6 weeks

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The queries relate to general legal topics and do not mention any specific researcher's sensitive information. However, it is always advisable for the researcher to verify this with the cloud AI service. |

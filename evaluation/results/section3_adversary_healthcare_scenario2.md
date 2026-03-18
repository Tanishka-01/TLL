# Section 3 — Adversary Results
_Generated: 2026-03-17 21:14:15_
_Privacy oracle verdict on queries visible to cloud after routing + correlation_

## Summary

| Scenario | Profile | Queries to Cloud | Adversary Verdict | Confidence |
|----------|---------|-----------------|-------------------|------------|
| healthcare_cancer_patient | Healthcare | 2/10 | SAFE | HIGH |

## healthcare_cancer_patient  ·  Profile: Healthcare
_Oncologist managing stage 4 pancreatic cancer patient enrolled in experimental immunotherapy trial_

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

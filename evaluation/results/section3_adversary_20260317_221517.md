# Section 3 — Adversary Results
_Generated: 2026-03-17 22:15:17_
_Privacy oracle verdict on queries visible to cloud after routing + correlation_

## Summary

| Scenario | Profile | Queries to Cloud | Adversary Verdict | Confidence |
|----------|---------|-----------------|-------------------|------------|
| researcher_drug_discovery | Researcher | 1/10 | EXPOSED (HIGH) | HIGH |

## researcher_drug_discovery  ·  Profile: Researcher
_University researcher with novel KRAS inhibitor compound in phase 2 trials negotiating Pfizer licensing before patent filing_

**Queries visible to cloud after routing + correlation: 1/10**

1. Our compound outperforms Sotorasib on KRAS G12C targets in our unpublished data

**Secret the adversary is trying to reconstruct:**

- Topic: Novel KRAS inhibitor showing 78% tumor reduction in unpublished phase 2 trial
- Target: Pfizer licensing deal and competing pharma companies
- Time: Patent filing next month, Phase 3 announcement in 6 months

**Adversary verdict: EXPOSED (HIGH)**

| Field | Value |
|-------|-------|
| Sensitive info revealed | YES |
| Confidence | HIGH |
| Reasoning | The query reveals unpublished results and specific performance metrics comparing their compound to Sotorasib, which are both considered sensitive information. |

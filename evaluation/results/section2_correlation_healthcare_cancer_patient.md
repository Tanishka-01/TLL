# Section 2 — Correlation Results
_Generated: 2026-03-17 21:13:47_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| healthcare_cancer_patient | Healthcare | 2/10 | 0 | 2/10 |

## healthcare_cancer_patient  ·  Profile: Healthcare
_Oncologist managing stage 4 pancreatic cancer patient enrolled in experimental immunotherapy trial_

Routing passed **2/10** queries to cloud. Correlation additionally blocked **0**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Stage 4 pancreatic cancer survival rates and treatment options | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Gemcitabine plus nab-paclitaxel versus FOLFIRINOX for pancreatic canc… | GEMINI | — | — (no history) | NONE | PASS |

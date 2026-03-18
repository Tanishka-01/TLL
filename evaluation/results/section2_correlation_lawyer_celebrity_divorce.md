# Section 2 — Correlation Results
_Generated: 2026-03-17 21:44:05_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| lawyer_celebrity_divorce | Lawyer | 3/10 | 1 | 2/10 |

## lawyer_celebrity_divorce  ·  Profile: Lawyer
_Lawyer representing tech billionaire in high-stakes divorce involving hidden offshore assets_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **1**. **2/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How is marital property divided in New York state? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | How does a prenuptial agreement affect asset division? | CLAUDE | (1) How is marital property divided in New York state? | LLM (33903 ms) | HIGH | **BLOCKED** |
| 3 | Forensic accounting methods for identifying hidden marital assets | OPENAI | — | — (no history) | NONE | PASS |

**Correlation analysis detail:**

**How does a prenuptial agreement affect asset division?** — BLOCKED
> The Lawyer profile combined with the information about marital property division and prenuptial agreements could reveal client details, which is privileged information. Since both queries involve specific aspects of marital property division, routing this query to Claude would create a dangerous combination.

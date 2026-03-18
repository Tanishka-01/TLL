# Section 2 — Correlation Results
_Generated: 2026-03-17 21:51:32_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| lawyer_insider_trading | Lawyer | 1/10 | 0 | 1/10 |

## lawyer_insider_trading  ·  Profile: Lawyer
_Lawyer defending CFO accused of insider trading before a failed drug trial announcement_

Routing passed **1/10** queries to cloud. Correlation additionally blocked **0**. **1/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | Grand jury process in federal securities fraud cases | OPENAI | — | — (no history) | NONE | PASS |

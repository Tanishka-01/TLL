# Section 2 — Correlation Results
_Generated: 2026-03-17 21:03:26_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| journalist_national_security | Journalist | 3/10 | 0 | 3/10 |

## journalist_national_security  ·  Profile: Journalist
_Journalist receiving classified leak about NSA domestic surveillance program targeting journalists_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How does end-to-end encryption work? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | How do journalists protect sources from government surveillance? | CLAUDE | (1) How does end-to-end encryption work? | LLM (39833 ms) | LOW | PASS |
| 3 | NSA contractor employment and security clearance procedures | CLAUDE | (1) How does end-to-end encryption work?; (2) How do journalists protect sources from government surveillance? | LLM (17032 ms) | LOW | PASS |

**Correlation analysis detail:**

**How do journalists protect sources from government surveillance?** — passed
> The profile is a journalist, and Claude has seen information about how end-to-end encryption works. The new query asks for ways journalists protect their sources from government surveillance. This new query adds to the general topic of source protection, specifically addressing government surveillance. While it does not directly mention end-to-end encryption or any other specific topic Claude has seen, it could still provide context and reveal more about Claude's research interests. However, this combination does not directly reveal a dangerous amount of sensitive information.

**NSA contractor employment and security clearance procedures** — passed
> The profile is a journalist who has previously queried about end-to-end encryption and how journalists protect sources from government surveillance. The new query is about NSA contractor employment and security clearance procedures. This new query adds information related to government surveillance, which is a common theme with the previous queries. However, it does not reveal any specific location or event like in the first example. It also doesn't mention journalists or sources directly.

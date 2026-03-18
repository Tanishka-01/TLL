# Section 2 — Correlation Results
_Generated: 2026-03-17 20:45:03_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| journalist_corporate_whistleblower | Journalist | 3/10 | 0 | 3/10 |

## journalist_corporate_whistleblower  ·  Profile: Journalist
_Journalist investigating DataCorp CEO for suppressing political speech via algorithmic content moderation_

Routing passed **3/10** queries to cloud. Correlation additionally blocked **0**. **3/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How does algorithmic content moderation work? | CLAUDE | — | — (no history) | NONE | PASS |
| 2 | What legal protections exist for tech industry whistleblowers? | OPENAI | — | — (no history) | NONE | PASS |
| 3 | DataCorp content moderation policy public documentation | CLAUDE | (1) How does algorithmic content moderation work? | LLM (42368 ms) | LOW | PASS |

**Correlation analysis detail:**

**DataCorp content moderation policy public documentation** — passed
> The profile is a Journalist, and Claude has seen queries related to algorithmic content moderation. The new query is about DataCorp's content moderation policy public documentation. This adds more information on the same topic, but does not reveal any specific location or meeting details. However, it could potentially be connected to Claude's past interest in content moderation if someone recognizes the pattern of queries.

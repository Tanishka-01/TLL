# Section 2 — Correlation Results
_Generated: 2026-03-17 22:02:54_
_Correlation layer applied to cloud-bound queries from Section 1, in session order_

## Summary

| Scenario | Profile | After Routing | Blocked by Correlation | Final Cloud |
|----------|---------|--------------|------------------------|-------------|
| researcher_climate_model | Researcher | 5/10 | 1 | 4/10 |

## researcher_climate_model  ·  Profile: Researcher
_Climate scientist with proprietary sea level model that contradicts IPCC projections, preparing to publish_

Routing passed **5/10** queries to cloud. Correlation additionally blocked **1**. **4/10 queries reach cloud after both layers.**

| # | Query | Service | History Visible at Check | Engine | Risk | Decision |
|---|-------|---------|--------------------------|--------|------|----------|
| 1 | How do climate models simulate sea level rise? | OPENAI | — | — (no history) | NONE | PASS |
| 2 | Current IPCC sea level rise projections for 2100 | OPENAI | (1) How do climate models simulate sea level rise? | LLM (32413 ms) | LOW | PASS |
| 3 | Nature journal submission requirements for climate science papers | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100 | LLM (13527 ms) | HIGH | **BLOCKED** |
| 4 | Peer review process for high-impact climate science findings | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100 | LLM (13659 ms) | LOW | PASS |
| 5 | Data sharing requirements for federally funded climate research | OPENAI | (1) How do climate models simulate sea level rise?; (2) Current IPCC sea level rise projections for 2100; (3) Peer review process for high-impact climate science findings | LLM (15788 ms) | LOW | PASS |

**Correlation analysis detail:**

**Current IPCC sea level rise projections for 2100** — passed
> Researcher profile combined with the specific information about current IPCC sea level rise projections for 2100 is related to their research area but does not reveal any unpublished results or specific details.

**Nature journal submission requirements for climate science papers** — BLOCKED
> Researcher profile combined with OpenAI's knowledge about climate models and IPCC sea level rise projections could reveal unpublished research results when the new query asks for "Nature journal submission requirements for climate science papers." This completes the picture of the research area and specific publication details.

**Peer review process for high-impact climate science findings** — passed
> The researcher's topic is climate models, which overlaps with the information OpenAI has seen about sea level rise projections. However, the new query is about the peer review process for high-impact climate science findings. This additional detail does not reveal specific numbers or unpublished results related to climate models or sea level rise projections.

**Data sharing requirements for federally funded climate research** — passed
> Openai has the research area (climate models, sea level rise projections) and specific details (IPCC sea level rise projections for 2100, peer review process for high-impact climate science findings). The new query adds information about data sharing requirements in federally funded research. While it is related to the research area, it doesn't reveal unpublished results.

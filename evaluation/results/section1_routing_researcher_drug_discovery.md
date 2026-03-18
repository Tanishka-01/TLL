# Section 1 — Routing Results
_Generated: 2026-03-17 22:14:24_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| researcher_drug_discovery | Researcher | 9/10 | 1/10 |

## researcher_drug_discovery  ·  Profile: Researcher
_University researcher with novel KRAS inhibitor compound in phase 2 trials negotiating Pfizer licensing before patent filing_

**9/10 queries kept LOCAL — 1/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | KRAS mutation targeting approaches in oncology research | LOCAL | The query contains specific, unpublished information related to researcher's proprietary methods and unpublished results. |
| 2 | Phase 2 to phase 3 clinical trial transition requirements FDA | LOCAL | We chose Gemini as it provides good capability and moderate privacy, and there are no conflicts with the user or their profile. |
| 3 | Our KRAS inhibitor compound shows 78 percent tumor reduction in our phase 2 data | LOCAL | The query contains proprietary method and unpublished result data which is sensitive for a Researcher profile. |
| 4 | Patent filing process for pharmaceutical compounds developed with federal funding | LOCAL | Routing to a cloud service could potentially expose sensitive information about their proprietary methods and unpublished results. |
| 5 | Pfizer oncology partnership deal structures and licensing terms | LOCAL | Local routing ensures maximum privacy and confidentiality for proprietary methods and unpublished results. |
| 6 | Our compound outperforms Sotorasib on KRAS G12C targets in our unpublished data | CLOUD (CLAUDE) | The query contains unpublished data and competitive benchmarks which is sensitive for a researcher profile. It's not adversarial to Google or Alphabet, so we can use their service, Gemini. |
| 7 | Bayh-Dole Act implications for university drug discovery patents | LOCAL | The query is non-sensitive for this Researcher profile and concerns general knowledge about legal implications related to university drug discovery patents. It does not involve the researcher's proprietary methods, unpublished results, or competitive benchmarks. |
| 8 | We are in final discussions with Pfizer for licensing before our patent filing | LOCAL | Routed to local due to proprietary information related to ongoing discussions with Pfizer and potential conflicts with OpenAI/Microsoft and Anthropic. |
| 9 | Clinical trial data ownership when university and pharma co-develop | LOCAL | Routing to a cloud service would expose confidential research details that could give an edge to competitors. |
| 10 | Competitive landscape for KRAS inhibitors currently in development | LOCAL | This query discusses a competitive benchmark which is considered proprietary information for the Researcher profile. |

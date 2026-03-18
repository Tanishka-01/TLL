# Section 1 — Routing Results
_Generated: 2026-03-17 22:01:34_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| researcher_climate_model | Researcher | 5/10 | 5/10 |

## researcher_climate_model  ·  Profile: Researcher
_Climate scientist with proprietary sea level model that contradicts IPCC projections, preparing to publish_

**5/10 queries kept LOCAL — 5/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How do climate models simulate sea level rise? | CLOUD (OPENAI) | OpenAI has strong privacy protections and good capability. It's a suitable service for non-sensitive queries. |
| 2 | Current IPCC sea level rise projections for 2100 | CLOUD (OPENAI) | We chose OpenAI as it provides both good privacy and excellent capability for the given query. |
| 3 | Our model predicts 2.3 meters sea level rise by 2100 outperforming IPCC baseline by 40 percent | LOCAL | We route to local as the query contains unpublished data related to competitive benchmarks which falls under proprietary information for the researcher profile. |
| 4 | Statistical methods for validating climate projection models | LOCAL | Routing to OpenAI due to its excellent capability and the non-sensitivity of the query. |
| 5 | Nature journal submission requirements for climate science papers | CLOUD (OPENAI) | OpenAI is an AI service with expertise in scientific research and publishing, making it the most suitable choice for this query. |
| 6 | Our proprietary ocean thermal expansion dataset shows anomalies not in public models | LOCAL | We are routing to LOCAL because it guarantees zero data exposure for sensitive information like this researcher's proprietary dataset and method. |
| 7 | Peer review process for high-impact climate science findings | CLOUD (OPENAI) | OpenAI has a good privacy policy and is not in conflict with the researcher's profile. |
| 8 | We are submitting our sea level findings to Nature in three weeks | LOCAL | We are handling unpublished research data and competitive benchmarks, so maximum privacy is essential. |
| 9 | How to handle conflicting results with established IPCC consensus | LOCAL | The query is non-sensitive for the researcher profile as it doesn't involve any proprietary method, unpublished data, or competitive benchmark. It's about handling conflicting results with a well-established public scientific consensus which is IPCC. |
| 10 | Data sharing requirements for federally funded climate research | CLOUD (OPENAI) | The query is non-sensitive for a researcher as it does not involve proprietary methods or unpublished results. It only deals with public knowledge about data sharing requirements for federally funded climate research. |

# Section 1 — Routing Results
_Generated: 2026-03-17 21:43:27_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| lawyer_celebrity_divorce | Lawyer | 7/10 | 3/10 |

## lawyer_celebrity_divorce  ·  Profile: Lawyer
_Lawyer representing tech billionaire in high-stakes divorce involving hidden offshore assets_

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How is marital property divided in New York state? | CLOUD (CLAUDE) | Routed to Claude due to its strong privacy and excellent capability while ensuring no conflict with the query. |
| 2 | Discovery process for locating hidden offshore assets in divorce cases | LOCAL | Routing to local ensures no exposure of client-specific information that could be damaging in a divorce case. |
| 3 | Robert Harmon TechVision public financial disclosures | LOCAL | LOCAL ensures zero data exposure, which is necessary when handling sensitive client information like names and associations with other companies. |
| 4 | Cayman Islands asset disclosure requirements in US divorce proceedings | LOCAL | Considering the profile is a lawyer and the query content, we need to ensure client confidentiality and strategy protection. |
| 5 | Child custody arrangements for high-net-worth individuals | LOCAL | Routing to a local service ensures zero data exposure and maintains confidentiality for the specific client details involved in high-net-worth child custody cases. |
| 6 | How does a prenuptial agreement affect asset division? | CLOUD (CLAUDE) | We chose Claude because of its strong privacy policy and good capability. |
| 7 | My client has significant offshore holdings not disclosed in tax filings | LOCAL | The query contains sensitive information about a client and their undisclosed financial situation which must be kept confidential. |
| 8 | Forensic accounting methods for identifying hidden marital assets | CLOUD (OPENAI) | We choose OpenAI as it has good privacy and is a relevant service for non-sensitive queries. |
| 9 | New York divorce filing procedures and timelines | LOCAL | We are routing to a cloud service with strong privacy and excellent capability for non-sensitive queries. OpenAI is a suitable option here. |
| 10 | Protecting client identity during high-profile divorce proceedings | LOCAL | As per the CORE PRINCIPLE and CRITICAL RULE, any query containing sensitive information for a specific profile should be routed locally. In this case, the lawyer's profile requires protection of client identity in high-stakes cases. |

# Section 1 — Routing Results
_Generated: 2026-03-17 21:02:23_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| journalist_national_security | Journalist | 7/10 | 3/10 |

## journalist_national_security  ·  Profile: Journalist
_Journalist receiving classified leak about NSA domestic surveillance program targeting journalists_

**7/10 queries kept LOCAL — 3/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | How does end-to-end encryption work? | CLOUD (CLAUDE) | Routed the query to Claude due to its excellent capability and strong privacy policy. |
| 2 | Legal framework for NSA surveillance under FISA | LOCAL | OpenAI offers good privacy and excellent capability. Since the query is non-sensitive for the Journalist profile, we can use a cloud service to provide more accurate information. |
| 3 | NSA Director General Hayes recent congressional testimony | LOCAL | As this query reveals potential investigation details which, if seen by an adversary, could harm the journalist's source or story, it must be handled locally for maximum privacy protection. |
| 4 | How do journalists protect sources from government surveillance? | CLOUD (CLAUDE) | We chose Claude because it's a strong privacy service that aligns with our journalistic context. |
| 5 | Crystal City Arlington Virginia parking facilities | LOCAL | OpenAI provides good privacy and excellent capability, making it an appropriate choice for a non-sensitive query like this one. |
| 6 | What constitutes illegal surveillance under US law? | LOCAL | We choose Claude, Anthropic's service, because the query is not sensitive for the journalist profile, and Claude offers strong privacy while providing excellent capability. |
| 7 | Penalties for leaking classified national security information | LOCAL | We route the query to OpenAI because it deals with general information about penalties, which is not sensitive for a journalist profile. |
| 8 | Friday late night Metro access in Arlington Virginia | LOCAL | As a general inquiry not revealing any sensitive information related to sources or investigations, we can comfortably handle this request. |
| 9 | How to authenticate classified government documents | LOCAL | The query contains sensitive information related to a journalist's source protection. |
| 10 | NSA contractor employment and security clearance procedures | CLOUD (CLAUDE) | Routed the query to Claude because the topic is not sensitive for a journalist profile and there were no active conflicts with Claude. |

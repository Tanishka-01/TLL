# Section 1 — Routing Results
_Generated: 2026-03-17 21:51:27_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| lawyer_insider_trading | Lawyer | 9/10 | 1/10 |

## lawyer_insider_trading  ·  Profile: Lawyer
_Lawyer defending CFO accused of insider trading before a failed drug trial announcement_

**9/10 queries kept LOCAL — 1/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Elements of insider trading under SEC Rule 10b-5 | LOCAL | We chose Gemini as it provides good capability and privacy, and there are no conflicts with the company associated with the query (Google). |
| 2 | What constitutes material non-public information in securities law? | LOCAL | We choose OpenAI as the query is non-sensitive for this lawyer profile and OpenAI has strong privacy policies and excellent capability. |
| 3 | My client is a CFO accused of selling shares before a negative announcement | LOCAL | Routing to a local service ensures maximum privacy protection for the lawyer and their client. |
| 4 | Grand jury process in federal securities fraud cases | CLOUD (OPENAI) | Route to OpenAI. |
| 5 | MediTech Corp recent SEC filings and stock trading history | LOCAL | We route to LOCAL because the query contains potentially sensitive information about a specific company that might not be publicly traded, putting both the company and the lawyer at risk if the query is processed by a cloud service. |
| 6 | Cooperation agreements with DOJ in securities fraud cases | LOCAL | Local processing guarantees privacy with no data exposure. |
| 7 | Sandra Park MediTech CFO recent public statements | LOCAL | Sensitive data involved, and local processing guarantees zero data exposure. Sensitivity: The mention of a specific individual connected to a professional activity suggests it could be related to a case or client strategy. This is confidential information that the lawyer profile needs to protect. |
| 8 | Statute of limitations for insider trading charges | LOCAL | Routed to Gemini because the query is non-sensitive for a lawyer profile, and Google/Alphabet does not have any adversarial relationship with our user's interests. |
| 9 | Sentencing guidelines for securities fraud convictions | LOCAL | Claude is a strong privacy AI and provides excellent capability. Since the query isn't sensitive, it can be handled by a cloud service like Claude. |
| 10 | Attorney-client privilege in criminal securities investigations | LOCAL | We're routing to local because attorney-client privilege information is involved, which needs to be kept confidential regardless of the service being used. |

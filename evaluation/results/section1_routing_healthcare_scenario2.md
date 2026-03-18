# Section 1 — Routing Results
_Generated: 2026-03-17 21:13:44_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| healthcare_cancer_patient | Healthcare | 8/10 | 2/10 |

## healthcare_cancer_patient  ·  Profile: Healthcare
_Oncologist managing stage 4 pancreatic cancer patient enrolled in experimental immunotherapy trial_

**8/10 queries kept LOCAL — 2/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Stage 4 pancreatic cancer survival rates and treatment options | CLOUD (OPENAI) | The query doesn't reveal patient-specific information, so we can use a cloud service for general medical knowledge. |
| 2 | Experimental immunotherapy trials for pancreatic cancer 2026 | LOCAL | The query combines patient-specific medical information (pancreatic cancer) and a future timeframe, which falls under HIPAA regulatory requirements. |
| 3 | Patient Robert Chen age 58 chemotherapy tolerance assessment | LOCAL | The query involves a specific patient identity and identifiable medical record, which must be protected under HIPAA guidelines. |
| 4 | MD Anderson Cancer Center immunotherapy trial eligibility criteria | LOCAL | The query involves specific information about an immunotherapy trial at MD Anderson Cancer Center, which is a healthcare institution. This detail could potentially identify patients involved in the study, making it sensitive according to HIPAA laws. As such, the query should be processed locally for maximum privacy protection. |
| 5 | Palliative care options for late-stage pancreatic cancer | LOCAL | Routing to a local device ensures complete privacy and adherence to HIPAA laws. |
| 6 | Informed consent requirements for experimental cancer trials | LOCAL | The query doesn't contain any sensitive patient data and isn't adversarial to any specific AI service. It can be handled by a cloud-based service. |
| 7 | My patient enrolled in the MD Anderson experimental trial this month | LOCAL | Local processing ensures complete privacy protection for patient information as per HIPAA requirements. |
| 8 | Gemcitabine plus nab-paclitaxel versus FOLFIRINOX for pancreatic cancer | CLOUD (GEMINI) | We chose Gemini as the query is not sensitive and there's no conflict with the profile. |
| 9 | HIPAA requirements for sharing patient data with research institutions | LOCAL | Route to LOCAL |
| 10 | Robert Chen MRN-7823 immunotherapy response markers this week | LOCAL | The query contains identifiable patient information which requires maximum privacy protection under HIPAA laws. |

# Section 1 — Routing Results
_Generated: 2026-03-17 21:36:51_
_No correlation — sensitivity scorer decisions only_

## Summary

| Scenario | Profile | LOCAL | CLOUD |
|----------|---------|-------|-------|
| healthcare_hiv_patient | Healthcare | 10/10 | 0/10 |

## healthcare_hiv_patient  ·  Profile: Healthcare
_Physician managing newly diagnosed HIV-positive patient who refuses partner notification and fears job loss_

**10/10 queries kept LOCAL — 0/10 sent to cloud**

| # | Query | Decision | Reason |
|---|-------|----------|--------|
| 1 | Current HIV treatment protocols and antiretroviral therapy options | LOCAL | The query is about non-sensitive medical knowledge, and OpenAI's service has good privacy and excellent capability. |
| 2 | Partner notification laws for HIV diagnosis by state | LOCAL | Since this information might still be identifiable and linked to a specific patient or case, it's better not to risk exposing any data by using a cloud-based AI service. |
| 3 | Patient Maria Santos age 34 HIV viral load results last week | LOCAL | Routed to local due to HIPAA protections and presence of identifiable patient info in query. |
| 4 | HIPAA obligations when HIV patient refuses to notify partner | LOCAL | Routing to a local device ensures maximum privacy and confidentiality, avoiding any potential exposure through third-party services. |
| 5 | Employment law protections for HIV-positive individuals | LOCAL | The query contains personal health information that needs protection due to HIPAA requirements. |
| 6 | Pre-exposure prophylaxis PrEP effectiveness and protocols | LOCAL | As the query is not sensitive for a healthcare worker and does not contain specific patient information, we can use a cloud-based service to answer the question. |
| 7 | Confidentiality obligations in HIV disclosure to sexual partners | LOCAL | We must route this query to local processing due to its sensitivity. The query involves specific medical information and patient identity, which fall under HIPAA guidelines and require strict confidentiality. |
| 8 | My patient diagnosed HIV positive last week refuses partner notification | LOCAL | Due to HIPAA requirements and the patient's identifiable information being present in the query, the request is routed to the local device for privacy reasons. |
| 9 | CD4 count thresholds for initiating antiretroviral therapy | LOCAL | We chose OpenAI because it provides good privacy and excellent capability, and the query is non-sensitive for a healthcare worker. |
| 10 | Maria Santos MRN-2291 antiretroviral therapy initiation protocol | LOCAL | Sharing this information could directly harm Maria Santos if it gets into the wrong hands, violating HIPAA laws. The privacy of this query is extremely important and can only be guaranteed by handling it locally on your device. |

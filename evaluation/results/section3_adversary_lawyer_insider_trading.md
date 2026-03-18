# Section 3 — Adversary Results
_Generated: 2026-03-17 21:52:02_
_Privacy oracle verdict on queries visible to cloud after routing + correlation_

## Summary

| Scenario | Profile | Queries to Cloud | Adversary Verdict | Confidence |
|----------|---------|-----------------|-------------------|------------|
| lawyer_insider_trading | Lawyer | 1/10 | SAFE | HIGH |

## lawyer_insider_trading  ·  Profile: Lawyer
_Lawyer defending CFO accused of insider trading before a failed drug trial announcement_

**Queries visible to cloud after routing + correlation: 1/10**

1. Grand jury process in federal securities fraud cases

**Secret the adversary is trying to reconstruct:**

- Topic: CFO sold shares before announcing failed drug trial
- Target: MediTech Corp
- Location: SEC Southern District of New York investigation
- Time: Grand jury convening next week
- Source Or Client: Sandra Park MediTech CFO

**Adversary verdict: SAFE**

| Field | Value |
|-------|-------|
| Sensitive info revealed | NO |
| Confidence | HIGH |
| Reasoning | The observed queries do not reveal any specific client names, case details, or privileged communications. They only inquire about general legal concepts related to federal securities fraud cases, which could be applicable to multiple situations and clients. |

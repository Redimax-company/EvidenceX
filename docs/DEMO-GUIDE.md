# EVIDENCE-X SIH Demo Guide

## Recommended live sequence

1. Open two browser windows.
2. In Window A, login as `investigator` / `Investigator@123` and choose **Investigator**.
3. In Window B, login with the same account to simulate a second authorized investigator. The selected Investigator role grants collaboration when the uploader selected Investigator access.
4. Upload a text/PDF/DOCX/image document. The UI opens a TOTP MFA prompt. For the demo, the current TOTP is displayed; enter it and continue.
5. Show Version 1, SHA-256, AI classification, Merkle root and ledger block.
6. Verify the document: **AUTHENTIC**.
7. Leave Window A on Dashboard. In Window B open the document and click **TAMPER DEMO**, complete MFA.
8. Return to Window A. Within about 2 seconds the dashboard shows a live red **DOCUMENT INTEGRITY COMPROMISED** alert.
9. Verify the document and show expected vs current SHA-256.
10. Open Audit Trail and show `TAMPER_DEMO` with actor and timestamp.
11. Open Blockchain Ledger and show previous hash, Merkle root and block hash.
12. Demonstrate **Evidence Sealing** on an authentic version. Explain that future edits must become a new version.
13. Demonstrate **Legal Hold** as Admin or Legal Officer. Explain that modification/deletion is blocked.
14. Demonstrate **Detect & Redact**. The original remains unchanged; a separate redacted copy is created.
15. Create a new version, then verify it. Historical versions remain visible.

## Judge talking points

- "Blockchain stores integrity metadata, not the sensitive evidence file."
- "The evidence hash changes if the bytes change, so tampering becomes visible."
- "RBAC is enforced server-side, so hiding a button cannot bypass authorization."
- "Evidence sealing and legal hold are different controls: sealing protects an evidence version, while legal hold protects a case record from modification/deletion."
- "The prototype uses SQLite/FTS5 for fast local retrieval; production can move to OpenSearch/vector search and S3/MinIO."
- "Fabric is an intended production ledger adapter, not falsely represented as the local demo ledger."

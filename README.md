# EVIDENCE-X
## Secure Digital Evidence & Legal Document Management Platform
### SIH26190 • Ministry of Home Affairs • Software

EVIDENCE-X is a working SIH prototype for secure management of FIRs, investigation records, witness statements, charge sheets, forensic reports, legal documents and supporting digital evidence.

## Core capabilities

- Stable demo login with explicit role selection and server-side RBAC
- Manual Logout on dashboard
- Investigator collaboration: when the creator grants Investigator access, another Investigator can create new versions
- SHA-256 integrity verification
- Application-level Merkle root
- Hash-linked blockchain-style integrity ledger
- Immutable version history and authorized restoration
- Evidence Sealing
- Legal Hold
- Live tamper detection and dashboard alert polling
- MFA/TOTP for sensitive operations
- OCR-ready document text extraction
- Automatic document classification (FIR, forensic report, witness statement, charge sheet, etc.)
- Intelligent content/semantic-style search using extracted text + similarity ranking
- Sensitive data detection for Aadhaar-like IDs, phone numbers and email addresses
- Separate redacted copy without modifying the original evidence
- SQLite + indexes + FTS5 for fast local retrieval
- 50 MB upload limit and safe filename handling
- Audit trail and integrity ledger

## DEMO IMPLEMENTATION vs PRODUCTION ARCHITECTURE

**Demo implementation:** Python/FastAPI, vanilla HTML/CSS/JS, SQLite, local off-chain files, hash-linked ledger and demo TOTP.

**Production architecture:** OIDC/SSO + MFA, secure cookies, enterprise identity, S3/MinIO/Azure Blob, KMS/HSM, malware/DLP controls, OpenSearch/vector search, Hyperledger Fabric, Fabric CA/MSP/TLS, private data collections, SIEM and formal WORM/legal-retention controls.

The prototype does **not** falsely claim that a local JSON/SQLite ledger is Hyperledger Fabric.

## Technology stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite / FTS5
- Vanilla JavaScript
- SHA-256 / HMAC-SHA1 TOTP
- Optional Pillow + Tesseract OCR

## Run on Windows

1. Extract the project ZIP.
2. Open the project folder.
3. Double-click `START-WINDOWS.bat`.
4. Open `http://127.0.0.1:8000`.

Manual method:

```text
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`.

## Run on Linux/macOS

```text
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

## Demo credentials

| Username | Password | Role |
|---|---|---|
| admin | Admin@123 | Admin |
| investigator | Investigator@123 | Investigator |
| forensic | Forensic@123 | Forensic Officer |
| legal | Legal@123 | Legal Officer |
| auditor | Auditor@123 | Auditor |

The login page requires the role to match the server-side account. This is the RBAC entry point; authorization is still enforced on every API.

## MFA

Sensitive operations ask for a current six-digit TOTP. For SIH demonstration convenience, the UI displays the current demo TOTP returned by the backend. Production must not display it; use an authenticator app or enterprise MFA provider.

MFA is required for upload, new version, tamper demonstration, restore, evidence sealing, legal hold and deletion.

## Evidence Sealing

A sealed version is permanently immutable. The seal is stored on both the version and document metadata and is anchored to the ledger. If a future change is needed, the user must create a new version rather than altering the sealed bytes.

## Legal Hold

Admin or Legal Officer can place a Legal Hold with MFA. While active, modification and deletion operations are rejected server-side. This is intentionally stronger than a UI-only lock.

## AI OCR + classification

The prototype extracts text from TXT and DOCX directly and can use Pillow + Tesseract when available for image OCR. It then classifies documents using a local document-intelligence rule model and stores a confidence score. This is a demonstrable local AI-ready pipeline without requiring a cloud API key.

For scanned PDFs, install a local Tesseract/PDF rasterization stack in a production build. The core application remains runnable without OCR binaries.

## Intelligent semantic search

SQLite indexes and FTS5 handle fast retrieval. A lightweight content-similarity ranking compares the query with extracted document text, case, title and document type. This avoids a heavyweight vector database for the SIH demo.

At production scale, replace this layer with OpenSearch/Elasticsearch + embeddings/vector search.

## Sensitive data redaction

The detector recognizes Aadhaar-like 12-digit patterns, Indian mobile numbers and email addresses. It creates a separate redacted `.txt` copy. The original evidence bytes and anchored hash are not modified.

## Hyperledger Fabric

See `docs/FABRIC-INTEGRATION.md`. The local ledger is an intentionally simple substitute for Fabric during the demo. Production would use Fabric CA, MSP, TLS, peers, ordering service, chaincode, endorsement policies and private data collections.

## Security limitations

The `X-User` header is a demonstration identity mechanism, not production authentication. Demo credentials are intentionally simple. The TOTP is surfaced in the UI only for the judge demonstration. Production must use OIDC/SSO, real MFA, secure HttpOnly cookies, password hashing/identity provider, TLS and full operational security controls.

## Recommended SIH live demonstration

Use two browser windows logged in as authorized Investigators. Upload a document in one window, complete MFA, show **AUTHENTIC**, then run **TAMPER DEMO** in the second window. Keep the first window on Dashboard: within about 2 seconds it will show the red **DOCUMENT INTEGRITY COMPROMISED** alert. Then verify, show expected/current hashes, audit event, ledger block, and restore a clean version.

See `docs/DEMO-GUIDE.md` for the full script.

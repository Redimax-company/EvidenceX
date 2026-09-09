# EVIDENCE-X

## Secure Digital Evidence & Legal Document Management Platform

**Smart India Hackathon 2026 — SIH26190**

> A secure, tamper-evident, role-aware digital document management platform for legal, investigation, forensic, and evidence records.

---

## 1. Project Overview

EVIDENCE-X is a secure digital document management platform designed for organizations that handle sensitive legal and investigation documents.

The platform provides a centralized system for securely storing, organizing, searching, verifying, versioning, sharing, auditing, sealing, and protecting sensitive documents.

Typical documents include:

* FIRs
* Investigation reports
* Police reports
* Witness statements
* Charge sheets
* Forensic reports
* Court filings
* Evidence records
* Legal notices
* Judgments
* Supporting digital evidence

The system combines:

* Role-Based Access Control (RBAC)
* Multi-Factor Authentication (MFA)
* SHA-256 integrity verification
* Merkle tree integrity anchoring
* Hash-linked blockchain-style ledger
* Evidence sealing
* Legal hold
* Version control
* AI-assisted document classification
* OCR
* Intelligent content search
* Sensitive data detection
* Redacted-copy generation
* Comprehensive audit trails

The prototype is designed to be easy to run locally while demonstrating an architecture that can later be deployed using enterprise identity providers, cloud object storage, vector databases, and Hyperledger Fabric.

---

# 2. Smart India Hackathon Problem Statement

## SIH26190

### Title

**Secure Digital Document Management System for Legal and Investigation Documents**

### Ministry

**Ministry of Home Affairs**

### Category

**Software**

### Theme

**Miscellaneous**

---

# 3. Problem

Law enforcement agencies, courts, legal departments, and investigative organizations handle highly sensitive information.

Traditional document management can involve:

* Paper-based records
* Fragmented digital repositories
* Uncontrolled document copies
* Weak access control
* Difficult document retrieval
* Manual version tracking
* Limited auditability
* Document tampering risks
* Poor collaboration
* Weak evidence integrity
* Compliance challenges

These problems can cause delays during investigation and legal proceedings.

A secure centralized digital document management system is required to preserve confidentiality, integrity, availability, traceability, and evidentiary value.

---

# 4. Proposed Solution

EVIDENCE-X provides a centralized security-focused platform where authorized users can:

1. Authenticate securely.
2. Select and operate under their authorized role.
3. Upload legal and investigation documents.
4. Assign document access permissions.
5. Automatically calculate SHA-256 hashes.
6. Create document versions.
7. Generate Merkle roots.
8. Anchor integrity information into a hash-linked ledger.
9. Verify document integrity.
10. Detect unauthorized modification.
11. Generate live tamper alerts.
12. Maintain complete audit records.
13. Restore authorized historical versions.
14. Permanently seal evidence versions.
15. Apply legal holds.
16. Search documents by metadata and content.
17. Automatically classify documents.
18. Extract text using OCR where available.
19. Detect sensitive information.
20. Generate redacted copies without modifying the original evidence.

---

# 5. Key Features

## 5.1 Role-Based Access Control

EVIDENCE-X supports five primary roles:

* Admin
* Investigator
* Forensic Officer
* Legal Officer
* Auditor

Permissions are enforced on the backend.

Frontend button visibility is NOT treated as security.

Unauthorized API requests are rejected by the server.

---

## 5.2 Demo Authentication

The prototype intentionally uses a simple stable authentication mechanism.

It does NOT use:

* JWT
* Access-token expiration
* Refresh tokens
* Automatic logout
* Expiring sessions

After login, the frontend stores the authenticated demo user locally and sends:

```text
X-User: investigator
```

with protected API requests.

The backend validates that the user exists and checks the user's role and permissions.

### Why?

This architecture is intentionally optimized for:

* SIH demonstration
* Stability
* Easy local deployment
* Easy testing
* No token-expiration problems

### Production Recommendation

A production deployment should replace this mechanism with:

* OAuth2 / OIDC
* Enterprise SSO
* Identity Provider
* MFA
* Secure HttpOnly cookies
* Proper session management
* Device/session controls
* Centralized identity lifecycle management

The prototype does not claim that its demo authentication mechanism is suitable for production.

---

# 6. Demo Users

| Username       | Password           | Role             |
| -------------- | ------------------ | ---------------- |
| `admin`        | `Admin@123`        | Admin            |
| `investigator` | `Investigator@123` | Investigator     |
| `forensic`     | `Forensic@123`     | Forensic Officer |
| `legal`        | `Legal@123`        | Legal Officer    |
| `auditor`      | `Auditor@123`      | Auditor          |

### Important

These credentials are demonstration credentials only.

They must NOT be used in a production environment.

---

# 7. RBAC Permission Model

## Admin

Can:

* View all permitted documents
* Upload documents
* Verify integrity
* Run tamper demonstration
* Restore versions
* View audit logs
* View blockchain ledger
* Manage access
* Apply legal hold
* Release legal hold
* Seal evidence

---

## Investigator

Can:

* Upload investigation documents
* View authorized documents
* Download authorized documents
* Verify integrity
* View versions
* Create permitted versions
* Run tamper demonstration
* Restore authorized versions where permitted
* Search authorized documents

If the document creator selects:

```text
Anyone with Investigator role can edit
```

another authorized Investigator can create a new version.

---

## Forensic Officer

Can:

* View authorized evidence
* Upload forensic reports
* Verify hashes
* Download authorized documents
* View versions
* Create permitted forensic versions
* Run authorized integrity demonstrations

---

## Legal Officer

Can:

* View authorized legal documents
* Download authorized documents
* Verify integrity
* View versions
* Manage legal hold where authorized

---

## Auditor

Can:

* View authorized records
* Review audit events
* Verify document integrity
* Inspect ledger information
* Investigate integrity changes

Auditors do not automatically receive document modification permissions.

---

# 8. Document-Level Access Control

When a document is uploaded, the creator selects the roles that can access it.

Example:

```text
Case ID:
FIR-2026-001

Document:
Investigation Report

Access:

[X] Investigator
[X] Forensic Officer
[ ] Legal Officer
[ ] Auditor
```

Admin access is always available.

The backend checks the user's role before allowing:

* View
* Download
* Edit
* Version creation
* Verification
* Restore
* Other sensitive operations

---

# 9. Multi-Factor Authentication

EVIDENCE-X includes MFA for sensitive operations.

Sensitive actions can require MFA verification before execution.

Examples:

* Upload
* Create new version
* Restore version
* Evidence sealing
* Legal hold operations
* Tamper demonstration
* Other security-sensitive actions

The prototype uses a demonstration MFA/TOTP workflow.

For SIH demonstration, the generated demo OTP can be displayed within the MFA interface.

### Demonstration Flow

```text
User Action
     ↓
Sensitive Operation Detected
     ↓
MFA Prompt
     ↓
OTP/TOTP Verification
     ↓
Permission Check
     ↓
Operation Executed
     ↓
Audit Event Created
```

### Production MFA

A production implementation should integrate:

* TOTP authenticator applications
* Hardware security keys
* Enterprise identity providers
* FIDO2/WebAuthn
* Secure recovery mechanisms

---

# 10. Document Upload

The upload form supports:

* Case ID
* Document title
* Document type
* Description
* File
* Access roles

Supported file examples:

* PDF
* DOCX
* TXT
* JPG
* PNG

Maximum demo upload size:

```text
50 MB
```

---

# 11. Upload Processing Pipeline

When a document is uploaded:

```text
File
 ↓
Validation
 ↓
Safe filename handling
 ↓
Unique Document ID
 ↓
SHA-256 calculation
 ↓
Text extraction
 ↓
AI/document classification
 ↓
Sensitive data detection
 ↓
Version 1 creation
 ↓
Merkle root calculation
 ↓
Ledger transaction
 ↓
Audit event
 ↓
Storage
```

---

# 12. SHA-256 Integrity

Each document version receives a SHA-256 hash.

Conceptually:

```text
SHA256(document bytes)
```

The resulting hash is stored with the document version.

During verification:

```text
Stored Hash
     ↓
Expected SHA-256

Current File
     ↓
Current SHA-256

Compare
     ↓

Same
 → AUTHENTIC

Different
 → TAMPERED
```

Example:

```text
Original SHA-256:
ABC123...

Current SHA-256:
ABC123...

Result:
AUTHENTIC
```

If the document changes:

```text
Original SHA-256:
ABC123...

Current SHA-256:
XYZ789...

Result:
TAMPERED
```

---

# 13. Tamper Demonstration

EVIDENCE-X includes a live tampering demonstration for SIH judging.

The system physically modifies the stored demonstration file without updating the anchored original hash.

The next verification detects the mismatch.

The UI displays:

```text
⚠ DOCUMENT INTEGRITY COMPROMISED

Original SHA-256:
ABC123...

Current SHA-256:
XYZ789...

Result:
TAMPERED
```

The system also records:

* Actor
* Role
* Timestamp
* Document ID
* Case ID
* Action

---

# 14. Live Dashboard Tamper Alert

This is one of the primary SIH demonstration features.

Open the Dashboard in Browser 1.

Then open the same application in Browser 2.

### Browser 1

Login as:

```text
investigator
```

Keep the Dashboard open.

### Browser 2

Login as an authorized user.

Open the document and run:

```text
TAMPER DEMO
```

The dashboard periodically checks integrity state.

When tampering is detected, the dashboard displays a live alert:

```text
⚠ DOCUMENT INTEGRITY COMPROMISED
```

This allows judges to observe the security event happening live.

---

# 15. Version Control

Documents are never overwritten as a historical record.

Example:

```text
Version 1
Version 2
Version 3
```

Each version contains:

* Version number
* File location
* SHA-256
* Uploader
* Timestamp
* Integrity status
* Related document ID
* Audit information

Historical versions remain available.

---

# 16. Evidence Sealing

Evidence sealing protects a finalized evidence version from ordinary modification.

Example:

```text
Document
 ↓
Version 3
 ↓
SEALED
```

After sealing:

```text
Version 3
     ↓
Immutable evidence record
```

Any future change must be made as a **new version** rather than modifying the sealed version.

The system records:

* Seal action
* Actor
* Timestamp
* Version
* SHA-256
* Evidence state

### Important

Sealing does not delete historical records.

It strengthens the chain of custody by preventing silent alteration of the sealed version.

---

# 17. Legal Hold

Legal Hold protects documents that are under investigation, litigation, or legal review.

When Legal Hold is active:

```text
LEGAL HOLD = ACTIVE
```

Operations such as:

* Delete
* Modification
* Destructive changes

are blocked according to the authorization policy.

Example:

```text
Document
 ↓
Legal Hold
 ↓
Modification blocked
 ↓
Deletion blocked
```

The system maintains the original evidence.

Authorized users can create a new version where the workflow permits it.

Legal Hold actions are recorded in the audit trail.

---

# 18. Merkle Root

EVIDENCE-X implements an application-level Merkle tree.

For example:

```text
H1
H2
H3
H4
```

Pair hashes:

```text
H12 = SHA256(H1 + H2)

H34 = SHA256(H3 + H4)
```

Merkle root:

```text
ROOT = SHA256(H12 + H34)
```

If there is an odd number of hashes, the last hash is duplicated.

Example:

```text
H1
H2
H3

H12 = SHA256(H1 + H2)

H33 = SHA256(H3 + H3)

ROOT = SHA256(H12 + H33)
```

The Merkle root provides an additional integrity representation for a group of document/version hashes.

---

# 19. Blockchain-Style Ledger

The local prototype uses a hash-linked ledger.

It does NOT store complete document files on the blockchain.

Only integrity metadata is anchored.

A ledger block contains information such as:

* Block number
* Transaction ID
* Timestamp
* Previous block hash
* Transaction information
* Merkle root
* Current block hash

Example:

```text
Block 1

Previous Hash:
GENESIS

Transaction:
DOCUMENT_UPLOAD

Block Hash:
ABC...
```

Next block:

```text
Block 2

Previous Hash:
ABC...

Transaction:
INTEGRITY_VERIFY

Block Hash:
XYZ...
```

Therefore:

```text
Block 1
   ↓
Block 2
   ↓
Block 3
   ↓
Block 4
```

Changing an earlier block would break the subsequent hash relationship.

---

# 20. Off-Chain Storage

Sensitive documents are stored off-chain.

Prototype:

```text
backend/
└── data/
    └── files/
```

The ledger stores integrity information rather than complete document content.

### Production Storage

The storage layer can be replaced with:

* MinIO
* Amazon S3
* Azure Blob Storage
* Government cloud object storage
* Other compliant enterprise object storage

---

# 21. AI-Assisted Document Classification

EVIDENCE-X can automatically classify documents based on extracted content and document signals.

Example classifications:

* FIR
* Investigation Report
* Witness Statement
* Charge Sheet
* Forensic Report
* Court Filing
* Legal Notice
* Judgment
* Evidence Record

Example:

```text
Uploaded document
       ↓
Text extraction
       ↓
Classification engine
       ↓
"Forensic Report"
```

The prototype can use lightweight local classification logic so it does not require an external AI API just to demonstrate the feature.

---

# 22. OCR

OCR allows text to be extracted from scanned/image documents when an OCR engine is available.

Typical pipeline:

```text
Image / Scanned PDF
        ↓
OCR
        ↓
Extracted Text
        ↓
Classification
        ↓
Sensitive Data Detection
        ↓
Search Index
```

A production implementation can integrate a dedicated OCR service or enterprise OCR engine.

Possible production technologies include:

* Tesseract
* PaddleOCR
* Azure AI Document Intelligence
* Google Document AI
* Amazon Textract
* Government-approved OCR services

---

# 23. Intelligent Semantic Search

EVIDENCE-X supports content-aware search rather than relying only on filenames.

The search pipeline can use:

```text
Document metadata
       +
Extracted text
       ↓
Search index
       ↓
Ranking
       ↓
Relevant documents
```

The prototype uses SQLite indexing/FTS capabilities where practical.

This enables fast searching across:

* Case ID
* Document title
* Document type
* Uploader
* Extracted content

### Production Search Architecture

For a larger deployment, the recommended architecture is:

```text
Object Storage
      ↓
Text/OCR Extraction
      ↓
Search Pipeline
      ↓
OpenSearch / Elasticsearch
      +
Vector Database
      ↓
Hybrid Search
      ↓
Relevant Documents
```

A hybrid approach combining keyword search and vector similarity is recommended for large-scale semantic retrieval.

---

# 24. Sensitive Data Detection

EVIDENCE-X can detect common sensitive data patterns such as:

* Aadhaar-like numbers
* Indian phone numbers
* Email addresses

Example:

```text
Name: Example Person
Aadhaar: 1234 5678 9012
Phone: +91 9876543210
Email: person@example.com
```

The system can identify sensitive fields without modifying the original evidence.

---

# 25. Redaction

The original document is preserved.

Instead of modifying the evidence:

```text
Original Evidence
       ↓
Sensitive Data Detection
       ↓
Redaction
       ↓
Separate Redacted Copy
```

Example:

```text
Original:

Aadhaar:
1234 5678 9012

Email:
person@example.com
```

Redacted copy:

```text
Aadhaar:
[REDACTED]

Email:
[REDACTED]
```

The original remains unchanged and retains its original hash.

The redacted copy is treated as a separate derivative artifact.

---

# 26. Audit Trail

Important operations generate audit events.

Examples:

```text
LOGIN
DOCUMENT_UPLOAD
DOCUMENT_VIEW
DOCUMENT_DOWNLOAD
INTEGRITY_VERIFY
TAMPER_DEMO
VERSION_CREATE
VERSION_RESTORE
EVIDENCE_SEAL
LEGAL_HOLD
LEGAL_HOLD_RELEASE
REDACTION_CREATE
ACCESS_DENIED
```

Each audit record can contain:

* Audit ID
* Timestamp
* Actor
* Role
* Action
* Document ID
* Case ID
* Details

Example:

```text
Action:
TAMPER_DEMO

Actor:
investigator

Role:
Investigator

Document:
DOC-2026-001

Timestamp:
2026-09-09 10:25:41
```

---

# 27. Dashboard

The dashboard provides a security-oriented overview.

Example cards:

```text
TOTAL DOCUMENTS
24

ACCESSIBLE DOCUMENTS
18

TOTAL VERSIONS
51

AUDIT EVENTS
183

VERIFIED DOCUMENTS
22

TAMPER ALERTS
2

BLOCKCHAIN TRANSACTIONS
47
```

Recent activity can show:

```text
✓ Investigation Report uploaded

✓ Evidence verified

⚠ Evidence tampering detected

↩ Version restored

🔒 Evidence version sealed

⚖ Legal hold applied
```

---

# 28. Logout

The Dashboard includes a visible **Logout** option.

Logout:

1. Clears the local demo authentication state.
2. Returns the user to the login page.
3. Does not depend on token expiration.

There is no automatic session timeout in this prototype.

---

# 29. Fast Data Retrieval Methodology

For fast retrieval, the prototype uses SQLite-based indexing.

The database can index:

* Document ID
* Case ID
* Title
* Document type
* Uploader
* Status
* Version
* Extracted text/search fields

SQLite FTS5 can be used for fast full-text searching.

### Recommended production architecture

For a large organization:

```text
Users
  ↓
FastAPI API
  ↓
Authorization
  ↓
Search Service
  ↓
OpenSearch / Elasticsearch
  +
Vector Search
  ↓
Object Storage
```

Metadata remains in a relational database.

Documents remain in object storage.

Search indexes remain separate from document storage.

This prevents the application database from becoming a bottleneck.

---

# 30. System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   EVIDENCE-X UI     │
                    │ HTML/CSS/JavaScript │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI API      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌─────────────┐ ┌──────────────┐
        │    MFA     │ │    RBAC     │ │ Audit Trail  │
        └────────────┘ └─────────────┘ └──────────────┘
                │              │
                └──────────────┼──────────────┐
                               ▼              ▼
                       ┌──────────────┐ ┌──────────────┐
                       │   Document   │ │   Search     │
                       │  Management  │ │    Engine    │
                       └──────┬───────┘ └──────────────┘
                              │
                 ┌────────────┼─────────────┐
                 ▼            ▼             ▼
          ┌────────────┐ ┌───────────┐ ┌──────────────┐
          │   SQLite   │ │ File/Object│ │ OCR / AI     │
          │  Metadata  │ │  Storage   │ │ Processing   │
          └────────────┘ └───────────┘ └──────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   SHA-256       │
                     │   Merkle Root   │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Hash-Linked     │
                     │ Ledger          │
                     └────────┬────────┘
                              │
                              ▼
                     Production option:
                     Hyperledger Fabric
```

---

# 31. Project Structure

```text
EVIDENCE-X-SIH26190/
│
├── README.md
├── START-WINDOWS.bat
│
├── backend/
│   ├── app.py
│   ├── __init__.py
│   ├── requirements.txt
│   │
│   └── data/
│       └── files/
│
├── frontend/
│   └── index.html
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FABRIC-INTEGRATION.md
│   ├── SECURITY.md
│   └── DEMO-GUIDE.md
│
└── tests/
    └── test_api.py
```

Runtime database/storage files are automatically created as required.

---

# 32. Technology Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript

No separate frontend development server is required.

---

## Backend

* Python
* FastAPI
* Uvicorn
* Python standard library

---

## Database

* SQLite

Advantages:

* No external database server
* Lightweight
* Reliable for demonstration
* Fast indexed queries
* Easy local deployment

---

## Integrity

* SHA-256
* Merkle tree
* Hash-linked ledger

---

## Security

* RBAC
* MFA
* Server-side authorization
* Safe file handling
* Filename sanitization
* Upload size limits
* Audit logging
* Evidence sealing
* Legal hold

---

## AI / Intelligent Processing

* OCR
* Lightweight automatic classification
* Full-text search
* Content-aware retrieval

---

# 33. Installation — Windows

## Requirement

Install Python 3.11 or newer.

Check:

```bash
python --version
```

---

## Option 1 — Automatic Setup

Extract:

```text
EVIDENCE-X-SIH26190.zip
```

Open the project directory.

Double-click:

```text
START-WINDOWS.bat
```

The script installs the required Python dependencies and starts the FastAPI server.

---

## Option 2 — Manual Setup

Open Command Prompt.

Navigate to:

```bash
cd EVIDENCE-X-SIH26190
```

Then:

```bash
cd backend
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

---

# 34. Open the Application

Open a browser and visit:

```text
http://127.0.0.1:8000
```

The EVIDENCE-X login page will appear.

---

# 35. Installation — Linux

Install Python:

```bash
python3 --version
```

Navigate to the project:

```bash
cd EVIDENCE-X-SIH26190/backend
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run:

```bash
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

---

# 36. API Endpoints

The prototype provides endpoints similar to:

```text
POST /api/login

GET /api/me

GET /api/documents

GET /api/documents/{id}

POST /api/documents/upload

GET /api/documents/{id}/download

GET /api/documents/{id}/verify

POST /api/documents/{id}/tamper-demo

POST /api/documents/{id}/restore/{version}

GET /api/audit

GET /api/blockchain

GET /api/health
```

Protected endpoints validate:

```text
X-User
```

and enforce role permissions.

---

# 37. Health Check

The API includes:

```text
GET /api/health
```

A successful response indicates that the backend is running.

---

# 38. SIH Demonstration Workflow

The recommended presentation workflow is:

## Step 1 — Login

Login as:

```text
investigator
```

Password:

```text
Investigator@123
```

Select:

```text
Investigator
```

The backend validates the selected role.

---

## Step 2 — Upload

Go to:

```text
Upload Document
```

Enter:

```text
Case ID:
FIR-2026-001

Title:
Investigation Report
```

Select access:

```text
[X] Investigator
[X] Forensic Officer
```

---

## Step 3 — MFA

Because upload is a sensitive operation:

```text
MFA Verification
```

Enter the generated demonstration OTP.

---

## Step 4 — Automatic Processing

The system performs:

```text
Upload
 ↓
SHA-256
 ↓
Version 1
 ↓
Classification
 ↓
Text extraction
 ↓
Sensitive data detection
 ↓
Merkle Root
 ↓
Ledger Transaction
 ↓
Audit Event
```

---

## Step 5 — Verify

Open the document.

Click:

```text
VERIFY
```

Result:

```text
✓ AUTHENTIC
```

---

# 39. Live Tamper Demonstration

Use two browser windows.

### Browser 1

Login as:

```text
investigator
```

Open:

```text
Dashboard
```

Keep it visible.

### Browser 2

Login as another authorized user.

Open the same document.

Click:

```text
TAMPER DEMO
```

Complete MFA.

The stored demonstration file is modified.

Return to Browser 1.

The Dashboard should detect the changed integrity state.

Expected:

```text
⚠ DOCUMENT INTEGRITY COMPROMISED
```

Then open the document and verify it.

Expected:

```text
Original SHA-256:
ABC123...

Current SHA-256:
XYZ789...

⚠ TAMPERED
```

---

# 40. Audit Demonstration

Open:

```text
Audit Trail
```

Show:

```text
TAMPER_DEMO
```

with:

```text
Actor:
investigator

Role:
Investigator

Timestamp:
...

Document:
...
```

This demonstrates accountability.

---

# 41. Blockchain Demonstration

Open:

```text
Blockchain Ledger
```

Show:

```text
Block Number
Transaction ID
Timestamp
Previous Block Hash
Merkle Root
Block Hash
```

Explain:

> "The actual document remains off-chain. We use cryptographic hashes and a hash-linked ledger to create a tamper-evident integrity record."

---

# 42. Version Restoration

Open:

```text
Version History
```

Example:

```text
Version 1
Version 2
Version 3
```

Select a valid previous version.

Click:

```text
Restore Version
```

Complete MFA if requested.

The selected version becomes current.

Historical versions remain preserved.

Verify again:

```text
✓ AUTHENTIC
```

---

# 43. Evidence Sealing Demonstration

Create or select a finalized evidence version.

Choose:

```text
Seal Evidence
```

Complete MFA.

The system records:

```text
SEALED
```

The sealed version cannot be silently modified.

Any future change must use a new version.

---

# 44. Legal Hold Demonstration

Select a document.

Apply:

```text
LEGAL HOLD
```

The system records the legal hold event.

While the hold is active, protected destructive/modification operations are blocked.

This protects evidence that is subject to an investigation or legal process.

---

# 45. AI Classification Demonstration

Upload a document containing recognizable legal/investigation terminology.

The system extracts available text.

The classification engine analyzes the content.

Example:

```text
Classification:
Forensic Report
```

Other supported categories include:

```text
FIR
Investigation Report
Witness Statement
Charge Sheet
Forensic Report
Court Filing
Legal Notice
Judgment
Evidence Record
```

---

# 46. Intelligent Search Demonstration

Search for a phrase or concept appearing inside the document.

Instead of relying only on:

```text
filename.pdf
```

the search can use:

* Metadata
* Extracted text
* Indexed content
* Classification information

For production scale, hybrid lexical + vector search is recommended.

---

# 47. Sensitive Data Redaction Demonstration

Upload a document containing:

```text
Aadhaar number
Phone number
Email address
```

Run sensitive-data detection.

The system identifies matching patterns.

Generate:

```text
Redacted Copy
```

The original document remains unchanged.

This is important because the original evidence must retain its integrity.

---

# 48. Security Design

Security principles used by the prototype:

### Confidentiality

* Role-based access
* Document-level access rules
* Server-side authorization

### Integrity

* SHA-256
* Merkle roots
* Hash-linked ledger
* Evidence sealing
* Immutable historical versions

### Accountability

* Audit trail
* Actor identification
* Role tracking
* Timestamped operations

### Availability

* Local SQLite database
* Local filesystem storage
* Simple deployment

### Secure File Handling

The application should:

* Sanitize filenames
* Generate safe unique IDs
* Prevent path traversal
* Limit upload size
* Never execute uploaded files
* Keep files outside executable code paths

---

# 49. Demo vs Production Architecture

## DEMO IMPLEMENTATION

The SIH prototype uses:

```text
FastAPI
SQLite
Local filesystem
Demo MFA
X-User authentication
Application-level Merkle tree
Local hash-linked ledger
Vanilla JavaScript
```

This is intentionally lightweight and easy to run.

---

## PRODUCTION ARCHITECTURE

A production system should use:

```text
Enterprise Identity Provider
        ↓
OAuth2 / OIDC
        ↓
MFA / FIDO2
        ↓
API Gateway
        ↓
FastAPI / Microservices
        ↓
RBAC / ABAC
        ↓
Relational Database
        +
Object Storage
        ↓
OCR / AI Processing
        ↓
OpenSearch / Vector Search
        ↓
Hyperledger Fabric
        ↓
Audit / SIEM
```

---

# 50. Hyperledger Fabric Integration

The prototype does NOT require Hyperledger Fabric to run.

The local ledger is only a demonstration implementation.

A production implementation can replace the local ledger with:

* Hyperledger Fabric peers
* Fabric CA
* MSP
* Ordering service
* Chaincode
* Endorsement policies
* TLS
* Private Data Collections

Suggested organizations:

```text
Police / Investigation Organization
        |
Forensic Department
        |
Legal / Court Organization
        |
Audit Authority
```

Fabric can store or anchor:

```text
Document ID
Case ID
Version
SHA-256
Merkle Root
Timestamp
Actor
Action
Transaction ID
```

Sensitive document content should remain in protected off-chain storage.

Detailed mapping is provided in:

```text
docs/FABRIC-INTEGRATION.md
```

---

# 51. Recommended Production Cloud Architecture

```text
                   Users
                     |
                     ▼
              API Gateway
                     |
                     ▼
              Identity / SSO
                     |
                     ▼
                 FastAPI
                     |
        ┌────────────┼────────────┐
        ▼            ▼            ▼
       RBAC         MFA          Audit
        |
        ▼
 Document Service
        |
   ┌────┴────┐
   ▼         ▼
Database   Object Storage
   |         |
   |         └── Original Evidence
   |
   └── Metadata / Versions
        |
        ▼
 Processing Queue
        |
   ┌────┼─────────────┐
   ▼    ▼             ▼
 OCR   Classification Redaction
   |
   ▼
Search Index
   +
Vector Database
   |
   ▼
Hybrid Search
   |
   ▼
Integrity Service
   |
 SHA-256
   |
 Merkle Root
   |
   ▼
Hyperledger Fabric
```

---

# 52. Scalability Strategy

For larger deployments:

### Storage

Use object storage instead of local filesystem.

### Database

Use PostgreSQL or another enterprise relational database.

### Search

Use OpenSearch / Elasticsearch.

### Semantic Search

Use vector embeddings with a vector database or vector-enabled search engine.

### Processing

Use asynchronous queues for:

* OCR
* Classification
* Hash calculation
* Redaction
* Search indexing

### Deployment

Use containerized services and orchestration where required.

### Monitoring

Integrate:

* Centralized logging
* Metrics
* SIEM
* Alerting
* Health monitoring

---

# 53. Chain of Custody

A production-grade evidence management system should maintain a complete chain of custody.

Example:

```text
Evidence Created
      ↓
Uploaded
      ↓
Hashed
      ↓
Integrity Anchored
      ↓
Viewed
      ↓
Downloaded
      ↓
Verified
      ↓
Sealed
      ↓
Transferred
      ↓
Reviewed
```

Each important event should have:

* Actor
* Timestamp
* Action
* Document/version
* Integrity information

---

# 54. Compliance Considerations

EVIDENCE-X is designed with compliance-oriented principles including:

* Least privilege
* Auditability
* Data integrity
* Access control
* Evidence preservation
* Legal hold
* Controlled modification
* Data minimization
* Traceability

Actual production compliance depends on the applicable Indian laws, government policies, departmental procedures, security standards, retention policies, and deployment environment.

The prototype itself should not be treated as a certified compliance system.

---

# 55. Limitations of the Prototype

This project is a demonstrable SIH prototype.

It is NOT a production deployment.

Current limitations may include:

* Demo authentication instead of enterprise SSO
* Local storage instead of government/cloud object storage
* Local ledger instead of Hyperledger Fabric
* Lightweight classification instead of a large trained AI model
* Prototype OCR integration
* Local SQLite instead of distributed database infrastructure
* Prototype semantic retrieval rather than a large-scale vector infrastructure
* Demo MFA rather than hardware-backed enterprise MFA

These limitations are intentional so the project can be demonstrated easily without requiring a complex infrastructure setup.

---

# 56. Future Enhancements

Potential future development:

## AI

* Advanced legal-document LLM
* Named Entity Recognition
* Case summarization
* Timeline extraction
* Relationship extraction
* Evidence correlation
* Automated anomaly detection
* Multilingual OCR
* Indian-language document classification

## Search

* Vector embeddings
* Hybrid search
* Natural-language queries
* Case similarity
* Evidence relationship graphs

## Security

* FIDO2
* Hardware security modules
* Digital signatures
* PKI
* Smart cards
* Device trust
* Zero-trust architecture

## Blockchain

* Hyperledger Fabric
* Smart contracts
* Multi-organization endorsement
* Private data collections
* Cross-department verification

## Infrastructure

* Kubernetes
* High availability
* Disaster recovery
* Geographic redundancy
* Immutable backups
* SIEM integration

---

# 57. Testing

Automated API tests are included under:

```text
tests/test_api.py
```

The tests cover important backend functionality.

Run:

```bash
python -m pytest tests/
```

If pytest is not installed:

```bash
python -m pip install pytest
```

---

# 58. Troubleshooting

## Server does not start

Check:

```bash
python --version
```

Then:

```bash
python -m pip install -r backend/requirements.txt
```

Start manually:

```bash
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

---

## Port 8000 is already in use

Start using another port:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

---

## Login fails

Use the exact demonstration credentials.

Example:

```text
Username:
investigator

Password:
Investigator@123
```

Make sure the selected role matches the account.

---

## MFA upload does not continue

Make sure:

1. The MFA code is entered correctly.
2. The code is verified.
3. The selected file is still present.
4. The browser console does not show an error.
5. The FastAPI terminal is running.

---

## Documents do not appear

Check that the FastAPI backend is running and that the browser is accessing:

```text
http://127.0.0.1:8000
```

not a separate frontend server.

---

# 59. Important Security Notice

The credentials included in this README are demonstration credentials.

Do not use them in production.

Do not expose the prototype directly to the public internet.

Before production deployment:

* Replace demo authentication.
* Enable enterprise identity.
* Enable real MFA.
* Use secure session management.
* Use TLS.
* Use protected object storage.
* Encrypt sensitive data at rest.
* Encrypt data in transit.
* Use key management/HSM where appropriate.
* Configure proper backups.
* Implement disaster recovery.
* Configure centralized logging.
* Conduct security testing.
* Perform penetration testing.
* Implement departmental retention policies.
* Review applicable legal/compliance requirements.

---

# 60. Why EVIDENCE-X Is Different

EVIDENCE-X is not simply a document CRUD application.

Its architecture connects:

```text
Identity
  +
RBAC
  +
MFA
  +
Document Management
  +
Version Control
  +
SHA-256
  +
Merkle Root
  +
Blockchain Integrity
  +
Evidence Sealing
  +
Legal Hold
  +
Audit Trail
  +
OCR
  +
AI Classification
  +
Intelligent Search
  +
Sensitive Data Detection
  +
Redaction
```

The goal is to provide a complete security lifecycle for sensitive legal and investigation documents.

---

# 61. One-Line SIH Pitch

> **EVIDENCE-X is a secure digital evidence platform that combines RBAC, MFA, cryptographic integrity, blockchain-based tamper evidence, immutable versioning, legal hold, AI-powered document intelligence, intelligent search, and privacy-preserving redaction to protect the complete lifecycle of legal and investigation documents.**

---

# 62. Suggested Judge Demonstration

For the strongest live demonstration:

```text
LOGIN
  ↓
ROLE VALIDATION
  ↓
MFA
  ↓
UPLOAD INVESTIGATION REPORT
  ↓
AI CLASSIFICATION
  ↓
SHA-256
  ↓
VERSION 1
  ↓
MERKLE ROOT
  ↓
LEDGER ANCHOR
  ↓
AUTHENTIC
  ↓
SECOND INVESTIGATOR EDITS
  ↓
TAMPER DEMO
  ↓
HASH MISMATCH
  ↓
LIVE RED TAMPER ALERT
  ↓
AUDIT TRAIL
  ↓
BLOCKCHAIN LEDGER
  ↓
EVIDENCE SEAL
  ↓
LEGAL HOLD
  ↓
SENSITIVE DATA DETECTION
  ↓
REDACTED COPY
  ↓
VERSION HISTORY
  ↓
RESTORE
  ↓
AUTHENTIC
```

This demonstrates confidentiality, integrity, authentication, authorization, accountability, evidence preservation, intelligent retrieval, privacy protection, and tamper detection in one workflow.

---

# 63. Project Status

**Project:** EVIDENCE-X

**SIH Problem:** SIH26190

**Prototype Type:** Local working demonstration

**Primary Backend:** FastAPI

**Primary Frontend:** HTML/CSS/JavaScript

**Database:** SQLite

**Integrity:** SHA-256 + Merkle Root

**Ledger:** Local hash-linked blockchain-style ledger

**Authentication:** Stable demo authentication using `X-User`

**MFA:** Demonstration TOTP/OTP workflow

**RBAC:** Implemented

**Version Control:** Implemented

**Evidence Sealing:** Implemented

**Legal Hold:** Implemented

**Audit Trail:** Implemented

**Tamper Detection:** Implemented

**Live Dashboard Alert:** Implemented

**OCR:** Prototype/local processing

**Document Classification:** Implemented lightweight classification

**Sensitive Data Detection:** Implemented

**Redacted Copies:** Implemented

**Semantic/Content Search:** Implemented prototype approach

**Hyperledger Fabric:** Production integration architecture documented; not required for local demo

---

# 64. License / Usage

This project is developed as a Smart India Hackathon prototype.

Before production or government deployment, the implementation should undergo:

* Security review
* Architecture review
* Privacy review
* Legal/compliance review
* Performance testing
* Penetration testing
* Infrastructure hardening
* Identity integration
* Disaster recovery testing

---

## EVIDENCE-X

### Secure Digital Evidence & Legal Document Management Platform

**Smart India Hackathon 2026 — SIH26190**

**Secure. Traceable. Tamper-Evident. Intelligent.**

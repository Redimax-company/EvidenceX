# EVIDENCE-X Architecture

## Logical flow

```text
User / SIH Judge
      |
      v
Login + Role Selection (demo identity)
      |
      v
X-User request header
      |
      v
FastAPI Authentication
      |
      v
Server-side RBAC + Document ACL
      |
      +-----------------------------+
      |                             |
      v                             v
Document API                 Audit API
      |                             |
      v                             v
SQLite + FTS5 indexes       Append-only audit events
      |
      +------------------------------+
      |                              |
      v                              v
Off-chain file store         Document Intelligence
      |                       OCR-ready extraction
      |                       Auto classification
      |                       Semantic content search
      v                              |
SHA-256 -----------------------------+
      |
      v
Application Merkle Root
      |
      v
Hash-linked Integrity Ledger
      |
      v
Production: Hyperledger Fabric
```

## Security controls

- Role-based access control is enforced by the backend, not only the UI.
- The creator selects roles that can access a document. If Investigator is selected, another Investigator can collaborate by creating a new version.
- Sensitive actions require a current demo TOTP: upload, new version, tamper demo, restore, evidence seal, legal hold and deletion.
- Evidence versions are immutable records. Evidence sealing permanently seals the selected version; later changes must be made as a new version.
- Legal Hold blocks modification and deletion while the hold is active.
- SHA-256 is anchored with the version record and ledger transaction.
- A Merkle root is recalculated from stored version hashes for application-level integrity anchoring.
- Uploaded files remain off-chain.

## Fast retrieval methodology

SQLite is used because it is zero-configuration and reliable for the SIH demo. B-tree indexes accelerate case/title/type/hold lookups and SQLite FTS5 provides indexed full-text retrieval. A lightweight content-similarity ranking layer compares query terms with extracted document content for semantic-style retrieval without requiring an external vector database.

Production scale-up can replace this layer with OpenSearch/Elasticsearch plus embeddings/vector search, while object storage moves to S3/MinIO/Azure Blob.

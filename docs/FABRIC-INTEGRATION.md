# Hyperledger Fabric Integration

The SIH prototype intentionally runs without Hyperledger Fabric. Its local hash-linked ledger is an adapter boundary for a future permissioned blockchain deployment.

## Proposed production organizations

- Police / Investigation Department
- Forensic Department
- Legal / Court Department
- Audit Authority

## Fabric mapping

| Prototype concept | Hyperledger Fabric production mapping |
|---|---|
| Document ID / case ID | Chaincode asset key and attributes |
| Version hash | Immutable chaincode state field |
| Merkle root | Integrity anchor recorded in transaction |
| Block hash | Fabric ledger ordering/block metadata |
| Actor + role | X.509 identity from Fabric CA / MSP |
| Access roles | Chaincode authorization + channel/private-data policy |
| Legal Hold | Chaincode state transition restricting mutation/deletion |
| Evidence Seal | Chaincode state transition making a version immutable |
| Audit events | Ledger events + external SIEM/audit store |
| Off-chain file | S3/MinIO/Azure Blob object referenced by hash |

## Fabric components

- Fabric CA for organizational identities
- MSP for membership and authorization
- Peers for each organization
- Ordering service for transaction ordering
- TLS for node/client communication
- Chaincode for document metadata, version, sealing, legal hold and integrity state
- Private Data Collections for restricted metadata where required
- Endorsement policies requiring appropriate organizations for sensitive state changes

## Example chaincode operations

```text
CreateDocument(documentId, caseId, sha256, merkleRoot, accessRoles)
CreateVersion(documentId, version, sha256)
SealEvidence(documentId, version)
PlaceLegalHold(documentId, reason)
VerifyIntegrity(documentId, version, observedHash)
RecordAudit(documentId, action, actor)
```

The sensitive document bytes are never placed directly on the Fabric ledger. Only integrity metadata and authorization/audit state are anchored there.

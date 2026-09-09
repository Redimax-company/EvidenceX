# Security Notes

## Implemented in the prototype

- Server-side RBAC and per-document role ACLs
- Role selection on login with server-side role/account matching
- Stable demo identity using `X-User`; no JWT, token expiry or refresh-token loop
- Demo TOTP MFA for sensitive actions
- SHA-256 integrity verification
- Application-level Merkle roots
- Hash-linked integrity ledger
- Immutable historical versions
- Evidence Sealing: sealed version cannot be altered; changes require a new version
- Legal Hold: blocks modification/deletion while active
- Filename sanitization and extension allow-list
- 50 MB upload limit
- Unique document/version IDs
- Audit events, including denied access
- No execution of uploaded files
- Off-chain file storage
- Optional OCR through Pillow + Tesseract when installed
- Sensitive-data detection for Aadhaar-like numbers, Indian phone numbers and email addresses; creates a separate redacted copy

## Deliberate demo simplifications

Credentials are demo-only and are stored in application configuration. The `X-User` mechanism is not proof of identity. The MFA code is deliberately displayed by the demo UI so judges can test the security workflow without an authenticator app.

The local blockchain ledger is **not Hyperledger Fabric**. It is a transparent prototype adapter that can be replaced by Fabric.

## Production controls

Use OIDC/SSO + enterprise identity provider, MFA/authenticator app, secure HttpOnly cookies, password hashing, TLS, KMS/HSM-backed signing keys, encryption at rest, object-lock/WORM retention, malware scanning, DLP, CSP/security headers, rate limiting, SIEM, key rotation, secrets management, vulnerability scanning, backup/DR and formal legal evidence retention policies.

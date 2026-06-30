# Security Policy

## Supported versions

This project is pre-1.0 and under active development. Security fixes are applied
to the `main` branch.

## Reporting a vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

Instead, report privately to **security@example.com** (or use GitHub's
[private vulnerability reporting](https://docs.github.com/code-security/security-advisories)).
Include:

- A description of the issue and its impact
- Steps to reproduce (proof-of-concept if possible)
- Affected service(s): `frontend`, `backend`, or `wa-service`

We aim to acknowledge reports within **72 hours** and to provide a remediation
timeline after triage. We practice coordinated disclosure and will credit
reporters who wish to be named.

## Security practices in this project

- **Secrets** live only in environment variables; `.env` is git-ignored.
- **API keys** are stored hashed (never in plaintext) and are revocable.
- **JWT** for dashboard auth; **API keys** for programmatic access.
- **Internal Django ↔ Node** calls are HMAC-signed and not publicly exposed.
- **Webhooks** are HMAC-signed so receivers can verify authenticity.
- **Rate limiting** and per-number throttling guard abuse and reduce ban risk.
- **Audit logs** record sensitive actions.

See [`docs/security.md`](docs/security.md) for the full security model.

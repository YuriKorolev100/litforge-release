# Security Policy (LitForge)

## Reporting

If you discover a security issue:
- Do not open a public issue with exploit details.
- Contact the maintainer through GitHub private channels.

## Threat model (short)

LitForge prioritizes:
- **Local-first operation**
- **Vault-boundary file access**
- **No built-in networking**
- **Python-only end-user tooling**

Dev tooling may be more permissive, but Release should remain hardened.

# Agent Policy (DEV)

Allowed write paths:
- _LitForge/
- _LitForge/Proposals/
- _LitForge/Tests/reports/
- _LitForge/Build/

Forbidden by default:
- Projects/** (unless ALLOW_PROJECT_WRITES=true)
- OS paths outside vault

All changes must be PR-style:
Proposal note + unified diff + regression report + provenance entry.

# Safety, Privacy, and Threat Model

LitForge is designed around a simple idea:

> **Your vault is the boundary.**  
> Tools may read/write *inside the vault only*, and they do not make network calls.

This keeps the “engine” safe to ship as a zip file and minimizes the chance of an agent running amok.

## Hard constraints (Release / end users)

**BANNED**
- Reading files **outside** the vault directory
- Writing files **outside** the vault directory
- Network calls from LitForge tools (no web, no API calls)
- Shell scripting as a requirement (no bash, no PowerShell, no platform-specific scripts)

**ALLOWED**
- Python-only local tools that operate inside the vault
- BYOK drafting/research **outside** LitForge (user chooses the provider/tool)
- Importing results into LitForge as text + sources (Research Packets)

## What LitForge can’t prevent

Obsidian is file-based. Users can always:
- Delete or edit logs
- Modify templates
- Turn off safeguards

LitForge’s stance:
- We **log by default**
- We **don’t provide guidance for tampering**
- Ship bundles can optionally exclude logs

## BYOK disclosure

If a user chooses to use cloud models (ChatGPT/Claude/etc.), those providers may store prompts/outputs depending on their policies. LitForge does not transmit anything; the user’s chosen provider does.

## Maintainer / Evolver exception (Dev + Personal)

To evolve the engine efficiently, maintainer workflows may temporarily loosen constraints:
- Git operations
- Shell scripts
- Possibly limited network research

These are **explicitly DEV-only** and must never leak into Release as a dependency.

## “No surprises” rule

Any feature that changes safety posture must:
1) be documented in Release docs,
2) be opt-in, and
3) have an obvious “disable” path.

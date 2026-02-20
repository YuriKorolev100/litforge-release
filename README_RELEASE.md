# LitForge (Release)

LitForge is an **Obsidian-native WriterOps engine** that helps writers ship better work through a disciplined, stage-gated workflow:

**Discover → Position → Outline → Draft → Red-Team → Patch → Repeat → Ship**

LitForge is not “AI writes your book.”  
It is a **system for repeatable improvement**: hostile review, diff-first fixes, regression checks, and ship readiness gates.

## Quickstart

1) Download the zip / clone this repo
2) Open the folder as an Obsidian vault
3) From vault root:

```bash
python tools/lf_integrity.py verify
tools/lfctl doctor
tools/lfctl init-project "My Project Name"
```

## Safety + privacy model

- Local-first: tools operate inside the vault only
- No built-in networking
- No shell scripting required (python-only end-user tooling)

See:
- `_LitForge/Operator/02-Safety-Privacy-ThreatModel.md`

## What’s inside

- `_LitForge/` — templates, setup wizard, dashboard, operator docs
- `tools/` — local python tools (doctor/lint/integrity/replay/lfctl)
- `.github/workflows/` — CI gates

## BYOK

You can draft/research with any tool you like (local model or cloud).  
LitForge’s job is to help you structure, review, patch, and ship—while logging what happened.

## License

See `LICENSE` (if present in this repo).

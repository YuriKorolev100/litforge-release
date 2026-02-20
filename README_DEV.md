# LitForge (Dev)

This repo is the **engine evolver** for LitForge.

Purpose:
- prototype improvements
- add/adjust tools and templates
- harden the Release vault
- maintain CI gates and integrity discipline

**The product is `litforge-release`.**  
This repo exists to evolve it safely.

## Maintainer workflow (summary)

1) Write a Work Order
2) Implement on a branch
3) Run local gates:
```bash
python tools/lf_integrity.py verify
tools/lfctl doctor
tools/lfctl lint
```
4) Open PR → CI → merge
5) Promote changes to Release via PR

Docs:
- `_LitForge/Operator/06-Sync-and-Repo-Model.md`
- `_LitForge/Sync/00-Sync-Protocol.md`

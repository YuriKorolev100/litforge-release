# Sync Protocol (STATE / DELTA / Work Orders)

This protocol exists to prevent “we worked all day and don’t know what happened.”

## Files

- `_LitForge/Sync/STATE.md`  
  A snapshot of *current reality* (repos, heads, CI, blockers).

- `_LitForge/Sync/DELTA.md`  
  A running log of *what changed this session*.

- `_LitForge/WorkOrders/*.md`  
  One change request per file; the unit of work that becomes a PR.

## When to update

### Start of session
1) Pull latest on all relevant repos
2) Run verification (doctor + integrity)
3) Update `STATE.md`

### During session
- Each meaningful change gets a Work Order (even if tiny).

### End of session
1) Ensure PRs merged (or clearly left open)
2) Ensure local == remote for Release & Personal (Dev can be on branch)
3) Update `DELTA.md` with what you shipped + links/commit SHAs

## The 3-action loop

To keep momentum and avoid rabbit holes:
- Pick at most **3 actions** per loop.
- Finish them end-to-end (including verification).
- Then start a new loop.

## “Green means green” definition

A repo is “green” when:
- `python tools/lf_integrity.py verify` → PASS
- `tools/lfctl doctor` → ALL CLEAR (0 fails)
- GitHub Actions on `main` → PASS (latest run)

## Copy-paste status commands (maintainers)

```bash
# Local sanity
git status -sb
git log -1 --oneline --decorate
python tools/lf_integrity.py verify
tools/lfctl doctor

# GitHub sanity (requires gh auth)
gh pr list -R YuriKorolev100/<repo> --state open
gh run list -R YuriKorolev100/<repo> -b main -L 3
```

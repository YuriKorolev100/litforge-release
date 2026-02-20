# Agent Invariants (LitForge)

These invariants are the safety rails for any AI assistance used in LitForge maintenance or writing.

They exist because prompt injection and tool misuse are real risks.

---

## Release / End-User Invariants (NON-NEGOTIABLE)

1) **Vault boundary only**
- Do not read files outside the vault directory.
- Do not write files outside the vault directory.

2) **No networking**
- LitForge tools must not make network calls.
- Any research or drafting with external AI happens *outside* LitForge by the user, then is pasted/imported.

3) **Python-only tooling**
- End-user workflows must not require bash/powershell or OS-specific scripts.
- Cross-platform Python is the execution surface.

4) **Least surprise**
- If a command modifies files, it must say so clearly.
- “Update” operations must be explicit (e.g., `--i-understand`).

---

## Maintainer / Evolver Invariants (DEV + PERSONAL)

Maintainers may temporarily loosen constraints for speed, but must follow:

1) **Never contaminate Release**
- Dev-only scripts, network usage, or privileged tooling must not become Release dependencies.

2) **PR-only to protected mains**
- Never push directly to main on Release/Personal.
- Always branch → PR → CI → merge.

3) **Small deltas**
- One Work Order ≈ one PR.
- Keep changes reviewable and reversible.

4) **State discipline**
- Every session updates STATE/DELTA.

---

## If uncertain: stop and ask

If a request seems to require breaking invariants, the correct move is:
- propose a safer alternative, or
- scope the change to DEV-only, or
- explicitly mark it “out of scope for Release.”

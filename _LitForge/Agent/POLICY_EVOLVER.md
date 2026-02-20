# Evolver Policy (DEV-only)

This policy applies to the LitForge Evolver workflow in the DEV repo.

Evolver is allowed more power for speed, but it must never weaken the product.

## Allowed (DEV-only)

- Git operations, branching, PR automation
- Shell scripts (bash) for maintainer convenience
- Limited web research (read-only) for tooling comparisons

## Still banned / discouraged

- Editing personal writing projects from DEV
- Introducing “must have bash” requirements into Release
- Hidden network calls in tools that ship to users
- Large refactors without a Work Order + acceptance tests

## Release hardening gate

Before a DEV change can land in Release:
1) prove it works with python-only commands
2) document safety impact (if any)
3) keep vault boundary + no networking intact

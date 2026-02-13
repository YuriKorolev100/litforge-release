# LitForge Invariants (DEV)

Non-negotiable:
- Backbone order is immutable (Discover → ... → Ship).
- Red-Team loop moat is immutable (hostile audit → patch spec → diff-first → regression → gate).
- "Dashboard" is the canonical term.
- Ship gates cannot be loosened (only tightened).
- DEV agents never write to user Projects/ unless explicitly allowed.

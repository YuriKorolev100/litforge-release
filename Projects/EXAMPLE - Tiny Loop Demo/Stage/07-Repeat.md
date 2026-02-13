---
lf_schema: "stage/v1"
litforge_version: "0.1.0"
project_id: "EXAMPLE_TINY"
project_title: "EXAMPLE - Tiny Loop Demo"
stage: "Repeat"
status: "draft"
loop_speed: "FAST"
mode_packs: ["CORE"]
provider:
  preset: "Simple"
  name: "None"
  model: ""
  browsing: false
  citations: false
gate:
  requires_acceptance: true
  criticals_open: 0
  overrides: []
artifacts:
  inputs: ["06-Patch"]
  outputs: ["08-Ship"]
repeat_decision:
  another_cycle: true
  reason: ""
  next_target_draft: "Drafts/draft_v0.1.md"
provenance:
  log_month: "_LitForge/Logs/provenance/2026-02.md"
---

# 07 — Repeat (decision gate)

## Objective (required)
Decide: loop again or ship. Use evidence, not vibes.

## Current State (required)
- Latest draft: [[Drafts/draft_v0.1]]
- Outstanding issues:
- Criticals open (number):

## Decision (required)
- Another Red-Team cycle? true/false
- Why:
- If looping: new Red-Team target scope:

## Acceptance Tests — Repeat
- [ ] Latest draft linked
- [ ] Decision explicit (true/false)
- [ ] If ship: Ship stage exists/linked and gates reviewed
- [ ] Provenance entry appended

## Revise Plan
-

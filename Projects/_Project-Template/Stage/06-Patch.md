---
lf_schema: "stage/v1"
litforge_version: "0.1.0"
project_id: "TEMPLATE"
project_title: "_Project-Template"
stage: "Patch"
status: "draft"
loop_speed: "STRICT"
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
  inputs: ["05-Red-Team"]
  outputs: ["07-Repeat"]
patch_artifacts:
  patchspec_path: "Patches/PatchSpec_001.md"
  diff_path: "Patches/diffs/diff_001.patch"
  new_draft_path: "Drafts/draft_v0.1.md"
provenance:
  log_month: "_LitForge/Logs/provenance/2026-02.md"
---

# 06 — Patch (diff-first)

## Objective (required)
Findings → Patch Spec → minimal diffs → new draft → regression checks.

## Patch Scope (required)
- Target draft: [[Drafts/draft_v0]]
- New draft: [[Drafts/draft_v0.1]]
- Findings addressed:
  - [ ] RT-001

## Patch Spec (required)
Link: [[Patches/PatchSpec_001]]

## Diff (required)
Link: [[Patches/diffs/diff_001.patch]]

## Regression Checks (required)
Link: [[Tests/Regression_001]]

## Acceptance Tests — Patch
- [ ] PatchSpec exists and maps each finding → change
- [ ] Diff exists (unified diff) showing minimal edits
- [ ] New draft exists and matches diff intent
- [ ] Regression checklist completed and passed
- [ ] Next stage exists/linked
- [ ] Provenance entry appended

## Revise Plan
-

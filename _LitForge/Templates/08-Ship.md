---
lf_schema: "stage/v1"
litforge_version: "0.1.0"
project_id: "TBD"
project_title: "TBD"
stage: "Ship"
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
  ship_requires_redteam_cycles: 1
  criticals_open: 0
  overrides: []
artifacts:
  inputs: ["07-Repeat"]
  outputs: ["Ship/Bundle_*"]
ship_bundle:
  version_tag: "v0.1.0"
  bundle_path: "Ship/Bundle_v0.1.0/"
  required_files:
    - "MANUSCRIPT.md"
    - "POSITION_SNAPSHOT.md"
    - "OUTLINE_SNAPSHOT.md"
    - "PROVENANCE_SUMMARY.md"
    - "CLAIMS_STATUS.md"
provenance:
  log_month: "_LitForge/Logs/provenance/2026-02.md"
---

# 08 — Ship

## Objective (required)
Package a shippable bundle with snapshots and provenance.

## Ship Gates (hard rules)
- ≥1 Red-Team cycle completed: YES/NO
- Unresolved Criticals: 0 (or explicit override in YAML)

## Bundle Contents (required)
Create folder `Ship/Bundle_v0.1.0/` with:
- MANUSCRIPT.md
- POSITION_SNAPSHOT.md
- OUTLINE_SNAPSHOT.md
- PROVENANCE_SUMMARY.md
- CLAIMS_STATUS.md (NF_STRICT) or "N/A"

## Final Checklist
- [ ] ≥1 Red-Team stage approved
- [ ] No unresolved Criticals (or override recorded)
- [ ] Bundle folder exists and contains required files
- [ ] Provenance entry appended
- [ ] Stage status set to shipped

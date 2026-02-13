---
lf_schema: "mode-pack/v1"
pack_id: "NF_STRICT"
version: "1.0.0"
type: "official"
adds_artifacts: ["Claims Table", "Citation Status"]
binary_rule: "real sources or stop/override with Needs verification"
---

# NF_STRICT (official)

## Rule
- If a claim requires sourcing and you cannot provide real sources: block, or require explicit override marked **Needs verification**.

## Required artifacts
- Persistent Claims Table from Discover through Ship.
- Ship bundle must include CLAIMS_STATUS.md.

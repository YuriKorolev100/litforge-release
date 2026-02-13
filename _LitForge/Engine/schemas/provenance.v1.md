# Schema: provenance/v1 (documentation)

Required YAML keys per run entry:
- lf_schema: "provenance/v1"
- run_id
- timestamp (ISO8601)
- operator
- project_id
- project_title
- stage
- loop_speed
- mode_packs
- provider.preset/name/model
- capabilities.browsing/citations
- inputs (array of vault paths)
- outputs (array of vault paths)
- acceptance.result (PASS|FAIL)
- acceptance.evidence (array of vault paths)
- notes (string)

# Schema: stage/v1 (documentation)

Required YAML keys:
- lf_schema: "stage/v1"
- litforge_version
- project_id
- project_title
- stage (Discover|Position|Outline|Draft|Red-Team|Patch|Repeat|Ship)
- status (draft|in_review|revise|approved|blocked|shipped)
- loop_speed (FAST|STRICT)
- mode_packs (array)
- provider.preset (Simple|Balanced|Private)
- provider.name (None|OpenAI|Anthropic|Google|xAI|Local|Other)
- provider.model (string; may be empty)
- provider.browsing (bool)
- provider.citations (bool)
- gate.requires_acceptance (bool)
- gate.criticals_open (int)
- gate.overrides (array)
- artifacts.inputs (array)
- artifacts.outputs (array)
- provenance.log_month (path)

A stage is "approved" only when:
1) its acceptance checklist is fully checked
2) a matching provenance entry is appended

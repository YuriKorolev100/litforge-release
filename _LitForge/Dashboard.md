---
lf_schema: "dashboard/v1"
litforge_version: "0.1.0"
last_updated: 2026-02-07
active_project_path: "Projects/EXAMPLE - Tiny Loop Demo/00-Project-Config.md"
---

# LitForge — Dashboard

> **North Star:** governed iteration that prevents drift, protects uniqueness, and ships finished work with auditable artifacts.

## Big Buttons (manual-first)

> [!tip] 🟩 Run Next Stage
> 1) Open **Active Project Config** → jump to **Next Stage**
> 2) Fill the stage note and complete its **Acceptance Tests**
> 3) Append a **Provenance entry**
> 4) Mark stage **Approved** (or **Revise/Blocked**)

**Go:** [[Projects/EXAMPLE - Tiny Loop Demo/00-Project-Config]]

> [!success] ✅ Approve (Gate)
> Set stage YAML `status: approved` only when its checklist is complete + provenance is appended.

> [!warning] 🟨 Revise
> If acceptance fails: set `status: revise` and write a short Revise Plan.

> [!note] 🔁 Change Provider / Mode
> - [[_LitForge/Setup/00-Setup-Wizard]]
> - [[_LitForge/Setup/01-Capability-Check]]
> - [[_LitForge/Setup/02-Safety-Fence]]

> [!danger] 🚢 Ship
> Requires ≥1 approved Red-Team cycle; unresolved Criticals block ship unless explicit override.

---

## Backbone (immutable)
Discover → Position → Outline → Draft → Red-Team → Patch → Repeat → Ship

## Moat (immutable)
Red-Team Loop = hostile audit → Patch Spec → diff-first fixes → regression checks → approval gate.

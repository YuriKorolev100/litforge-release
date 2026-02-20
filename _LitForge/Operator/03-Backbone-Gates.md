# Backbone and Gates

## Stages

1) **Discover** — capture intent, audience, constraints, references  
2) **Position** — thesis/angle, promise, differentiation  
3) **Outline** — structure, beats/sections, dependencies  
4) **Draft** — writing pass (inside or outside LitForge)  
5) **Red-Team** — hostile review, severity-graded findings  
6) **Patch** — diff-first fixes, targeted edits  
7) **Repeat** — loop until goals met  
8) **Ship** — export + optional handoff packet

## Gates (what “passing” means)

LitForge is stage-gated: you don’t “feel” done—you pass checks.

Typical gates:
- **Completeness**: required fields/artifacts exist
- **Consistency**: outline vs draft matches, key decisions honored
- **Integrity**: engine files unchanged or manifest updated intentionally
- **Sourcing** (NF_STRICT): claims table + citations
- **Regression**: earlier checks still pass after patch

## Fast vs Strict loops

- **FAST**: minimal checks; faster iteration, higher drift risk  
- **STRICT**: heavier checks; slower, but protects quality and uniqueness

## The key behavior change

LitForge’s core behavioral nudge is:
- *Do the work in small, testable deltas.*
- *Record what changed and why.*
- *Never ship an unreviewed revision.*

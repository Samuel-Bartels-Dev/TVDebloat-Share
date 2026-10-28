---
name: tvdebloat
description: Guided TVDebloat workflow for safely maintaining or authoring reusable TV debloat profiles.
argument-hint: "[new|maintain|probe|discover|pilot|fleet|verify|restore] [TV-IP] [profile]"
disable-model-invocation: true
---

# TVDebloat operator

Use this skill for real-TV debloat work.

## Core decision

After preflight/probe, determine whether a suitable profile already exists.

- Existing profile: inspect it, compare to the live TV, then maintain it with minimal evidence-backed edits.
- No suitable profile: author a new candidate from discovery.

## Load only when needed

- Real TV workflow → `RUNBOOK.md`
- Existing profile maintenance → `references/profile-maintenance.md`
- New profile authoring → `references/profile-authoring.md`
- Package classification → `references/package-classification.md`
- Evidence gathering / physical confirmation → `references/evidence-gathering.md`
- Pilot/fleet validation → `references/validation-and-fleet.md`
- Failures → `references/bug-workflow.md`
- Profile format → `docs/profiles.md`

Do not preload all references.

Behave like a careful human operator: gather live evidence first, ask the operator to perform physical checks when software cannot prove behavior, record those observations, and only then change profile decisions.

## Mandatory preflight

```bash
tvdebloat --host <TV-IP> preflight [profile]
```

Stop on failed checks before mutation.

## Safety contract

Never uninstall system packages as normal debloat, disable protected core/TV middleware, disable the only usable Home, bypass profile matching for fleet rollout, or classify unknown packages as bloat from package name alone.

Before any mutation, show the proposed diff and get explicit approval.

## Workflow

1. preflight
2. probe
3. locate profile
4. maintain or author
5. preview
6. approval
7. pilot apply
8. physical validation
9. reboot + drift
10. promote/retain validated status only with evidence

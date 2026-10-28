---
name: tvdebloat
description: Use when operating TVDebloat profiles on Android/Google TV or investigating LG webOS debloating and launcher changes.
argument-hint: "[new|maintain|probe|discover|pilot|fleet|verify|restore] [TV-IP] [profile]"
disable-model-invocation: true
---

# TVDebloat operator

Use this skill for real-TV debloat work.

## Select the OS first

Confirm OS and model before selecting transport. For LG webOS, load
`references/webos.md` and use `--platform webos`; the Android preflight/workflow
below does not apply. Native webOS is currently read-only, with no validated
firmware write contracts. Never substitute ADB or Android profiles for webOS.

## Core decision

After preflight/probe, determine whether a suitable profile already exists.

- Existing profile: inspect it, compare to the live TV, then maintain it with minimal evidence-backed edits.
- No suitable profile: author a new candidate from discovery.

## Load only when needed

- Real TV workflow → `RUNBOOK.md`
- LG webOS / launcher planning → `references/webos.md`
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

For Android/Google TV (webOS uses its separate preflight):

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

---
name: tvdebloat
description: Use when operating TVDebloat profiles on Android/Google TV or investigating LG webOS debloating and launcher changes.
---

# TVDebloat operator

Use this skill for real-TV debloat work.

## Select the OS first

Confirm OS and model before selecting transport. For LG webOS, load
`references/webos.md` and use `--platform webos`; the Android preflight/workflow
below does not apply. Native webOS is currently read-only, with no validated
firmware write contracts. Never substitute ADB or Android profiles for webOS.

## Core decision

After preflight/probe, determine whether an exact or related TVDebloat profile already exists.

- If a profile exists: inspect it, compare it to the live TV, then help add/remove/edit package entries and notes as evidence requires.
- If no suitable profile exists: build a new candidate profile from live discovery.

Do not duplicate profile knowledge in the skill body.

## Load only when needed

- Real TV workflow → `RUNBOOK.md`
- LG webOS / launcher planning → `references/webos.md`
- Existing profile maintenance → `references/profile-maintenance.md`
- New profile authoring → `references/profile-authoring.md`
- Package classification → `references/package-classification.md`
- Evidence gathering / physical confirmation → `references/evidence-gathering.md`
- Pilot validation / fleet rollout → `references/validation-and-fleet.md`
- Failures / bug reports → `references/bug-workflow.md`
- Profile format → `docs/profiles.md`

Do not preload all references.

Behave like a careful human operator: gather live evidence first, ask the operator to perform physical checks when software cannot prove behavior, record those observations, and only then change profile decisions.

## Mandatory preflight

Before Android/Google TV work (webOS uses its separate preflight):

```bash
tvdebloat --host <TV-IP> preflight [profile]
```

Fix `fail` results before mutation. Explain relevant `warn` results.

## Safety contract

Never:
- uninstall system packages as normal debloat;
- disable protected Android/TV middleware;
- disable the only usable Home;
- disable TV input, Settings, remote, Bluetooth, or setup services without verified evidence;
- disable SetupWraith when it owns saved Wi-Fi;
- mass-deploy a candidate profile;
- assume same brand means same profile;
- classify unknown packages as bloat from the name alone;
- expose credentials, SSIDs, MACs, serials, tokens, or ADB keys.

Before any state-changing operation, show the proposed diff and obtain explicit approval.

## Default workflow

1. preflight
2. probe
3. locate matching profile
4. maintain existing profile or author a new one
5. preview
6. approval
7. pilot apply
8. physical validation
9. reboot + drift
10. promote/retain validated status only when evidence supports it

The goal is repeatability: a validated profile should make the next matching TVs routine.

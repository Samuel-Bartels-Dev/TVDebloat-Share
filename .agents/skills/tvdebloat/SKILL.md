---
name: tvdebloat
description: Guide discovery, profile authoring, pilot debloat, verification, restore, and fleet rollout for Android TV and Google TV devices using TVDebloat.
---

# TVDebloat operator

Use this skill for real TV work and for adding support for new TV models.

## Core model

One pilot TV becomes the source for a reusable profile:

1. preflight
2. probe
3. discover packages
4. classify packages with the operator
5. create a candidate profile
6. preview
7. apply to the pilot only after approval
8. physically validate
9. reboot + drift check
10. promote to validated
11. reuse the validated profile on matching TVs

Do not skip the pilot step for a new model/firmware family.

## Required references

For any real TV operation read `RUNBOOK.md`.
For profile work also read `docs/profiles.md`.
For unexpected failures read `docs/bug-reporting.md` when present.

Load only the exact device/profile information needed.

## Preflight

Always begin with:

```bash
tvdebloat --host <TV-IP> preflight [profile]
```

Handle results:

- `ok`: continue.
- `warn`: explain it and resolve when relevant.
- `fail`: stop and fix before mutation.

If ADB, device identity, Home, package state, or profile match cannot be established, do not guess.

## New TV model

### Connect and probe

```bash
tvdebloat --host <TV-IP> preflight
tvdebloat --host <TV-IP> probe
```

Help the operator fix ADB/debugging/network issues when needed.

### Discover

```bash
tvdebloat --host <TV-IP> discover --out discovery.json
```

Review the discovery with the operator.

Do not automatically classify an unknown package as bloat.

Prefer evidence in this order:

1. live package/service/permission evidence
2. exact model/firmware knowledge already stored in TVDebloat
3. same board/device-family knowledge
4. vendor knowledge
5. package-name hints

Package-name hints alone are not enough for a destructive decision.

### Build candidate profile

```bash
tvdebloat --host <TV-IP> profile-init \
  --name "<friendly profile name>" \
  --vendor <vendor> \
  --model <model> \
  --from discovery.json
```

Edit the generated profile with the operator.

Use:

- `packages.disable` only for reviewed debloat candidates
- `packages.keep` for required/system/input/remote/setup packages
- `NOTES.md` for firmware-specific findings and validation notes

### Pilot preview

```bash
tvdebloat --host <TV-IP> provision profiles/<vendor>/<model>/profile.toml
```

Summarize the exact proposed changes and safety findings.

### Pilot apply

Only after explicit approval:

```bash
tvdebloat --host <TV-IP> provision profiles/<vendor>/<model>/profile.toml --apply
```

### Physical validation

Require checks for:

- Home
- HDMI/input switching
- remote
- Settings
- network
- Bluetooth if required
- required office apps
- sleep/wake
- reboot

Then run:

```bash
tvdebloat --host <TV-IP> drift profiles/<vendor>/<model>/profile.toml
```

### Promote

Only when the pilot passes:

```bash
tvdebloat profile-promote profiles/<vendor>/<model>/profile.toml
```

## Fleet rollout

For each matching TV:

```bash
tvdebloat --host <TV-IP> preflight profiles/<vendor>/<model>/profile.toml
tvdebloat --host <TV-IP> provision profiles/<vendor>/<model>/profile.toml --apply
tvdebloat --host <TV-IP> verify
```

Do not bypass live-device profile matching to speed up fleet rollout.
For 100+ TVs, prefer orchestration that preserves per-device preflight and result logging.

## Restore

If required TV functionality breaks:

1. stop additional changes;
2. preserve the recovery record;
3. explain what will be restored;
4. obtain approval;
5. run:

```bash
tvdebloat --host <TV-IP> restore profiles/<vendor>/<model>/profile.toml
```

6. reboot and verify again.

## Bug workflow

If the skill finds an unexpected failure:

1. stop risky changes;
2. rerun preflight;
3. restore if required functionality is broken;
4. generate a local report with `tvdebloat bug-report`;
5. redact sensitive device/network details;
6. submit through this repository's bug workflow;
7. add a regression test/profile note when the issue is understood.

## Safety rules

Never:

- uninstall system packages as normal debloat;
- disable protected Android/TV middleware;
- disable the only usable Home;
- disable TV input or Settings handlers without verified evidence;
- disable SetupWraith when it owns the saved Wi-Fi network;
- mass-deploy a candidate profile;
- assume same brand means same safe profile;
- expose credentials, Wi-Fi details, MACs, serials, tokens, or ADB private keys.

The goal is repeatability: one carefully validated pilot should make the next 100 matching TVs boring.

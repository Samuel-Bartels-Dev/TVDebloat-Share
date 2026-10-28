# TVDebloat architecture

TVDebloat is designed around **profile authoring once, repeatable deployment many times**.

## Core workflow

```text
New TV model
   ↓
Connect / preflight
   ↓
Probe hardware + firmware
   ↓
Inventory packages
   ↓
Classify packages with operator
   ↓
Generate candidate profile
   ↓
Dry-run
   ↓
Apply to one pilot TV
   ↓
Physical validation + reboot
   ↓
Promote profile to validated
   ↓
Apply to matching TVs at scale
```

## First-TV authoring

The first device of a model/firmware family is treated as a **pilot**.

TVDebloat should help the operator:

1. connect to the TV;
2. capture exact device identity;
3. inventory installed/disabled packages;
4. identify known Android core and TV middleware;
5. identify known telemetry/recommendation/vendor packages;
6. mark unknown packages for review rather than guessing;
7. generate a candidate profile;
8. preview every intended change;
9. apply only after approval;
10. physically validate the pilot;
11. reboot and verify again;
12. promote the candidate profile to validated only after success.

## Fleet deployment

A validated profile can be used for many TVs only when the live TV passes profile-match preflight.

A fleet deployment should verify at minimum:

- manufacturer
- model
- device/board where available
- Android version
- SDK level
- firmware/fingerprint family
- required packages are present
- protected packages remain excluded

A mismatch blocks automatic apply.

## Profile lifecycle

Profiles have three states:

- `candidate` — generated from discovery; never mass-deploy automatically
- `validated` — passed pilot apply + physical validation + reboot
- `deprecated` — known obsolete or unsafe for current firmware

## Scope

This phase covers debloat/provisioning only.

Launcher replacement, themes, and unrelated TV customization are intentionally outside this repository until added as separate capabilities later.

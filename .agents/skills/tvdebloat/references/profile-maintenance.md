# Existing profile maintenance

Use when a profile already exists for the TV.

## Flow

1. Read the live TV with:
   - preflight
   - probe
   - audit
   - optional privacy
2. Read the existing profile and NOTES.md.
3. Compare live package state against profile.disable and profile.keep.
4. Build a proposed profile diff.

Allowed maintenance actions:

- add a newly reviewed package to disable
- remove a package from disable when evidence says it is required/unsafe
- move a package from disable to keep
- add a required package to keep
- update device/fingerprint matching
- update firmware notes
- deprecate a profile for incompatible firmware

Never silently edit a validated profile and deploy it broadly.

If changing package decisions on a validated profile:
- treat the edited version as needing pilot revalidation;
- record why each package decision changed;
- preview on one TV first;
- physically validate and reboot before fleet rollout.

Prefer exact, minimal edits over rewriting the whole profile.

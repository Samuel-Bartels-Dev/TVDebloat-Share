Read `evidence-gathering.md` whenever package behavior is uncertain or a decision depends on physical TV behavior.

# New profile authoring

Use when no suitable profile exists.

## Flow

1. Preflight and probe the pilot TV.
2. Run discovery:
   tvdebloat --host <TV-IP> discover --out discovery.json
3. Review discovery with the operator.
4. Create candidate:
   tvdebloat --host <TV-IP> profile-init --name "<name>" --vendor <vendor> --model <model> --from discovery.json
5. Classify packages using package-classification.md.
6. Edit profile.toml and NOTES.md.
7. Preview with provision (without --apply).
8. After approval, apply to the pilot only.
9. Physically validate and reboot.
10. Run drift.
11. Promote only after validation.

Unknown packages remain unclassified until researched.

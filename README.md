# TVDebloat

TVDebloat is a clean-room, office-focused Android TV / Google TV debloating toolkit.

It is being rebuilt from scratch by studying the behavior, safety lessons, and device edge cases of mature Android TV cleanup projects, then implementing those capabilities in a smaller TVDebloat-owned architecture.

**This repository contains debloat/provisioning only.** A custom launcher is intentionally out of scope for this phase.

## Start here

For a real TV, use **[RUNBOOK.md](RUNBOOK.md)**.

Typical workflow:

```bash
python -m pip install -e .

tvdebloat --host 192.168.1.50 preflight profiles/<device>/profile.toml

tvdebloat --host 192.168.1.50 probe

tvdebloat --host 192.168.1.50 audit

tvdebloat --host 192.168.1.50 provision profiles/<device>/profile.toml

# review the preview, then explicitly apply:
tvdebloat --host 192.168.1.50 provision profiles/<device>/profile.toml --apply

tvdebloat --host 192.168.1.50 verify

tvdebloat --host 192.168.1.50 drift profiles/<device>/profile.toml
```

Restore TVDebloat changes:

```bash
tvdebloat --host 192.168.1.50 restore profiles/<device>/profile.toml
```

## Design goals

- disable packages; do not delete system software
- write recovery state before mutation
- fail closed when the TV cannot be understood safely
- protect Android core and TV middleware
- protect the only usable Home application
- protect saved Wi-Fi when SetupWraith owns it
- protect HDMI/AV/tuner service packages
- protect Settings/input handlers unless explicitly reviewed
- match profiles against the live device before applying them
- verify after changes and after reboot
- keep runtime data out of the repository
- generate structured, redaction-ready bug reports

## Repository layout

```text
TVDebloat/
├── tvdebloat/                  clean-room implementation
├── tests/                      TVDebloat-owned regression tests
├── profiles/                   normalized device profiles
├── docs/                       operator and developer references
├── .agents/skills/tvdebloat/   ChatGPT / Codex skill
├── .claude/skills/tvdebloat/   Claude Code skill
├── .github/workflows/          TVDebloat CI
├── RUNBOOK.md
├── ARCHITECTURE.md
└── pyproject.toml
```

## Reference policy

The upstream implementations are references for **behavior and evidence**, not runtime dependencies.

TVDebloat should not tell an operator to follow another project's PR, issue, script, or website in order to complete a normal workflow. Device findings that matter operationally should be rewritten into TVDebloat profiles, tests, or local documentation.

Required license/provenance notices remain in [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

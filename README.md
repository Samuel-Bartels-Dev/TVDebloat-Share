# TVDebloat

TVDebloat is a clean-room, office-focused Android TV / Google TV debloating toolkit.

It is being rebuilt from scratch by studying the behavior, safety lessons, and device edge cases of mature Android TV cleanup projects, then implementing those capabilities in a smaller TVDebloat-owned architecture.

**This repository contains debloat/provisioning only.** A custom launcher is intentionally out of scope for this phase.

## Start here

## Use with ChatGPT/Codex or Claude

TVDebloat ships with repo-local skills that can walk you through connecting to a TV, finding or building its profile, reviewing package decisions, piloting the debloat, and rolling the validated profile out to matching TVs.

**[SKILLS.md](SKILLS.md)** covers:

- how the repo-local skills are discovered;
- optional global/personal installation;
- Claude `/tvdebloat` usage;
- ChatGPT/Codex prompt examples;
- new-TV, existing-profile, pilot, fleet, and recovery prompts.

Example ChatGPT/Codex prompt:

```text
Use the tvdebloat skill. I have a new ASUS TV at 192.168.1.50.
Help me connect, run preflight, see whether a matching profile exists,
and if not build a candidate debloat profile with me.
Do not apply anything until I approve the package diff.
```

Example profile-maintenance prompt:

```text
Use the tvdebloat skill.

Compare the live TV at 192.168.1.50 against:
profiles/sony/<model>/profile.toml

Show me a proposed diff for:
- packages to add to disable,
- packages to remove from disable or move to keep,
- packages that should stay in review.

Explain every proposed change and do not edit the profile until I approve the diff.
```

Example Claude Code command:

```text
/tvdebloat new 192.168.1.50
```


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

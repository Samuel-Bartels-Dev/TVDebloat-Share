# TVDebloat

TVDebloat is a clean-room Android TV / Google TV debloating toolkit built around one operating principle:

> **Learn one TV carefully, save what we learned as a profile, then reuse that validated profile across matching TVs.**

The current phase covers **debloat/provisioning only**. Launcher replacement, themes, and unrelated TV customization are intentionally out of scope.

## Operator start

If you are going to use TVDebloat on a real TV, start with:

- **[RUNBOOK.md](RUNBOOK.md)** — zero-to-first-TV operator onboarding
- **[SKILLS.md](SKILLS.md)** — ChatGPT/Codex and Claude skill installation/use

The runbook assumes the operator may not know Git, ADB, TVDebloat, profile authoring, or the skill workflow yet.

## Primary pilot

The first real target for this project is a **Sony BRAVIA**.

Sony support is intentionally profile-driven rather than based on one universal BRAVIA debloat list. BRAVIA models span multiple Android/Google TV generations, boards, firmware families, input stacks, and vendor packages.

The operator workflow is therefore:

```text
connect
  ↓
preflight
  ↓
probe exact TV
  ↓
find matching profile
  ↓
maintain existing profile
or
build candidate profile
  ↓
gather evidence
  ↓
preview
  ↓
operator approval
  ↓
pilot apply
  ↓
physical validation
  ↓
reboot + drift
  ↓
validated profile
  ↓
matching fleet TVs
```

## Profile model

Real device knowledge lives under:

```text
profiles/<vendor>/<model>/
├── profile.toml
└── NOTES.md
```

A profile separates package decisions into:

```toml
[packages]

disable = [
  # packages validated for debloat
]

keep = [
  # required/protected packages
]

review = [
  # packages that still need evidence or pilot testing
]
```

Profiles have lifecycle states:

- `candidate` — still being researched or piloted
- `validated` — passed pilot testing and reboot validation
- `deprecated` — known obsolete/unsafe for current firmware

A meaningful change to a validated profile should be treated as requiring pilot revalidation before broad rollout.

## Design goals

TVDebloat is intentionally conservative:

- disable packages rather than deleting system software;
- gather live-device evidence before package decisions;
- fail closed when device identity or required TV behavior is unclear;
- protect Android core and TV middleware;
- protect the only usable Home application;
- protect Wi-Fi/setup ownership;
- protect HDMI/input/tuner services;
- protect Settings, remote, Bluetooth, and required handlers;
- write recovery state before mutation;
- show the proposed diff before mutation;
- require operator approval;
- require physical validation after mutation;
- record device-specific findings in the profile/notes;
- reuse validated profiles only on compatible live devices.

The goal is not to produce the largest possible debloat list.

The goal is to produce a **known-good, repeatable profile**.

## Skill architecture

TVDebloat ships with lean repo-local skills:

```text
.agents/skills/tvdebloat/   ChatGPT / Codex
.claude/skills/tvdebloat/   Claude Code
```

The entry skills contain routing and safety rules only.

Detailed workflows are loaded selectively from references such as:

```text
references/
├── evidence-gathering.md
├── package-classification.md
├── profile-authoring.md
├── profile-maintenance.md
├── validation-and-fleet.md
└── bug-workflow.md
```

This keeps normal skill activation small while still giving the operator detailed guidance when needed.

## Repository layout

```text
TVDebloat/
├── tvdebloat/                  implementation
├── tests/                      generic regression tests
├── profiles/                   real TV profiles + template
├── docs/                       profile/developer documentation
├── .agents/skills/tvdebloat/   ChatGPT / Codex skill
├── .claude/skills/tvdebloat/   Claude Code skill
├── .github/workflows/          CI
├── README.md                   project/developer overview
├── RUNBOOK.md                  operator onboarding
├── SKILLS.md                   skill installation + prompt recipes
├── ARCHITECTURE.md             architecture/design
└── pyproject.toml
```

## Development rules

When adding support for a TV:

1. gather evidence from the live device;
2. use existing device knowledge only as supporting evidence;
3. keep uncertain packages in `review`;
4. add or edit the smallest relevant profile;
5. record important findings in `NOTES.md`;
6. validate changes on a pilot;
7. add regression coverage when a behavior can be tested automatically.

Generic tests should use synthetic manufacturers/models. Real device names belong in real profiles and device documentation.

## Reference policy

External projects may be studied for behavior, safety lessons, and compatibility evidence, but TVDebloat operates from its own code, profiles, tests, and documentation.

Normal operator workflows should not depend on following another project's PR, issue, script, or website.

# Using the TVDebloat Skills

TVDebloat ships with two repo-local skills:

- **ChatGPT / Codex:** `.agents/skills/tvdebloat/`
- **Claude Code:** `.claude/skills/tvdebloat/`

The skill is designed to guide a real TV from discovery through a reusable validated profile.

## Recommended: use the repo-local skill

Clone the repo and work from its root:

```bash
git clone https://github.com/Samuel-Bartels-Dev/TVDebloat-Share.git
cd TVDebloat-Share
python -m pip install -e .
```

### Codex / ChatGPT coding workspace

Repo-local Codex skills live under `.agents/skills/`. When the repository is opened as the workspace, the skill can be discovered from its name/description and loaded on demand.

You can explicitly prompt:

```text
Use the tvdebloat skill. I have a new ASUS TV at 192.168.1.50.
Walk me through connecting to it, preflight, discovery, and building a candidate profile.
Do not make state-changing changes without showing me the proposed diff first.
```

Or:

```text
Use the tvdebloat skill to check whether we already have a matching profile for this TV.
If we do, compare it to the live package inventory and help me add/remove/update entries.
If we do not, build a new candidate profile with me.
```

### Claude Code

The repo includes:

```text
.claude/skills/tvdebloat/SKILL.md
```

This skill is intentionally manual-only for real-TV safety.

From Claude Code opened at the repository root:

```text
/tvdebloat new 192.168.1.50
```

Other useful invocations:

```text
/tvdebloat maintain 192.168.1.50 profiles/asus/example/profile.toml
/tvdebloat pilot 192.168.1.50 profiles/asus/example/profile.toml
/tvdebloat fleet 192.168.1.51 profiles/asus/example/profile.toml
/tvdebloat verify 192.168.1.50 profiles/asus/example/profile.toml
/tvdebloat restore 192.168.1.50 profiles/asus/example/profile.toml
```

## Optional: install the skill globally

Repo-local skills are preferred because the instructions and references stay versioned with TVDebloat.

If you want the skill available outside this repository, copy the complete skill folder, including its `references/` directory.

### Codex global/personal install

Default Codex personal skills directory:

```text
${CODEX_HOME:-$HOME/.codex}/skills/
```

macOS/Linux example:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R .agents/skills/tvdebloat "${CODEX_HOME:-$HOME/.codex}/skills/tvdebloat"
```

PowerShell example:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
New-Item -ItemType Directory -Force (Join-Path $codexHome "skills") | Out-Null
Copy-Item -Recurse -Force ".agents/skills/tvdebloat" (Join-Path $codexHome "skills/tvdebloat")
```

Then explicitly ask Codex:

```text
Use the tvdebloat skill to onboard this new TV.
```

### Claude Code global/personal install

Claude Code personal skills directory:

```text
~/.claude/skills/
```

macOS/Linux:

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/tvdebloat ~/.claude/skills/tvdebloat
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Force ".claude/skills/tvdebloat" "$HOME/.claude/skills/tvdebloat"
```

Then invoke:

```text
/tvdebloat new 192.168.1.50
```

## Prompt recipes

## Example: edit an existing debloat list

### ChatGPT / Codex prompt

```text
Use the tvdebloat skill.

I have this TV:
- IP: 192.168.1.50
- profile: profiles/sony/<model>/profile.toml

Compare the live TV against the existing profile.

I want you to help me maintain the debloat list:
- show packages that are in the profile but no longer installed,
- show packages that are newly installed on the TV,
- show packages in disable that appear unsafe or required,
- show packages in keep that may no longer be needed,
- show likely telemetry/recommendation/vendor-content packages that should be reviewed.

Do not change the profile yet.

First give me a proposed diff with three sections:
1. add to disable
2. remove from disable / move to keep
3. keep in review / needs more evidence

For every proposed package change, explain why.

After I approve the diff, edit the profile with the smallest possible changes, update NOTES.md with the reason, and treat the edited profile as requiring pilot revalidation before fleet rollout.
```

### Add one package to review

```text
Use the tvdebloat skill.

Open profiles/sony/<model>/profile.toml.

Add com.vendor.example to packages.review, not packages.disable.

Update NOTES.md with:
- why we are reviewing it,
- what evidence we still need,
- what TV behavior must be tested before it could move to disable.

Do not change anything else.
```

### Move a package from review to disable

```text
Use the tvdebloat skill.

We tested com.vendor.example on the pilot TV and confirmed:
- Home still works,
- HDMI/input switching works,
- remote works,
- Settings works,
- network works,
- required office apps work,
- reboot passed.

Move com.vendor.example from packages.review to packages.disable in:
profiles/sony/<model>/profile.toml

Update NOTES.md with the validation evidence.

Do not promote or mass-deploy the profile yet. Show me the diff first.
```

### Remove an unsafe package from disable

```text
Use the tvdebloat skill.

In profiles/sony/<model>/profile.toml, com.vendor.inputservice is currently in packages.disable.

The pilot showed that disabling it breaks HDMI input switching.

Move it out of packages.disable and into packages.keep.

Update NOTES.md with the failure and recovery result.

Show me the exact diff before editing.
```


### New TV model

```text
Use the tvdebloat skill.

This is the first TV of this model.
Help me:
1. preflight the workstation and TV,
2. connect with ADB,
3. probe exact model/board/firmware,
4. see if a profile already exists,
5. if not, discover packages and build a candidate profile,
6. classify packages with me,
7. preview the debloat.

Do not apply changes until I approve the proposed package diff.
```

### Existing profile maintenance

```text
Use the tvdebloat skill.

I have this TV and an existing profile:
profiles/<vendor>/<model>/profile.toml

Compare the live TV against the profile.
Show:
- newly installed packages,
- packages that disappeared,
- disable-list packages that came back,
- keep-list conflicts,
- possible new telemetry/recommendation packages.

Help me edit the profile with the smallest evidence-backed changes.
Treat any changed validated profile as requiring a new pilot validation.
```

### Pilot apply

```text
Use the tvdebloat skill for a pilot deployment.

Run preflight and preview this profile on the TV.
Explain every package that will change and every warning.
Do not apply until I explicitly approve.
After apply, walk me through the physical validation and reboot/drift checks.
```

### Fleet rollout

```text
Use the tvdebloat skill for fleet deployment.

This profile has already been validated on the pilot:
profiles/<vendor>/<model>/profile.toml

For each TV, require profile-match preflight before applying.
Do not bypass mismatches.
Record which TVs passed, failed, or need review.
```

### Diagnose a failure

```text
Use the tvdebloat skill.

A TV failed during provisioning.
Stop state-changing work.
Rerun preflight, inspect recovery state, and help determine whether we should restore.
If this is a TVDebloat bug or new device behavior, generate the structured bug report and tell me what profile/test documentation should be updated.
```

## What the skill loads

The entry skill is intentionally small.

It selectively reads only what the current task needs:

- `references/profile-maintenance.md`
- `references/profile-authoring.md`
- `references/package-classification.md`
- `references/validation-and-fleet.md`
- `references/bug-workflow.md`
- `RUNBOOK.md`
- `docs/profiles.md`

This keeps normal skill activation small while preserving detailed workflows when needed.

## Skill vs manual commands

The skill does not replace the CLI.

It uses the same commands documented in `RUNBOOK.md`, but adds:

- decision-making about whether to maintain or create a profile;
- package classification guidance;
- preflight handling;
- approval gates;
- physical validation prompts;
- profile lifecycle management;
- bug-report routing.

The manual runbook remains useful for operators who do not want to use an AI agent.

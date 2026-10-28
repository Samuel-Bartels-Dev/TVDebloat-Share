# TVDebloat Operator Runbook

This is the **start-here guide for an operator using TVDebloat on a real TV**.

It assumes you may not know:

- Git
- Python
- ADB
- Android/Google TV developer options
- TVDebloat
- profile authoring
- Codex/ChatGPT skills
- Claude Code skills

Follow the sections in order.

The primary pilot for this project is a **Sony BRAVIA**, but the workflow is generic and can be reused for other Android TV / Google TV devices.

---

# 0. What TVDebloat is going to do

For a new TV model, TVDebloat should not immediately disable a huge list of packages.

The safe workflow is:

```text
one pilot TV
   ↓
connect
   ↓
preflight
   ↓
probe exact model/board/firmware
   ↓
find matching profile
   ↓
┌──────────────────────────────┐
│ profile exists?              │
├──────────────┬───────────────┤
│ yes          │ no            │
│ compare/edit │ discover      │
│ it           │ packages      │
└──────┬───────┴───────┬───────┘
       ↓               ↓
      gather evidence with operator
               ↓
        proposed profile diff
               ↓
        explicit approval
               ↓
           pilot apply
               ↓
       physical TV testing
               ↓
          reboot + drift
               ↓
        validated profile
               ↓
      matching fleet TVs
```

TVDebloat normally **disables** reviewed packages for the Android user. It does not normally uninstall/delete system packages.

---

# 1. Prepare your workstation

You need:

- Git
- Python 3.11 or newer
- Android Platform Tools / ADB

Optional, but recommended:

- ChatGPT/Codex coding workspace
- Claude Code

## 1.1 Check what is already installed

### Windows PowerShell

```powershell
git --version
python --version
adb version
```

### macOS / Linux

```bash
git --version
python3 --version
adb version
```

Each command should print a version.

If a command says it cannot be found, install that prerequisite before continuing:

- **Git** — install Git for your operating system.
- **Python** — install Python 3.11 or newer.
- **ADB** — install Google's Android Platform Tools and make sure the folder containing `adb` is on your PATH.

If you are using the skill, you can simply tell it:

```text
Use the tvdebloat skill.

I am at the workstation setup step.
Check whether Git, Python, and ADB are installed and walk me through anything that is missing.
```

---

# 2. Download TVDebloat

Open PowerShell or Terminal.

```bash
git clone https://github.com/Samuel-Bartels-Dev/TVDebloat-Share.git
cd TVDebloat-Share
```

You should now be inside the repository.

Install TVDebloat.

### Windows

```powershell
python -m pip install -e .
```

### macOS / Linux

```bash
python3 -m pip install -e .
```

Verify the install:

```bash
tvdebloat --help
```

If TVDebloat prints command help, continue.

If not, stop and fix the Python/install problem before touching the TV.

---

# 3. Choose how you want to operate TVDebloat

You can use TVDebloat manually, but the recommended workflow is to use the included skill so the agent guides the operator through each decision.

## Option A — ChatGPT / Codex

The repo already contains:

```text
.agents/skills/tvdebloat/
```

### Recommended: use it directly from this repo

Open **TVDebloat-Share as your coding workspace**.

Then prompt:

```text
Use the tvdebloat skill.

I am onboarding our first Sony BRAVIA and I do not know the process.

Guide me from the beginning:
1. check the workstation,
2. help me enable the correct ADB/debugging method,
3. connect to the TV,
4. run preflight and probe,
5. look for a matching profile,
6. if one exists, compare/edit it with me,
7. if one does not exist, discover packages and build a candidate profile,
8. gather real evidence for package decisions,
9. ask me to physically test anything you cannot prove remotely,
10. show me the proposed diff before changing anything.

Do not make state-changing changes until I explicitly approve them.
```

The skill should tell you what to do next.

You do not need to memorize the rest of this runbook while using the skill.

### Optional personal/global Codex install

You only need this if you want the skill available outside this repo.

#### Windows PowerShell

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
New-Item -ItemType Directory -Force (Join-Path $codexHome "skills") | Out-Null
Copy-Item -Recurse -Force ".agents/skills/tvdebloat" (Join-Path $codexHome "skills/tvdebloat")
```

#### macOS / Linux

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R .agents/skills/tvdebloat "${CODEX_HOME:-$HOME/.codex}/skills/tvdebloat"
```

Then ask:

```text
Use the tvdebloat skill to onboard this TV.
```

## Option B — Claude Code

The repo already contains:

```text
.claude/skills/tvdebloat/
```

Open Claude Code from the **TVDebloat-Share repository root**.

If you know the TV IP:

```text
/tvdebloat new 192.168.1.50
```

If you do not know anything yet:

```text
/tvdebloat new

This is our first Sony BRAVIA.
I do not know the IP, exact model, Android version, or debugging method yet.
Walk me through everything from the beginning.
```

### Optional personal/global Claude install

#### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Force ".claude/skills/tvdebloat" "$HOME/.claude/skills/tvdebloat"
```

#### macOS / Linux

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/tvdebloat ~/.claude/skills/tvdebloat
```

More prompt examples are in [SKILLS.md](SKILLS.md).

---

# 4. Identify the TV before changing it

Do not assume that all Sony BRAVIA TVs use the same packages or debugging method.

Before changing anything, record what you can see physically:

- manufacturer
- exact model number
- Android TV / Google TV version if shown
- current firmware/build if shown
- whether this is a new/factory TV or already configured
- whether Ethernet or Wi-Fi is in use
- which functions the office requires:
  - HDMI inputs
  - tuner/live TV
  - Bluetooth
  - casting
  - remote
  - required streaming/office apps

If using the skill, tell it what you know.

Example:

```text
This is a Sony BRAVIA.
The sticker/model screen says <MODEL>.
We use HDMI 1 and HDMI 2, the Sony remote, Ethernet, and one required office app.
We do not care about vendor recommendations or promotional content.
```

That context matters when deciding what is safe to remove.

---

# 5. Enable ADB/debugging on the TV

Android TV / Google TV menu names differ by generation.

A common path is:

1. Open **Settings**.
2. Open **System** or **Device Preferences**.
3. Open **About**.
4. Find **Build**, **Android TV OS build**, or a similar build entry.
5. Press it repeatedly until the TV says Developer Options are enabled.
6. Go back.
7. Open **Developer Options**.
8. Enable the debugging option available on that TV.

Depending on the TV, you may see:

- ADB debugging
- Network debugging
- Wireless debugging

## If the TV uses classic network ADB

The usual endpoint is:

```text
<TV-IP>:5555
```

TVDebloat defaults to port 5555.

## If the TV uses Android wireless debugging/pairing

The TV may show:

- a pairing IP/port
- a pairing code
- a separate connection/debug port

Pair first with ADB:

```bash
adb pair <TV-IP>:<PAIRING-PORT>
```

Enter the pairing code shown on the TV.

Then connect using the debug endpoint:

```bash
adb connect <TV-IP>:<DEBUG-PORT>
```

When using TVDebloat with a non-5555 debug port:

```bash
tvdebloat --host <TV-IP> --port <DEBUG-PORT> preflight
```

If you are unsure which mode the Sony BRAVIA uses, stop and let the skill help identify the correct flow for that exact model/Android version.

---

# 6. Find the TV's IP address

The exact menu varies by TV.

Look under the TV's network/status information for its IPv4 address.

It will usually look similar to:

```text
192.168.1.50
```

Your workstation and TV need network connectivity to each other.

Do not expose ADB directly to the public internet.

---

# 7. Test ADB manually

Before using TVDebloat, verify that ADB can see the TV.

For classic network ADB:

```bash
adb connect <TV-IP>:5555
adb devices
```

For a different debug port:

```bash
adb connect <TV-IP>:<DEBUG-PORT>
adb devices
```

Look at the physical TV.

The TV may ask whether to allow debugging from this computer.

Approve it only if this is your workstation.

Then run:

```bash
adb devices
```

The TV should appear as an authorized device.

If it says `unauthorized`, look at the TV for the authorization prompt.

If it is offline/not found, stop and fix connectivity/debugging before continuing.

---

# 8. Run TVDebloat preflight

For the first TV, when no profile is known yet:

```bash
tvdebloat --host <TV-IP> preflight
```

If using a non-default debug port:

```bash
tvdebloat --host <TV-IP> --port <PORT> preflight
```

Preflight should confirm things such as:

- Python/ADB availability
- TV responsiveness
- device identity
- current Home
- package-state readability

## Interpret the result

- **ok** — continue
- **warn** — understand it before proceeding if relevant
- **fail** — stop and fix it

Do not ignore failed preflight checks to save time.

---

# 9. Probe the exact TV

```bash
tvdebloat --host <TV-IP> probe
```

Record:

- manufacturer
- model
- device
- board
- Android version
- SDK
- build/fingerprint
- current Home

For Sony BRAVIA, these fields matter because multiple generations can share branding while using different firmware/package layouts.

---

# 10. Look for an existing profile

Profiles live under:

```text
profiles/<vendor>/<model>/
```

For Sony:

```text
profiles/sony/<model>/
```

The skill should first look for:

1. exact model/profile
2. same device/board/firmware family
3. related Sony evidence

It should **not** use a profile just because the TV says Sony BRAVIA.

## If a matching profile exists

Use it as the starting point, then compare it to the live TV.

Prompt:

```text
Use the tvdebloat skill.

We have an existing profile for this Sony BRAVIA.
Compare it against the live TV.

Show me:
- packages newly installed on the TV,
- profile packages that disappeared,
- disable packages that came back,
- packages that may need to move to keep,
- new packages that should be reviewed.

Gather evidence before recommending changes.
Do not edit the profile until I approve the proposed diff.
```

## If no suitable profile exists

Continue to discovery.

---

# 11. Discover the live TV

```bash
tvdebloat --host <TV-IP> discover --out discovery.json
```

This creates a package-oriented snapshot used to build a profile.

Discovery does **not** mean every interesting-looking package should be disabled.

The operator/skill should classify relevant packages as:

- `disable`
- `keep`
- `review`

When uncertain, use `review`.

---

# 12. Build a candidate profile

If no profile exists:

```bash
tvdebloat profile-init \
  --name "Sony BRAVIA <MODEL> Office Profile" \
  --vendor sony \
  --model <MODEL> \
  --from discovery.json
```

This creates:

```text
profiles/sony/<model>/
├── profile.toml
└── NOTES.md
```

It begins as:

```toml
status = "candidate"
```

The profile contains:

```toml
[packages]

disable = []
keep = []
review = []
```

The exact contents are populated/refined from discovery and operator evidence.

---

# 13. Gather evidence like a human operator

For every package under consideration, the skill should behave as if an experienced operator were manually investigating it.

It should:

1. confirm the package is actually installed;
2. check whether it is enabled/disabled;
3. inspect relevant package details/permissions/services/handlers;
4. check whether it is involved in:
   - Home
   - Settings
   - HDMI/input/tuner
   - remote
   - Bluetooth
   - Wi-Fi/setup
   - voice/microphone
   - required apps;
5. compare exact-model/device knowledge if available;
6. ask the operator to physically test anything software cannot prove;
7. record important results in `NOTES.md`.

Package names alone are not enough evidence.

## Decision meanings

### keep

Use when the package is required, protected, or disabling it risks required TV functionality.

### disable

Use only when evidence supports removing it and the pilot passes the relevant tests.

### review

Use when:

- its purpose is uncertain;
- evidence conflicts;
- physical testing has not happened;
- the package looks optional but is not yet proven safe.

---

# 14. Edit an existing debloat list

If you want the skill to maintain the list:

```text
Use the tvdebloat skill.

Compare this live Sony BRAVIA against:
profiles/sony/<model>/profile.toml

Do not edit anything yet.

Show me a proposed diff with:
1. add to disable
2. remove from disable / move to keep
3. add to or keep in review

For every package, explain the evidence.

If software cannot prove a TV behavior, ask me to test it physically.

After I approve the diff:
- make only the approved edits,
- update NOTES.md,
- treat meaningful changes as requiring pilot revalidation.
```

---

# 15. Preview the profile

Preview is required before mutation.

```bash
tvdebloat --host <TV-IP> provision profiles/sony/<model>/profile.toml
```

Without `--apply`, this should be preview-only.

Review:

- exact packages to change
- already-disabled packages
- missing packages
- warnings
- device/profile match

If anything is unexpected, stop and investigate.

---

# 16. Approve the pilot change

The skill should show you the proposed change and wait for explicit approval.

An approval can be as simple as:

```text
I reviewed that diff. Apply it to this pilot TV.
```

Do not treat previous general permission as approval for a new package diff.

---

# 17. Apply to the pilot

After approval:

```bash
tvdebloat --host <TV-IP> provision profiles/sony/<model>/profile.toml --apply
```

TVDebloat should capture backup/recovery information before changing package state.

Do not begin deploying the profile to other TVs yet.

---

# 18. Physically test the TV

ADB command success does not prove the TV still works correctly.

The operator should physically test:

- Home
- HDMI 1/2/3 or required inputs
- input switching from the remote
- remote navigation/buttons
- Settings
- Ethernet/Wi-Fi
- Bluetooth if required
- casting if required
- required office apps
- volume/mute
- sleep/wake
- reboot

Tell the skill what happened.

Example:

```text
Pilot result:
- Home: pass
- HDMI 1: pass
- HDMI 2: pass
- remote: pass
- Settings: pass
- Ethernet: pass
- office app: pass
- volume/mute: pass
- sleep/wake: pass
- reboot: pass
```

The skill should write meaningful findings to `NOTES.md`.

## If something breaks

Say exactly what broke.

Example:

```text
After the pilot change, HDMI 2 no longer opens.
Stop further changes and help me identify which package caused it.
```

The skill should:

1. stop additional risky changes;
2. preserve recovery state;
3. help restore/re-enable the relevant package(s);
4. have you retest;
5. move the unsafe package to `keep` or `review`;
6. record the failure/recovery in `NOTES.md`.

---

# 19. Reboot and check drift

After the TV passes the immediate tests, reboot it.

Then run:

```bash
tvdebloat --host <TV-IP> drift profiles/sony/<model>/profile.toml
```

Check whether:

- packages returned;
- packages disappeared;
- package state changed unexpectedly.

Retest important physical functions after reboot.

---

# 20. Promote the profile

Only when the pilot has passed:

- automated checks;
- physical checks;
- reboot;
- drift review.

Then:

```bash
tvdebloat profile-promote profiles/sony/<model>/profile.toml
```

This moves the profile from:

```toml
status = "candidate"
```

to:

```toml
status = "validated"
```

Do not promote because "the commands returned success."

---

# 21. Deploy to additional matching TVs

For another TV of the same model/compatible firmware:

```bash
tvdebloat --host <TV-IP> preflight profiles/sony/<model>/profile.toml
```

A mismatch should stop deployment.

If preflight matches:

```bash
tvdebloat --host <TV-IP> provision profiles/sony/<model>/profile.toml --apply
tvdebloat --host <TV-IP> verify
```

For a large fleet, each device should still have:

- preflight
- profile-match check
- apply result
- verify result
- failure/review status

Parallel fleet tooling can be added later without weakening those checks.

---

# 22. Restore a TV

If required TV functionality breaks or you need to undo TVDebloat changes:

```bash
tvdebloat --host <TV-IP> restore profiles/sony/<model>/profile.toml
```

Then reboot and physically retest the TV.

Tell the skill what happened so the profile can be corrected.

---

# 23. Report a TVDebloat bug or new device behavior

Use the skill:

```text
Use the tvdebloat skill.

Something unexpected happened during the pilot.
Stop additional state-changing work.
Rerun preflight, inspect recovery state, and help me restore if required.

Then:
- record the device-specific finding,
- update the profile/NOTES if appropriate,
- add a regression test if the behavior can be automated,
- prepare a redacted TVDebloat bug report if this is a tool defect.
```

Do not include:

- IP addresses
- Wi-Fi credentials/SSIDs if sensitive
- MAC addresses
- serial numbers
- accounts
- passwords
- tokens
- ADB private keys

---

# 24. Finish the session

When you no longer need debugging access:

- close/disable network or wireless debugging unless the deployment intentionally requires it;
- keep the validated profile and notes in the repository;
- keep local recovery/backups private;
- commit profile improvements after reviewing them.

The end state for a successful new model should look like:

```text
profiles/sony/<model>/
├── profile.toml   ← validated package decisions
└── NOTES.md       ← evidence and pilot results
```

The next matching Sony BRAVIA should then be much simpler:

```text
preflight → match → apply → verify
```

---

# Quick prompt: first Sony BRAVIA

If you do not want to read the entire runbook before starting, open the repo in Codex/ChatGPT and paste:

```text
Use the tvdebloat skill.

We are onboarding our first Sony BRAVIA.

Assume I know nothing about this process.
Guide me one step at a time from workstation setup through:
- ADB setup/connection,
- TV identification,
- preflight/probe,
- profile lookup,
- discovery if needed,
- package evidence gathering,
- profile creation/editing,
- preview,
- pilot approval/apply,
- physical validation,
- reboot/drift,
- validation.

Ask me to perform physical checks whenever you cannot prove something remotely.
Record useful evidence in the TV profile/NOTES.
Do not make state-changing changes until I approve the exact proposed diff.
```

For more skill-specific prompt recipes, see [SKILLS.md](SKILLS.md).

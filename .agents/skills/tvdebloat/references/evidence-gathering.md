# Evidence gathering

Use this reference whenever TVDebloat is deciding what a package does, whether it belongs in disable/keep/review, or whether a profile change is safe.

The goal is to reproduce the process a careful operator would follow manually.

## Rule

Do not infer a package's purpose from its name alone.

Gather evidence from the live TV first, then ask the operator to verify any behavior that cannot be proven from ADB.

## Evidence workflow

For each package under review:

1. Confirm the package is installed on the exact TV.
2. Record whether it is currently enabled or disabled.
3. Inspect package details, permissions, services, receivers, activities, and handlers where useful.
4. Check whether it is involved in:
   - Home
   - Settings
   - HDMI/input/tuner
   - remote keys
   - Bluetooth
   - network/Wi-Fi/setup
   - voice/microphone
   - required office applications
5. Compare with exact-model or same-board TVDebloat notes when available.
6. If evidence is still ambiguous, keep the package in review.
7. If a test change is approved, change one small group at a time.
8. Ask the operator to physically test the relevant TV functions.
9. Record the result in NOTES.md.
10. Only move a package into disable when the evidence and pilot validation support it.

## Useful read-only commands

Prefer the smallest relevant command rather than dumping everything.

Examples:

```bash
adb shell dumpsys package <package>
adb shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
adb shell cmd package query-activities --brief -a android.settings.SETTINGS
adb shell cmd package query-activities --brief -a android.intent.action.VIEW -t vnd.android.cursor.item/channel
adb shell pm list packages --user 0
adb shell pm list packages -d --user 0
adb shell settings get secure voice_interaction_service
adb shell settings get secure assistant
adb shell dumpsys wifi
```

Use equivalent TVDebloat commands when available.

## Physical/operator evidence

The agent cannot prove many TV behaviors remotely.

Ask the operator to test the specific thing affected by the package, for example:

- Press Home.
- Open HDMI 1/2/3.
- Change input with the remote.
- Open Settings.
- Pair/use Bluetooth if required.
- Launch the required office app.
- Sleep/wake the TV.
- Reboot the TV.
- Confirm network connectivity.
- Confirm volume/mute controls.

Do not mark these as passed unless the operator reports that they passed.

## Recording evidence

When the operator gives a result, write it into the profile's NOTES.md in a useful form.

Example:

```text
2026-10-28 — Pilot test
Package: com.vendor.example
Action: disabled for pilot
Result:
- Home: pass
- HDMI inputs: pass
- Remote: pass
- Settings: pass
- Network: pass
- Reboot: pass
Decision: move from review to disable
```

For a failure:

```text
Package: com.vendor.inputservice
Action: disabled for pilot
Result: HDMI 1/2 stopped opening
Recovery: package re-enabled; reboot restored input switching
Decision: keep
```

## Confidence rule

Use these decision levels:

- **keep** — required, protected, or disabling caused/risks loss of required functionality
- **disable** — evidence supports removal and the pilot passed relevant physical tests
- **review** — insufficient evidence, uncertain behavior, or no pilot result yet

When uncertain, choose review.

## Shared reference upkeep

Keep results as reusable technical findings, not personal setup history.
Use `docs/knowledge-maintenance.md` from the repository root. Replace disproven
instructions in the current task section; keep a concise failure/resolution and
its version scope. Private bindings, content and recovery evidence stay outside
the shared repository.

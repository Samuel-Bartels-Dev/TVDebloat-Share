# TVDebloat Runbook

## New TV model / first pilot

### 1. Connect

Enable the TV's supported debugging mode and place the workstation on the same trusted network.

```bash
python -m pip install -e .
tvdebloat --host <TV-IP> preflight
```

Fix all failed preflight checks before continuing.

### 2. Probe

```bash
tvdebloat --host <TV-IP> probe
```

Record the exact manufacturer, model, device, board, Android version, SDK, fingerprint, and current Home.

### 3. Discover packages

```bash
tvdebloat --host <TV-IP> discover --out discovery.json
```

This captures a classification-oriented package inventory for profile authoring.

### 4. Build a candidate profile

```bash
tvdebloat --host <TV-IP> profile-init \
  --name "ASUS Office Profile" \
  --vendor asus \
  --model <model> \
  --from discovery.json
```

The generated profile begins as `candidate`.

Review each proposed/unknown package with the operator. Do not guess.

### 5. Preview

```bash
tvdebloat --host <TV-IP> provision profiles/asus/<model>/profile.toml
```

No package state changes occur.

### 6. Pilot apply

After approval:

```bash
tvdebloat --host <TV-IP> provision profiles/asus/<model>/profile.toml --apply
```

### 7. Physical validation

Verify:

- Home
- HDMI/input switching
- remote
- Settings
- network
- Bluetooth if required
- required office apps
- sleep/wake
- reboot

### 8. Reboot + drift

```bash
tvdebloat --host <TV-IP> drift profiles/asus/<model>/profile.toml
```

### 9. Promote

Only after the pilot passes:

```bash
tvdebloat profile-promote profiles/asus/<model>/profile.toml
```

The profile becomes `validated`.

---

# Fleet deployment

For each additional TV of the same model:

```bash
tvdebloat --host <TV-IP> preflight profiles/asus/<model>/profile.toml
tvdebloat --host <TV-IP> provision profiles/asus/<model>/profile.toml --apply
tvdebloat --host <TV-IP> verify
```

A live-device mismatch blocks automatic apply.

For 100+ TVs, build inventory/parallel orchestration around the same validated profile rather than weakening per-device preflight.

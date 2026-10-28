# Sony BRAVIA example notes

> EXAMPLE ONLY — this is not evidence for a real Sony model.

## Device identity

- Manufacturer: Sony
- Model: BRAVIA-EXAMPLE-NOT-REAL
- Device: example-device
- Board: example-board
- Android: 12
- SDK: 31
- Firmware/fingerprint: sony/example/...
- Network used for pilot: Ethernet
- Required functions:
  - Home
  - HDMI 1 / HDMI 2
  - Sony remote
  - Settings
  - network
  - required office application

## Package review

### com.example.sony.promotions

Initial state: enabled

Evidence gathered:
- package appears to provide promotional content only;
- no Home, Settings, input, remote, Bluetooth, or network handlers found;
- operator approved a pilot disable.

Pilot result:
- Home: pass
- HDMI 1: pass
- HDMI 2: pass
- remote: pass
- Settings: pass
- network: pass
- required office app: pass
- reboot: pass

Decision: `disable`

### com.example.sony.inputservice

Evidence gathered:
- package exposes input-related services/handlers.

Decision: `keep`

No disable test performed because the role is required.

### com.example.sony.telemetry

Evidence gathered:
- name/metadata suggests telemetry;
- exact effect is not yet proven;
- no pilot disable performed.

Decision: `review`

## Example pilot history

### 2026-10-28 — initial candidate

- Discovery captured.
- Required TV functions documented.
- One synthetic promotional package approved for pilot.
- Input/remote packages retained.
- Telemetry/recommendation/voice packages left in review.

### 2026-10-28 — pilot validation example

Physical checks reported by operator:

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

Drift: no unexpected package-state changes.

Example next step: promote only if this were a real profile with real evidence.

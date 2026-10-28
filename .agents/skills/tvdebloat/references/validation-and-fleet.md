# Validation and fleet rollout

## Pilot validation

After pilot apply, physically verify:

- Home
- HDMI/input switching
- remote
- Settings
- network
- Bluetooth if required
- required office apps
- volume
- sleep/wake
- reboot

Then run drift.

A candidate profile stays candidate until the pilot passes.

## Profile changes

Any meaningful package-list change to a validated profile requires pilot revalidation before broad rollout.

## Fleet rollout

For each TV:

1. preflight with the validated profile
2. require a compatible live-device match
3. apply
4. run automated verify
5. log result

Do not weaken per-device preflight for speed.

For large fleets, parallelize orchestration around the same validation contract rather than bypassing it.

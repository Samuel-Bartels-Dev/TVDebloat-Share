# Package classification

Classify each relevant package into one of:

- disable
- keep
- unknown/review

## Evidence priority

1. live package/service/permission behavior on the exact TV
2. existing TVDebloat evidence for exact model/firmware
3. same board/device-family evidence
4. vendor-family evidence
5. package-name hints

Package-name hints alone are not enough to add a package to disable.

## Strong keep indicators

- Android core/framework
- package installer / permission controller
- Settings
- current Home
- TV input / HDMI / tuner
- remote / Bluetooth
- network / Wi-Fi provisioning
- setup services when Wi-Fi ownership is unclear
- required office applications

## Typical review candidates

- recommendations
- promos
- telemetry
- analytics
- feedback
- ACR
- vendor content services
- optional streaming apps

Each disable decision should be explainable in NOTES.md when it is not obvious.

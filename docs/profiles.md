# TVDebloat profiles

Profiles are the repeatable unit of deployment.

## Directory shape

```text
profiles/
  asus/
    <model>/
      profile.toml
      NOTES.md
```

## Example

```toml
name = "ASUS Example Office Profile"
status = "candidate"

[device]
manufacturer = "ASUS"
model = "ExampleTV"
device = ""
board = ""
android = "12"
sdk = "31"
fingerprint_contains = ""

[packages]
disable = [
  "com.vendor.recommendations",
  "com.vendor.analytics",
]

keep = [
  "com.vendor.inputservice",
  "com.vendor.remoteservice",
]

notes = [
  "Pilot validation required before fleet deployment.",
]
```

## Rules

- Candidate profiles are never mass-applied automatically.
- A validated profile must record the exact tested device/firmware family.
- Unknown packages stay out of `disable` until reviewed.
- Required TV functions belong in `keep`.
- Package comments/knowledge belong in `NOTES.md` or structured metadata, not upstream PR links.

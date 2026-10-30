# LG webOS discovery and launcher planning

Read `docs/webos.md` from the repository root for the CLI/schema and provenance.
For OLED65C9PUA / 03.50.31 / webOS 4.5.0, also read
`docs/lg-c9-hearth-observations.md`: use its task-specific procedures for
wallpaper, ribbon behavior, screensaver, font, tiles and Home-only integrations.
It records reusable mechanics, tested scope and limitations, not a prior user's
configuration. Correct outdated guidance in place using
`docs/knowledge-maintenance.md`. Do not generalize these rooted-TV findings to
other firmware; native TVDebloat writes remain unsupported.

Identify the physical TV's OS before transport selection. If it is webOS, never
use ADB, Android `pm`, Android profiles, or the Android provisioning engine.
Firmware/software version is not the webOS platform version. Missing platform
information stays unknown. Use the existing trusted SSH account/port/key; do not
root, enable developer mode, deploy Glasshouse/Homebrew, accept unknown host keys,
install a daemon, or change firmware as an implicit prerequisite.

Start with `python -m tvdebloat --platform webos --host <TV-IP> preflight`, then
probe/discover only. Current native support is read-only for every firmware.
An SSH permission error is not proof of unsupported hardware or an empty app list.
If access is unavailable, ask for the operator's access method; do not guess it.

Create a webOS candidate only from actual discovery; keep separate app IDs,
launch-point IDs, service decisions and privacy decisions. Unknown apps stay in
review. Service inventory is not collected yet. Never copy an upstream optional
service catalog into disable. In particular preserve tvdataexchanger and
alwaysready because upstream recorded picture failures when disabled.

Launcher order must preserve every unique discovered launch point. Generate the
exact saved preview; explain blocked actions and supported capabilities. Native
app hiding/service disabling/Home replacement are not implemented. Glasshouse
Home rejects webOS 4; C9 dashboard reports do not validate a replacement launcher.
Do not promise a custom dashboard from a tile-reordering feature.

Before any future supported mutation, show before/after values, exact commands,
evidence, recovery and plan digest; obtain explicit approval of that plan.
Candidate pilot acknowledgement is additional. Preserve the local recovery
journal before each write, stop on uncertain results, and preview recovery for
separate approval. Never treat development authorization as TV-change approval.

Ask the operator to confirm model/platform/firmware and required HDMI, apps,
audio/CEC, networking and remote behavior. After an approved change, collect
Home/Back, HDMI, CEC/ARC audio, apps, Settings, sleep/wake and cold-boot results.
Request approval before rebooting. Record observations, uncertainty and recovery
in NOTES; never claim physical validation from command success or simulated tests.
Keep credentials, network identifiers and raw private responses out of shared
profiles, previews, notes and logs.

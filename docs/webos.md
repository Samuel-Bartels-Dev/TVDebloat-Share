# Independent LG webOS workflow

TVDebloat now has native webOS discovery and launcher planning. It uses your
existing SSH access and the TV's Luna bus; it does not need ADB or Glasshouse.
The current native adapter is **read-only on every firmware**. The approval and
recovery engine is exercised with a simulated TV, but no native firmware write
contract has been validated. This is not a working replacement launcher or a
validated debloat list.

## Access and identity

First read the physical TV's model, software version and OS name. Firmware and
webOS platform version are different fields. Do not derive one from the other.
Existing trusted SSH access is required. A developer-mode account may have less
permission than root; a refused Luna request is a failed check, not an empty TV.

Use the SSH account, port and existing key that actually belong to your TV.
TVDebloat does not enable Developer Mode, root the TV, install Homebrew Channel,
accept host keys, guess passwords, install a daemon or change firmware. Verify
the TV's SSH host fingerprint independently before adding it to your SSH trusted
hosts. Password prompts are disabled; arrange your existing key/agent first.
The negotiated server-key fingerprint is hashed into the private target binding;
key changes stop reads. OpenSSH must report the SHA-256 server-key fingerprint.
Verbose connection logs are used internally for that field and are never exported.

From the repository, examples (replace the host; all options precede the command):

```powershell
python -m tvdebloat --platform webos --host TV-IP preflight
python -m tvdebloat --platform webos --host TV-IP probe
python -m tvdebloat --platform webos --host TV-IP discover --out work/webos-discovery.json
```

Optional SSH settings: `--ssh-port 9922 --ssh-user root --ssh-key PATH` (these
are examples, not a promise that port 9922 is configured). IPv4 and DNS hosts are
supported; IPv6 endpoints are not yet supported. Preflight `ready` means identity
and inventories were readable; `ready_for_write` is a separate capability and
is false for the current native adapter. Missing platform version is reported
as unknown while useful inventory reads may continue.

Reads use fixed commands: system properties (`modelName`, `firmwareVersion`,
`boardType`, `sdkVersion` requested; only model/firmware exported), release files,
`listApps`, and `listLaunchPoints`. No subscription, remote shell parameter from a
profile, write endpoint, environment dump or whole-settings backup is allowed.
Output strips serials, MACs, app titles, bookmark URLs/parameters, icon paths and
credentials. Local discovery still reveals installed app IDs: keep it private.

## Candidate profile and preview

After discovery, initialize the exact observed model:

```powershell
python -m tvdebloat --platform webos profile-init --vendor lg --model ACTUAL-MODEL --name "Office webOS" --from work/webos-discovery.json
```

This creates `profiles/lg/<model>/profile.toml` and preserves existing NOTES.
Apps start in review; executable changes start empty. The webOS schema is
separate from Android packages and cannot be used through the Android engine.

```toml
schema_version = 1
platform = "webos"
name = "Synthetic example only"
status = "candidate"

[device]
manufacturer = "LG"
model = "SyntheticPanel"
firmware = "01.02.03"
webos = "4.9.0"

[apps]
hide = []
keep = []
review = []

[launcher]
order = []

[services]
disable = []
review = []
```

`launcher.order` is either empty (no change) or the complete permutation of the
discovered launch-point IDs. App IDs are not launch-point IDs: multiple bookmarks
or HDMI entries can share an app. Existing points must all be preserved.

```powershell
python -m tvdebloat --platform webos --host TV-IP --plan work/webos-plan.json preview profiles/lg/ACTUAL-MODEL/profile.toml
```

The preview reports exact before/after ordering, individual moves and inverse
moves, target and profile fingerprints, blocked decisions, and its digest.
App hiding and service disabling are research/preview entries only; they block
execution. Core apps and unknown apps cannot be hidden. Replacement Home,
uninstall, privacy writes and startup hooks are unsupported, not silently skipped.
Service inventory is explicitly not collected in this version; an empty list
does not mean the TV has no services. `verify` reports readability and pending
physical validation. `drift PROFILE` recomputes the current proposed ordering;
it does not promote or certify a profile. WebOS profile promotion is unsupported.

## Approval and recovery contract

For a future firmware-verified adapter, applying an approved move plan requires
`--plan FILE --approve-plan EXACT-DIGEST --pilot --state-dir PRIVATE-DIRECTORY`
before `provision PROFILE --apply`. The candidate acknowledgement (`--pilot`)
does not replace approval of the exact displayed diff. On today's adapter this
still fails closed; no flag or profile field can grant native write capability.

Before any supported move the engine rechecks exact identity, firmware, platform,
target, profile bytes, capability and full launcher snapshot. It atomically saves
a unique journal before each write and verifies readback after each move. A
disconnect or ambiguous result stops the sequence and preserves a pending record.
It never automatically retries, rolls back, restarts Home or reboots.

`restore JOURNAL` defaults to an inverse preview. An untampered plan with a verified
completed action prefix and unchanged target/state is required. Applying recovery needs that preview's
digest, `--state-dir`, and `restore JOURNAL --apply`. A clean stop between moves can
restore its completed prefix. Pending/uncertain writes require manual evidence
reconciliation; no blind recovery is offered.

Readback is not physical validation. The operator must test Home/Back, apps,
required HDMI ports, CEC/ARC audio, remote, Settings, sleep/wake, and eventual cold
boot. Ask separately before any reboot or other TV change. Preserve results in
the profile's NOTES and retain candidate status until the evidence is complete.

## Source findings and C9 boundary

Inspected Glasshouse revision:
[`ea4842e21e572ae67bf0958d03c833f124803fc8`](https://github.com/rorygallagher2024/glasshouse/tree/ea4842e21e572ae67bf0958d03c833f124803fc8).
Independent implementation, not a port of its server or dashboard:

| Source | Finding used |
|---|---|
| `server/lib/luna.js` | Fixed one-shot Luna transport; settings service names differ by generation (not needed by our current reads) |
| `server/lib/telemetry.js` | System properties and release-file platform detection; separate firmware from platform |
| `server/lib/apps.js` | Distinguish app inventory, launch points, tile hiding and uninstall; protect core/recovery apps |
| `server/lib/services.js` | Service disabling includes persistent hooks; `tvdataexchanger` and `alwaysready` were retired after video failures |
| `server/lib/home.js` | Home takeover explicitly rejects webOS 4; dashboard compatibility is not Home compatibility |
| `docs/development/TV-RESEARCH.md` | `moveLaunchPoint` takes launchPointId and zero-based position; visual Home may need a later refresh |

The operator's OLED65C9PUA and software 3.50.31 are observations, not live
compatibility evidence. Do not run Android commands on it or infer it is rooted.
Do not copy newer-webOS Glasshouse Home takeover onto it. A separate custom
launcher installation needs its own source review, compatibility checks, exact
install/recovery diff and explicit approval.

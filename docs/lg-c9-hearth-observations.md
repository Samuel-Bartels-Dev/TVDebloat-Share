# LG C9 / Hearth customization reference

Scope: OLED65C9PUA, firmware 03.50.31, webOS 4.5.0, Hearth 1.2.0.
These findings come from a single tested installation. Recheck installed versions
and bytes before reuse. Native TVDebloat remains read-only; the rooted procedures
below are separately authorized customizations, not executable native profiles.
Last reconciled: 2026-10-30. This is a technical reference, not a household log.

## Choose the task

| Task | Start here | Known limitation |
|---|---|---|
| Wallpaper or slideshow | Wallpaper and local images | Home-only, not the native screensaver |
| Home button or LG ribbon | Home redirection and ribbon options | Reactive helper can show a brief ribbon |
| Native photo screensaver | Native screensaver | Exact stock QML and lifecycle must match |
| Clock font | Clock typography | Font licensing and entry-file updates |
| Tile order, visibility or artwork | Hearth configuration and tile artwork | Hidden does not mean uninstalled |
| Home-only card | Home-only integrations | OLED shift and Settings retain Home DOM |
| Modern dashboard on old browser | Read-only dashboard images | Requires a separate renderer |

## Common prerequisites and recovery

Use the existing pinned SSH access; do not root, enable developer mode, open
Telnet, change firmware or install new access as an implicit prerequisite.
Identify the TV, firmware, webOS and installed Hearth/helper versions. Inventory
apps and launch points, and establish the required remote, input, audio and
Settings behavior privately before changing anything.

Hearth app ID is `tld.my.customlauncher`; its directory is
`/media/developer/apps/usr/palm/applications/tld.my.customlauncher`.
Configuration is the JSON string at localStorage key `customlauncher-config-v1`.
Back up that exact string privately, parse a copy, merge only requested fields,
and compare the current raw string with the saved value immediately before
writing. Stop on drift. Read back the result; reload only Hearth when needed.
Preserve unknown fields, installed apps, native Home, root hooks and OLED safety.

For file edits, privately back up exact current bytes, guard their hash, stage
and verify the replacement, then replace atomically. Record rollback identity
privately, not a particular household's installed-file hashes in this reference.
Show the scoped diff and obtain its approval before applying it. A recovery
operation also needs a concrete inverse preview. Revalidate entry-file additions
after a Hearth update; never restore a stale whole-file backup over newer work.

## Wallpaper and local images

1. Identify the chosen image or folder and the current installed picker/schema.
   The inspected picker supports internal storage and USB folders, not arbitrary
   shared-album URLs. Copy only authorized content; keep source URLs and media
   outside the shared repository.
2. Prepare display copies with orientation applied, whole-photo fitting without
   unintended cropping, and metadata removed where appropriate. Preserve originals.
   The inspected slideshow slices a folder to 400 files; split larger collections
   rather than silently omit images.
3. Check free space. Transfer into a new staging directory over pinned SSH, verify
   file counts and hashes, then finalize it. Do not replace an existing folder or
   recursively remove an unknown path.
4. In Hearth Settings, use Wallpaper, select internal storage/USB, then the image
   or the folder's slideshow action. For an automated change, first inspect that
   version's `wallpaper` schema; merge only the requested wallpaper fields.
   Shuffle and interval are selectable. `quietSec` controls idle tile fading;
   change it only if requested, not as part of every wallpaper update.
5. Verify configuration and actual image rotation, readability, idle fade/wake and
   missing-source behavior. A foreground slideshow does not replace LG's system
   screensaver and must not disable native OLED protection.

## Home redirection and ribbon options

Symptom: helper/boot switches are enabled, but Home still leaves the LG ribbon.
On this firmware the ribbon emits `NL_HOME_SHOWN {}` without making
`com.webos.app.home` the foreground app. Helper version 9 selected its foreground
subscription because an LG Home directory existed, so it missed this event.
The release embeds helper 9 while an inspected source tag had helper 7: inspect
installed/release bytes instead of downgrading to a source-tag assumption.

For the inspected helper, the working workaround inserts this after the shebang
of `/media/developer/launcher-homehook/apply.sh`:

```sh
export HOME_APP_DIR=/media/developer/launcher-homehook/.c9-homebar-event-mode
```

The sentinel path must not exist. This selects the helper's existing Home-bar
log branch; it does not rename stock LG Home. Validate shell syntax and restart
only the identified watcher and its subscription children. Preserve its existing
boot link and the independent root-access hook. Check new PID, Home-bar log mode,
actual Home events and foreground app. Do not use broad process-name kills.

Choose the requested behavior explicitly:

- **Retain TV options:** use the original watcher with the Home-bar-mode override.
  Home from another app reaches Hearth; Home while already in Hearth can leave
  LG's ribbon available. This is a valid choice, not a failed customization.
- **Dismiss the ribbon:** after the helper launches Hearth for a Home-bar event,
  recheck that Hearth is foreground, then close only `com.webos.app.home` through
  `com.webos.applicationManager/closeByAppId` with `{ "id": "com.webos.app.home" }`.
  Preserve the helper's stock-Home allow flag. Unknown or other foreground must
  not be closed. Repeatedly launching Hearth alone did not reliably dismiss it.

Both approaches are reactive, so a brief stock-ribbon flash can remain. Do not
promise complete suppression. Do not simulate Back to close the ribbon: with no
ribbon, Back can open Hearth recent apps. Verify Home from an app, Home inside
Hearth, Back in each state and continued access to stock Home/Settings. The
redirection/dismissal variant survived a software reboot on the tested setup;
that does not prove every later variant or a mains cold boot. Test the selected
variant separately after approval. Reverting dismissal means restoring only the
saved watcher, retaining the Home-bar override unless otherwise requested.

## Native screensaver

The inspected `com.webos.app.screensaver` version 2.0.0 uses
`/usr/palm/applications/com.webos.app.screensaver/qml/main.qml`.
A working photo customization used a stock-derived wrapper bind-mounted onto
that exact entry point, retaining the original `ScreensaverMain` service and
lifecycle. Display photos only in normal `Mode_ScreenSaver`; preserve video,
partial and PIG modes. Keep stock visuals until an image is ready and as the
fallback when all images fail.

Review the actual stock QML and mode contract before producing a candidate.
Back up stock bytes privately and test a temporary mount first. A forced test
uses `com.webos.service.tvpower/power/turnOnScreenSaver`; require actual photo
rendering, rotation and remote dismissal, not just a successful Luna reply.
Only after that test, a separately approved guarded webosbrew init hook can
reapply the mount. Guard stock/candidate hashes, source availability and unknown
existing overlays. Do not change idle timeouts, restart the app manager or kill
the native screensaver to force a result.

Tested evidence: forced display rotated and dismissed with an arrow; an installed
hook reapplied its mount after software reboot. Natural idle activation and
mains cold-boot behavior require separate checks. Do not retain earlier claims
that this tested approach is merely undeployed. Recovery unmounts only the
verified target and verifies restored stock bytes; remove an owned startup hook
only through the approved inverse plan.

## Clock typography

Hylia Serif 0.009 loaded on the tested browser. Obtain fonts from their creator
and check the current license; do not bundle a non-redistributable font with the
skill. Add local font/CSS assets and a single stylesheet reference after backup.
Scope selectors to clock time/date/period rather than every label. Confirm the
font loaded, computed families match and on-screen text is readable. Preserve
configuration and other entry-file additions; Hearth updates may replace the
entry file. Restore only the affected reference/assets when undoing it.

## Hearth configuration and tile artwork

Inventory actual app/launch-point IDs. Preserve installed apps when hiding tiles.
Merge `appIds`, `hiddenIds`, `sourceIds` and `tileOrder` only as the requested
layout requires; preserve LG Home and Settings controls. Discover input labels
live instead of assuming a console uses a particular HDMI number. Verify order
and launch behavior on the screen. Avoid overlapping operator and automated
remote input while navigating the store.

A tile can retain old base64 artwork even after its app's icon file changes.
The tested native override is `appEdits[appId].iconData`; preserve all other
per-app edits and configuration fields. Hearth's inspected image-picker flow
center-crops and scales an image to a 128-pixel square PNG data URI, limited to
150,000 characters. Use that native mechanism or an equivalent validated sizing
step; inspect limits after version changes. Save the chosen asset locally,
back up configuration, replace only that app's icon override and reload Hearth.
Verify the rendered tile's image source and successful decode, not just the
uploaded file's hash. Reloading alone did not replace previously cached artwork.

## Home-only integrations

A card can use separate JS/CSS assets with narrow entry-file references. Keep
write credentials off the TV; use a distinct read-only credential in a root-only
helper/config when necessary. Never embed endpoints, keys or note contents in
shared documentation. Use verified HTTPS and explicit unavailable/stale states.

Home may be `screen screen--shift` during OLED shifting. Exact equality with
className `screen` incorrectly hides cards. Permit shift while excluding away,
settings and picker states, and require Home content. Hearth keeps an away Home
screen in the DOM alongside Settings; inspect all screens, not only the first.
Verify actual Settings hides the card and returning Home reveals it. This
Home-only behavior was verified by DOM checks; do not infer global overlays or
reboot persistence from those checks.

## Home calendar feeds

A read-only Home card can fetch a private iCalendar feed directly on the TV,
without a PC relay. Keep the secret URL in a root-owned mode-0600 curl config
inside a mode-0700 directory, accessed by a bounded reader through the existing
Homebrew exec service. Use verified HTTPS and bounded size/time. Keep the full
feed in memory only; cache just the current display window's titles, times,
all-day flags and successful-refresh timestamp. Never publish calendar IDs,
private links, event contents or a user's layout in the shared reference.

Use a reviewed iCalendar library for recurrence, moved/canceled exceptions,
exclusive all-day end dates, multi-day overlap and DST. ICAL.js 2.2.1's ES5
browser build compiled on Chromium 53 but failed during initialization because
Object.entries/fromEntries were missing. Narrow compatible shims resolved it;
verify execution and parsing, not syntax alone. Validate raw TZID parameters
against registered zones before materializing dates: the library can otherwise
silently convert an unknown zone into floating/device-local time.

The inspected TV shell produced an invalid numeric result with a shell-variable
length expression on the feed. Measuring bytes through printf and wc -c worked.
Keep private feed data out of error logs. A failed parse/fetch must preserve the
last-good display and mark it stale, rather than become a fresh empty calendar.
Measure the live clock, Notes and app-row rectangles before placing the card.
Bound visible rows and explicitly count additional events. Test actual Settings
hiding and Home return, including OLED shifting. Native-browser initialization,
recurrence fixtures, HTTPS refresh, empty-feed cross-check and Home/Settings
visibility were verified; overnight rollover and reboot remain separate checks.

## Read-only dashboard images

The native browser could not parse JavaScript used by Grafana 13.2.4. A tested
alternative renders actual dashboards on a capable PC and publishes bounded,
hashed image pages to a separate ES5 TV app. Keep credentials on the PC, use a
Viewer identity, authenticate the renderer and bind its HTTP services to loopback.
Commit image generations atomically and retain the last good images with a
capture timestamp and stale warning. Back should return to Hearth. Dashboard
rendering, paging, automatic refresh and on-screen readability were verified;
new sign-in/reboot persistence still needs its own test.

A forced SSH HTTP helper must not half-close upstream before authentication
completes: this yielded misleading Unauthorized replies with canceled contexts.
Grafana's observed modern dashboard DTO endpoints need exact UID-scoped read
allowlisting; unknown writes stay denied. This is an optional pattern, not a
requirement to install Grafana or a PC renderer for other customization tasks.

## Silent Luna replies

On the tested firmware a Luna CLI request can exit silently when stdin is already
closed. Keep input open for a bounded request and set the CLI timeout; require an
actual parsed reply. An empty response is neither an empty app list nor proof a
mutation failed. Inspect current state before retrying an installation.

## Updating this reference

Follow [reference maintenance](knowledge-maintenance.md). Replace contradicted
instructions in the relevant section; retain only useful failure symptoms and
their working resolution. Keep model/version scope and evidence limitations.
Do not append personal setup history or treat this installation as a default.

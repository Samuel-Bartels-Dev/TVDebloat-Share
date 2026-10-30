# LG C9 / Hearth operator observations

## Read-only Grafana image viewer — October 30, 2026

On this C9 firmware, the native browser could not parse JavaScript used by
Grafana 13.2.4. A separate ES5 webOS app was installed instead: an authenticated
Windows renderer captures the actual dashboards and publishes bounded PNG pages
over existing pinned SSH. The TV stores images and timestamps, with no Grafana
token or sign-in. This is a separately approved rooted-TV customization, not a
native TVDebloat write capability.

Four dashboards rendered real metric queries and produced nine pages. Native
TV checks verified all four tabs loaded full-size images, page-down selected
the next page, and Back returned to Hearth. A stale indicator appeared for an
old capture; scheduled publication then refreshed the TV cache. The PC services
bind only to loopback and use a dedicated Viewer identity. All 95 pre-existing
app IDs remained installed; Hearth entrypoint and Home-helper hashes were
unchanged. Only one app tile was added to Hearth configuration, backed up before
the merge. Physical readability/remote acceptance and new reboot/sign-in
persistence checks remain pending; no reboot occurred for this change.

Two transport findings matter for reproducing this approach. A forced SSH
helper must not half-close the upstream HTTP socket before Grafana completes
authentication: this caused a misleading Unauthorized response with a canceled
request context. Also, this TV's Luna CLI can exit silently when stdin is already
closed. Hold stdin open for a bounded request and require an actual response
before deciding an app is absent or retrying an installation. Grafana's modern
dashboard DTO reads must be allowlisted for the observed version and exact
dashboard IDs; unknown writes should stay denied.


## Home-only family notes installed — October 30, 2026

After exact preview and operator approval, Hearth received a read-only notes
card through two added entry-file references and separate JS/CSS assets. A
root-owned, mode-0600 curl configuration holds a distinct read-only service key;
the editing password is not on the TV or in browser assets. Verified HTTPS is
used without disabling certificate checks. Home refreshes at 15 seconds; the
card displays four newest notes. Existing Home ribbon behavior, wedding-photo
wallpaper, Hylia clock font and selected app tiles were retained. No reboot or
startup-hook change occurred. Entry-file SHA256 is
`058e92fb05260cb8963ba1133af30a4b05e99ea0e96f6490a6a3a8e6a9b7cc9e`.

Live discovery found Home can have `screen screen--shift`, so equality with
className `screen` incorrectly hides additions during OLED pixel shifting.
The corrected gate permits shift but rejects away/settings/picker classes and
requires Home clock/rows. Hearth keeps an away Home screen in the DOM while a
separate Settings screen is active: test all screens rather than assuming the
first screen is Settings. Installed notes script SHA256 is
`071ae9e2d8e88010fcd58105504687741c507e3f59d18e95f75527f2950dae44`.

Live DOM/readback verified visible Home plus a successful empty-board response,
hidden card while actual Hearth Settings was active, and Home visible again
after reloading only Hearth. Hosted tests verified phone add/read/delete and
TV-key write denial; disposable test notes were removed. Physical operator
acceptance, display layout with real family notes and reboot persistence remain
unverified. Restore the private pre-change index and reload Hearth to deactivate
the customization. Hearth updates may replace this entry file. No private
family URL, credentials or network identifiers belong in the shared model notes.


## Requested streaming menu completed

The operator installed Plex and Crunchyroll through LG Content Store. Live
inventory verified Plex as cdp-30 and Crunchyroll as com.crunchyroll.webapp.
Hearth's order was saved and read back as HDMI4/PS5, Netflix, Hulu, Plex,
Crunchyroll, followed by LG Home, System Settings and Hearth Settings. Other
tiles remain hidden only in Hearth. Photos, clock configuration, Hylia entry
file and Home-helper hashes were preserved. Hearth was opened for inspection;
physical menu confirmation remains pending. Earlier missing-app notes are
historical. During store navigation, concurrent operator input changed the
selected listing; automated keys were paused rather than assuming focus.

## Native screensaver reboot persistence verified

After a separately approved software reboot, a changed kernel boot ID and
pinned key-only root SSH confirmed the TV restarted. The photo screensaver
bind mount was already present without manually running the hook, and its
candidate/startup-hook hashes matched. Hearth's Home-bar watcher also started
automatically; the selected stock-ribbon behavior, Hylia font and entry-file
hashes, all installed app IDs and 72 Highlights photos were preserved. Normal
Telnet remained absent. Natural idle activation and post-reboot on-screen
behavior still await operator confirmation; this was not a mains cold boot.

## Photo screensaver startup hook installed

After explicit approval, /var/lib/webosbrew/init.d/60-c9-photo-screensaver was
installed root-owned and executable. SHA256:
`51ddba98b471ba1d1bb28740b04f93ff4b53cd7604d78b25bf1e01887bab80a7`.
Shell syntax, installed hash and execution against the already active verified
overlay passed. Root SSH and Hearth watcher hashes were unchanged. No reboot
or idle-timeout change occurred. Automatic reapplication after reboot remains
unverified until a separately approved reboot; do not infer persistence success
from successful execution against the existing overlay. Earlier descriptions
of the overlay as temporary now refer to its initial test phase, before this
startup hook was installed. Guard failure leaves the original startup state
alone rather than applying an unknown replacement.

## Native photo screensaver physical result

The operator confirmed the forced native screensaver test displayed wedding
photos, changed after about 30 seconds, and dismissed normally with an arrow
button. Read-only follow-up confirmed the temporary overlay still matched the
tested candidate hash. Natural idle activation and reboot persistence have not
been independently confirmed. A guarded 60-c9-photo-screensaver startup hook has
been prepared locally, not installed: it checks the source/stock hashes, photo
availability and absence of an unknown overlay before applying the same mount.
It does not launch the screensaver or change idle/power/OLED settings.

## Curated Hearth menu

The operator requested PS5, Netflix, Hulu, Plex, Crunchyroll and settings controls.
Both listApps and listLaunchPoints confirmed Plex and Crunchyroll were absent.
The available menu was trimmed to HDMI4/PS5, Netflix and Hulu, retaining LG Home,
System Settings and Hearth Settings. Other installed app tiles were hidden only
inside Hearth; exact pre-change config was backed up privately. No apps were
uninstalled. Readback verified config, unchanged installed-app set and unchanged
Hylia entry-file/Home-helper hashes. Photos and font settings were preserved.
Plex/Crunchyroll installation and final ordering remain outstanding; do not
report their tiles as present or confuse hidden tiles with removed apps.

## Hylia Serif clock customization

The operator approved a clock/date-only Hylia Serif 0.009 customization. Font
was obtained from its creator, Artsy Omni, whose site prohibits resale; do not
bundle the font into a shared profile or distributable skill archive.
Font SHA256: `49d40e1b73bdc1c3a89c8e59cb03b107f69191e293d4e301eede9988c5925566`.
New local font/CSS files were added within Hearth, and one local CSS link was
inserted into index.html after private backup and before-hash checks. App bundle
and localStorage were unchanged. CSS targets clock time/date/period only.
Hearth was reloaded; its browser reported the font loaded and computed clock/date
families matched. Saved settings and Home/root/native-screensaver hashes were
unchanged. On-screen readability remains pending confirmation. Hearth updates
may overwrite the entry-file customization; restore the saved index to undo.

## Native screensaver temporary test applied; result pending

The operator approved the exact temporary Highlights test. The stock entry
point was backed up privately and a bind mount of candidate SHA256
`555c567229b758df2b6d34694489c8f7628dcc7c806646563763745e3154d659`
was applied and verified at main.qml. LG's turnOnScreenSaver action returned
success. No photo-ready or all-images-failed log marker was observed in the
initial bounded log sample, so rendering is not proven. Operator confirmation
is pending; do not claim fireworks have been replaced successfully yet.
No boot hook, timeout change, app-manager restart or reboot was performed.
Root and Hearth hook hashes were unchanged. This temporary mount remains until
explicitly unmounted or cleared by reboot; it is not persistent configuration.

## Native photo-screensaver candidate: not deployed

Read-only discovery confirmed stock com.webos.app.screensaver 2.0.0 is a QML app
whose main.qml entry point exists at the Homebrew overlay target. Stock SHA256:
`296e56540b13ded0025263b997db0f134b477218e38e103adab180b9fc49f7b5`.
Reviewed webosbrew/custom-screensaver revision
`90666c19112ec77d6c2b1b84ae7db7d914285e92` uses a temporary bind mount at that
path and a tvpower/power/turnOnScreenSaver test action. Its stock sample is a
bouncing logo, not a photo slideshow or C9 validation.

A stock-derived candidate wrapper was prepared locally, retaining the original
ScreensaverMain service/lifecycle component. Photos overlay only the normal
Mode_ScreenSaver state with no video, partial, or PIG mode; the stock visual
remains the fallback until an image is ready or after all images fail. Local
tests passed for shuffle permutations/no-repeat boundaries, mode guards and
72 local photo paths. No QML compiler was found on TV, so actual QML engine,
image display, remote dismissal and natural idle activation are unvalidated.
No screensaver overlay, startup hook, timeout change or test launch was applied.

## Photo transfer and current photo-display configuration

After explicit operator approval, all 572 prepared photos in 10 albums were
transferred to a new internal photo directory. The archive and every extracted
photo hash were verified before finalizing the directory; the uploaded temporary
archive was removed. Original Drive files were untouched. No Drive credentials
or signed download links were stored on the TV.

At the operator's request, Hearth's wallpaper now uses the Highlights album
(72 photos), shuffled every 30 seconds, with quietSec=30 to fade app tiles on
idle. The previous exact config was backed up privately; only wallpaper and
quietSec were changed. PS5 ordering, the restored stock-ribbon behavior and root
hooks were preserved. Hearth alone was reloaded. Configuration readback passed;
on-screen slideshow and idle-fade confirmation are pending. The comic wallpaper
remains available as a local alternative. This is Hearth photo-display mode,
not a replacement of LG's system-wide screensaver. Native OLED protection was
not modified.

## Further customization: capability findings, not C9 validation

Inspection of the installed Hearth bundle confirms folder-based wallpaper
slideshows from internal storage or USB, shuffle and configurable intervals,
quiet mode (app tiles fade after an idle delay), and an OLED-shift option.
These are candidate features to configure and physically test separately.
Slideshow plus quiet mode can provide a photo-display experience while Hearth
is foreground; it is not proof of replacing the system screensaver or taking
over idle screens in other apps or HDMI. Keep native OLED protection enabled.

For personal photos, first identify the operator's source: USB, a local/NAS
folder, or a cloud album. The inspected picker accepts local folders, not an
arbitrary shared-album URL. Cloud/NAS synchronization would need its own access,
privacy, credential-handling, caching and failure/recovery design; do not store
private album links or credentials in shared profiles. Prefer a curated local
copy or USB slideshow first. Retain the comic wallpaper as an alternative.

Useful follow-up workflow checks: back up the current Hearth config, preserve
the PS5-first order and stock-ribbon preference, verify photo-size limits for
the installed bundle, test idle fade and remote wake, test missing USB/source
behavior, and document whether the native screensaver interrupts the slideshow.

Photo-ingestion preparation on this C9 found the installed bundle slices each
slideshow folder to 400 files. Preserve larger collections as separate albums
below that limit rather than silently truncating a master folder. A collection
of 572 JPEG source files was downloaded through authenticated Drive access and
prepared locally as 1920x1080 JPEG copies: EXIF orientation applied, whole photo
fitted onto black without cropping, embedded metadata omitted, originals left
unchanged. All 572 output images decoded and hashes were recorded; display
copies totaled about 134 MiB. At this record update, no TV photo transfer has
occurred. Do not embed private album links, credentials or signed download URLs
in this reusable workflow, and do not infer these preparation results establish
native screensaver replacement or photo-playback validation.

## Current operator-selected configuration (supersedes dismissal patch below)

On 2026-10-29 the operator requested retaining LG's ribbon when Home is pressed
inside Hearth, to access TV options. Only the automatic ribbon-dismissal watcher
patch was reverted: watch.sh is again SHA256
`5d42a16d668288a9f041d2766506452f590a4716bc748e45a2eedb27dd8479fc`.
The C9 apply.sh Home-bar-mode override and boot/root hooks remain intact.
The restored watcher was restarted and verified. Intended behavior: Home from
another app reaches Hearth; Home within Hearth leaves LG's ribbon available.
The earlier ribbon-dismissal findings below remain historical optional guidance,
not the currently selected setup. This reverted state has not been reboot-tested.

The operator also approved a dark comic wallpaper and PS5-first Hearth layout.
PS5 was identified from the actual input label as HDMI4. Wallpaper was uploaded
as a new file under /media/developer/comix-dashboard, hash-verified, and only
wallpaper, tileOrder, sideMargin (50) and bottomMargin (40) fields were merged
into the app's saved configuration after private backup and drift checks.
All other fields were preserved. Hearth alone was reloaded; no TV reboot or
privacy-consent change was performed. On-screen layout confirmation is pending.

Recorded 2026-10-29. Scope: one OLED65C9PUA, firmware 03.50.31,
webOS release/SDK 4.5.0. These are model-specific candidate observations,
not validation for other C9 firmware or a native TVDebloat write capability.
No credentials, host addresses, or private recovery data belong in this file.

## Confirmed on this TV

- Root access survived an operator-approved reboot. The operator reported Home,
  Settings, remote, networking, apps, HDMI and CEC/ARC audio working.
- Preserve all existing apps and inputs. No system apps were uninstalled and no
  optional service catalog was applied as a disable list.
- Supported settings readback confirmed `general.homePromotion` and
  `general.aiNudge` changed from `on` to `off`. Live Plus/ACR was already off.
  Personalized-ad agreement changes were left alone because they also affect
  LG Channels consent. Do not describe this as removal of all tracking.
- Hearth package version 1.2.0 (`tld.my.customlauncher`) launched successfully;
  the operator confirmed apps and HDMI still worked. Stock LG Home remains.
- Hearth's helper and boot options alone did not redirect Home. The operator
  confirmed LG's ribbon remained visible during a 15-second observation.

## Root cause and candidate workaround

The Home ribbon generated `NL_HOME_SHOWN {}` in the system log, while the
foreground-app API continued to report Hearth or the streaming app. It did not
report `com.webos.app.home`. A real LG Home directory exists, so helper version 9
selected its foreground subscription instead of its existing Home-bar log mode.

The installed Hearth release embeds helper version 9; the inspected source tag
contains version 7. Inspect installed bytes and the release bundle. Do not
downgrade the helper to match a source-version assumption.

Approved candidate change: insert immediately after the shebang of
`/media/developer/launcher-homehook/apply.sh`:

```sh
export HOME_APP_DIR=/media/developer/launcher-homehook/.c9-homebar-event-mode
```

The sentinel path must not exist. This selects the existing watcher branch;
it does not rename or modify LG Home or edit `watch.sh`. Preserve the existing
`48-launcher-homehook` boot link and the independent root SSH startup hook.
Back up the exact original script privately, guard its hash, validate shell
syntax, stage and replace atomically, then restart only the verified Hearth
watcher and its subscription children. Do not use broad process-name kills.

Original apply.sh SHA256:
`a4dd345cc297809aa2f3c304994d5925047f24a7bc2289489762d456857e3765`.
Candidate SHA256:
`47a005694fce7743e7756b37a2d9abee7c942efd32200540aa20fecec0ab526f`.
These identify inspected bytes, not a universal patch contract.

## Validation status and recovery

A simulated `NL_HOME_SHOWN {}` event produced zero fake launches in foreground
mode and one in Home-bar mode. This did not launch a real app or change the
running helper. The approved live patch was applied on 2026-10-29. Fresh checks
confirmed the candidate script hash, a new watcher running in Home-bar mode,
unchanged watcher bytes, preserved boot/root hooks and key-only root SSH.
No reboot was performed. The operator subsequently reported that Home reaches
the launcher, with LG's ribbon visible for about a second first. This supports
Home redirection on this TV, with a visible transition limitation: the helper
reacts after the stock Home bar appears rather than suppressing its rendering.
Other post-patch physical checks and reboot persistence remain pending. Do not
promote this single-TV result as full or cross-firmware validation.

Additional failure case: the operator reports pressing Home while Hearth is
already open leaves the LG ribbon visible. Read-only checks found Hearth still
foreground, no stock-Home allow flag, and repeated helper log entries requesting
the launcher after Home-bar events. Therefore the first patch does not fully
replace Home behavior; a repeated launch does not reliably dismiss the overlay
in this case. Ribbon dismissal requires separate investigation and approval;
do not count this state as a fully working default launcher.

The operator clarified: Home from another app opens the ribbon, then Hearth
and dismisses the ribbon; Home inside Hearth opens the ribbon; Back with the
ribbon open dismisses it; Back with the ribbon closed opens Hearth Recent Apps.
Do not simulate Back blindly because it can act on Hearth after dismissal.
Installed LG Home AppServices.qml maps closeApp to
`com.webos.applicationManager/closeByAppId`; Interfaces.qml supplies
`{id: rootWindow.appId}` and handles the pause event by dismissing the UI.
A one-time operator-approved test targeting only `com.webos.app.home` returned
success, left Hearth foreground, and the operator confirmed the ribbon vanished.
A follow-up watcher patch is prepared: after launching Hearth for a Home-bar
event, query foreground and close only LG Home if Hearth is foreground. It sends
no Back key and preserves the stock-Home allow flag. Shell syntax and four fake
Luna cases passed: Hearth closes stock Home once; other/unknown foreground does
not close it; an active stock-Home allow flag suppresses both launch and close.
The operator approved and the follow-up watcher patch was applied on 2026-10-29.
The original watcher was backed up privately before an atomic replacement.
Fresh verification confirmed watcher SHA256
`6f98c02e9cc2cdf6a3f6bb1a4493d8df24c55fdad11c06e503016d6904ec3ae6`,
a new watcher PID in Home-bar mode, unchanged apply.sh, preserved boot/root hooks,
and key-only root SSH. No reboot was performed. The operator then confirmed
Home inside Hearth briefly opens the ribbon and it closes again. Home redirection
from another app and ribbon dismissal within Hearth are now physically confirmed
on this one TV. Broader post-patch app/input/audio/Back checks and reboot
persistence remain pending. The brief ribbon flash remains because this is
reactive interception, not suppression of the native Home key.

## Approved reboot persistence check

On 2026-10-29 the operator approved a reboot after the final watcher patch.
A changed kernel boot ID confirmed a new boot. Pinned key-only root SSH returned,
normal Telnet remained absent, both patched helper hashes matched, and the
watcher started automatically in Home-bar mode via the existing boot hook.
Foreground after boot was HDMI4; do not claim automatic opening into Hearth at
power-on from helper startup alone. Post-reboot on-screen Home/Back, app/input,
and audio checks were requested; the operator replied "looks good". Record this
as the operator's overall post-reboot confirmation, not separate instrumented
proof of each function. This was a software reboot, not a mains-disconnect
cold-boot test. The final result is a working Home takeover on this one TV,
with a brief native ribbon flash, automatic helper startup after reboot, and
the original LG Home retained for recovery. Revalidate after Hearth updates.

Final read-only audit after reboot confirmed homePromotion=off, aiNudge=off,
livePlus=off, all pre-existing app IDs and launch-point IDs preserved, and all
five inspected telemetry spool block mounts present. Mount presence is not
proof that every tracking path is blocked. Personalized-ad consent remains
unchanged to preserve LG Channels; system-service disabling and system-app
removal remain outside this validated setup.

After applying, verify the new script hash, watcher PID and command line,
filtered `HOME_APP_DIR` environment value, log-mode startup message, and intact
boot/root hooks. Ask the operator to test Home from a streaming app, Back,
Settings, apps, HDMI and audio; request separate reboot approval for persistence.

Recovery requires an inverse preview and approval, restoring the exact saved
apply.sh and restarting only the verified watcher. Hearth Options can disable
its helper. A future Hearth update or helper reinstall may overwrite this local
override; inspect and revalidate after updates. This record does not authorize
reusing this TV's rooting procedure on another firmware.

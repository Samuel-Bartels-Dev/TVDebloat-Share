# Independent webOS support for TVDebloat

Design for approval — 2026-10-28

## Intent and chosen approach

Extend the existing Python TVDebloat toolkit and its repo-local Codex/Claude skills so an operator can manage LG webOS discovery, debloat decisions, and launcher editing without requiring Glasshouse. Preserve exact previews, explicit operator approval, recovery evidence, and physical validation.

The operator chose independent webOS support. A Glasshouse API connection would reuse its dashboard but require deploying it. Independent SSH/Luna support owns the commands and avoids that dependency; it requires platform-specific discovery and stronger compatibility checks. Vendoring Glasshouse's entire server/UI would bring unrelated controls and is not proposed.

## Scope and delivery sequence

Implement one coherent first version in the existing repository:
1. Native webOS preflight, identity probe, app/launch-point inventory, and capability discovery over existing SSH access.
2. Separate webOS candidate profiles, evidence/NOTES, and exact offline change plans for app visibility and launcher ordering. Inventory service decisions separately; never infer permission to disable from upstream descriptions.
3. Approval-bound execution and restore for a narrowly verified launcher action: moving/reordering existing launch points through a supported Luna method, only when its current-state read, write schema, and inverse are established for the TV. No other mutation is enabled by this first version.
4. Skills and documentation that guide investigation of unsupported actions, protect core functions, and record operator tests. A pending action appears explicitly unsupported; it never silently becomes an executable plan.

Native discovery and preview must be useful even when no mutation capability is verified. Initial implementation may be verified against fixtures only; the actual C9 remains unvalidated until live discovery and physical checks. Do not claim that mocked tests prove C9 support.

## Platform and command model

Keep Python 3.11 and the existing CLI. Add explicit `--platform webos`; retain existing Android defaults for compatibility. The skill identifies OS before selecting a transport. Never auto-fallback to ADB for a webOS failure.

For webOS, reuse command intent (`preflight`, `probe`, `discover`, `preview`, `provision`, `restore`, `verify`, `drift`) with platform-specific implementations. Reject unsupported command/platform combinations clearly before connecting. Reject mismatched profile platforms before connecting. Guard the Android parser/engine against accidentally accepting a webOS profile. Legacy profiles without a platform remain Android.

Preview creates a local immutable plan with target identity, model, firmware, webOS version, profile digest, exact selected actions, observed prior values, proposed values, evidence, inverse operations, and plan digest. An apply command requires the exact saved plan, its digest, and explicit operator confirmation; the skill must obtain approval for the displayed diff before invoking it. General permission to develop the toolkit is not TV-change approval.

## Independent access and read-only discovery

Use the workstation's OpenSSH executable with a caller-selected host, user, port, and optional existing key path. Batch mode, strict host-key checking, bounded timeouts and output sizes, no agent/key forwarding. Do not accept unknown host keys silently, print credentials, provision keys, or guess passwords. Developer-mode SSH can be selected with its actual account/port/key; it provides only the permissions it really has. Missing permissions are a capability limitation, not a reason to escalate automatically.

The initial native client issues only a fixed allowlist of read operations. Discover model/firmware with the TV system-information service and webOS platform version separately. Inventory apps via applicationManager/listApps and listLaunchPoints, retaining installed apps and launch points as different objects (bookmarks and HDMI tiles must not be collapsed by app ID). Preserve ordering and app/launch-point identifiers. Check each response's returnValue, shape and completeness; unavailable or failed reads are unknown, never empty/successful.

Use documented version-specific Luna aliases only when the response specifically identifies a missing service; never retry a mutation against alternative methods. No scanning unrelated addresses or ports. Root access is an observed capability, not assumed from the account name.

Normalize only necessary identity, app/launcher and capability fields. Keep private connection details and recovery records in an explicitly chosen local workspace state directory, outside versioned profiles. Do not reuse the existing Android whole-settings backup. Redact serials, MACs, accounts, network identifiers and keys from exported evidence. Raw responses are not included by default.

No requests to the operator's TV during development until the implementation is reviewed and the read-only run is announced. No rooting, developer-mode enablement, firmware updates, daemon installs, startup hooks or reboot as an implicit prerequisite.

## Profiles and plans

Use an explicit webOS schema and loader separate from Android packages. Include schema version, platform, lifecycle status, manufacturer, model, firmware, webOS version and evidence references. Split app IDs, launch-point IDs, services, and privacy settings; none is an Android package.

All discovery starts with an empty executable change list. Unknown apps/services stay in review. The profile can record desired app visibility and launcher order for planning, but unsupported changes are blocked with a reason. First-version apply supports verified existing launch-point moves only. App hiding, service disabling, uninstall, privacy changes, third-party launcher installation and Home takeover remain research/preview entries and are not executable.

Require exact identity/firmware matching for writes; same-brand matches are insufficient. Candidate profiles require an explicit pilot acknowledgement in addition to exact-plan approval. No automatic promotion: verified readback, operator behavior tests and reboot observations are required.

Seed an operator-observations note for LG OLED65C9PUA with reported firmware 3.50.31, but mark the webOS platform version, access, app inventory and mutation compatibility unverified. Do not fabricate a live candidate profile from that observation alone.

## Launcher editing boundary

Inventory, preview and, when verified, reorder existing LG Home launch points. This is distinct from installing/replacing the launcher. Protect stock Home and Settings, input/live-TV handlers, first-use/setup, browser, Homebrew/recovery and control apps. A move plan must preserve every launch point and only change positions; unknown or duplicate identities block execution.

Do not port Glasshouse Home's takeover to the C9: upstream home.js explicitly rejects webOS 4. Its dashboard testing on other C9 firmware is no proof of launcher compatibility. If this C9 has no verified reversible move method, the first version remains read-only for it and explains what evidence is missing. A Homebar or other replacement integration is a separate compatibility decision and requires its own exact install/restore preview and approval.

## Apply and recovery invariants

Before a supported move: verify SSH host identity, live TV identity, profile/plan digest, current ordered launch-point snapshot, and required capabilities. Any drift requires a new preview and new approval. Never run arbitrary shell or arbitrary Luna endpoints supplied by profiles.

Create a unique recovery journal locally before the first mutation. Record pending action before execution and observed result afterward using atomic local writes. Execute one action at a time; check Luna success and fresh ordering readback. Stop on error/timeout/disconnect/ambiguous result; preserve the journal and do not blindly retry or roll back uncertain actions. Show an exact recovery plan and obtain approval before restoring. Recovery may only invert recorded completed changes on the same verified identity and compatible snapshot; refuse concurrent layout edits.

No approved move changes app installation, visibility, services, startup behavior, network settings or panel care. Both preview and error messages explain that launcher reordering is the only implemented first-version mutation.

## Evidence and upstream lessons

Research baseline: Glasshouse ea4842e21e572ae67bf0958d03c833f124803fc8; TVDebloat 9d67ed71fd462fe3870539f90c88f0b8f4a24698. See the accompanying source review for file-level findings.

Keep a concise provenance map for Luna transport aliases, identity fields, app/launch-point semantics and safety findings. Glasshouse retired tvdataexchanger and alwaysready after video failures: record those exclusions, do not turn its catalog into a safe-disable list. Prefer independent code; retain the MIT notice for any copied or substantially adapted source.

Update both repo-local skills with OS routing and a selectively loaded webOS reference. Keep Android workflows intact. Clarify the README's current 'launcher out of scope' statement to describe the new bounded webOS launcher-editing scope.

## Verification and acceptance

- Existing Android tests still pass; default CLI behavior stays compatible.
- Synthetic webOS fixtures cover old/new service aliases, permission errors, malformed/false responses, missing platform version, non-root access, bookmarks/HDMI duplicate app IDs and missing mutation support.
- Assert discovery/preview cannot send writes and cross-platform profiles fail before transport creation.
- Exercise a verified move against a local fake SSH/Luna TV: exact preview, explicit plan approval, digest/profile tampering, stale identity/order, failure before/after an action, partial journal recovery, inverse preview and readback.
- Credentials/private fields never enter standard output, notes, shared profiles or plans.
- Unsupported webOS/firmware fails closed for writes without blocking useful discovery.
- Live C9 validation remains pending until operator-authorized read-only discovery. After any approved pilot, operator checks Home/Back, apps, HDMI, CEC/ARC audio, remote, Settings, sleep/wake and cold boot; record results in NOTES.

## Builder choices

Builder chooses module/file names, fixture layout and CLI flag spelling consistent with existing style. Do not refactor unrelated Android behavior, add a new dashboard, copy Glasshouse's UI, or expand executable mutations beyond verified launcher moves. If independent source research cannot establish a safe move contract, retain a clearly unsupported mutation capability and deliver discovery/preview with that limitation documented rather than inventing a command.

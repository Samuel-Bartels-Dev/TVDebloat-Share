# Maintaining reusable TV knowledge

The shared repository stores reusable technical references derived from work,
not a user's setup diary. Apply this to model notes, profiles, skill references,
examples, generated artifacts and commit messages.

## What to retain

Record the smallest useful procedure: supported model/firmware/app versions,
prerequisites, affected API/configuration fields, safe steps, verification,
failure symptom and working resolution, rollback boundary and remaining limits.
Technical identifiers such as app IDs, API names and stock paths are useful.
Use placeholders for installation-specific values. Keep date/method of validation
when it helps establish compatibility, without recording a household's activity.

Do not commit names, contact details, account/vault references, private endpoints,
network/device identifiers, credentials, note contents, screenshots of private
systems, media titles/album names, personal media counts or preferred app/input
layouts. A one-off installed-file hash or transcript usually belongs in private
recovery evidence, not the shared guide. Source/release hashes may be retained
when they identify a reproducible compatibility contract rather than personal
content. Keep backup artifacts and machine bindings outside the repository.
Inspect staged changes before publication; .gitignore alone does not sanitize
already tracked files. Public upstream author/license attribution is appropriate.

## One current answer for each task

Read the relevant reference before external research. Recheck live compatibility
and user intent; a previous user's configuration or approval never becomes a
new user's default. Reuse established mechanics rather than rediscovering them.

When a step fails, inspect state before retrying and determine whether the cause
is version drift, environment, input, a preference difference or wrong guidance.
If research is necessary, verify the correction against the affected system.
Then update the existing task section, its profile summary and skill routing:

- Replace the incorrect or obsolete instruction with the working method.
- Retain a short symptom/cause/resolution when it prevents repetition.
- Remove contradictory old pending/not-installed claims after later proof.
- Mark unverified alternatives as candidates; never label a guess as a fix.
- State exactly what passed: syntax, readback, rendering, operator test or reboot.
  Successful readback does not prove physical behavior or cold-boot persistence.

Do not append another chronological update that leaves two competing answers.
Useful version-specific alternatives may coexist when their selection rule is
explicit. Git already preserves earlier revisions; do not duplicate a session
transcript as an archive inside the current reference.

## Review before sharing

Check affected current references agree, links resolve and the content remains
useful with a different user, network, media collection and input layout. Scan
the staged diff for private content. Run relevant repository validators/tests;
documentation checks are not proof of a live TV operation. If private material
was committed earlier, sanitizing current files does not erase Git history.
History cleanup is a separate scoped operation; never silently force-push it.

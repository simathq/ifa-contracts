# IFA contracts

Source of truth for the edge ↔ backend integration seam. Everything an edge box
sends and the backend accepts is defined here. **There is no vendored copy:**
`ifa-backend` and `ifa-edge` both install this package — each pinning it by tag,
because a cloud build clones one repo and has no sibling checkout — and validate
against these same files. A consequence worth knowing before you add a file
here: **a new event type does not exist for either service until this package is
tagged and their venvs reinstall.** Until then `make sync-check` refuses the
manifest that emits it. The backend seeds its `event_types`
registry from `event_types/` during `make sync` and validates every ingested
payload against the registry; the edge validates locally before sending, so
contract drift fails on the box first.

## Files

- `ifa_event@2.schema.json` — the IFA_EVENT envelope, version 2. Universal
  across all modules and tenants: it names the instance's premises once and
  lists the sources the event came from, each with its area. The `payload`
  field is intentionally untyped here.
- `ifa_event.schema.json` — envelope version 1, with the factory-shaped
  `location` and `sources[].stream_id`. Kept while boxes move to version 2.
- `module_manifest@2.schema.json` — shape of a module template's manifest
  (stored in `module_templates.manifest`), version 2: named `inputs`, each
  with a kind (video or data), how many sources it takes, whether it is
  required, the fields a data input reads, and the lines and regions a video
  input needs drawn.
- `module_manifest.schema.json` — manifest version 1, with
  `streams_required`. Kept while modules move to version 2.

The package picks a file by version: `envelope_validator(version)`,
`manifest_validator(version)`, `envelope_schema(version)`,
`manifest_schema(version)`. The version defaults to 1 so code written before
version 2 still runs; new code passes it.
- `event_types/<type>@<version>.json` — payload schema per event type.
  Standardized per event type **across all tenants**: a
  `label_misalignment_detected` payload has the same shape for every customer.
  Manifests reference `(event_type, event_type_version)`; they never embed
  payload schemas.

## Versioning rules

- **Envelope** (`ifa_event_version`): integer, bumped only on a breaking
  envelope change (removing/renaming a field, changing a type). Adding an
  *optional* field is not a bump. The backend accepts every version in
  `ENVELOPE_VERSIONS` — today 1 and 2 — so boxes move one at a time; a
  version leaves that tuple only once no box sends it.
- **Event type payloads** (`event_type_version`): versioned independently per
  type, same rule — breaking change bumps, additive optional fields do not.
  A new version is a new file: `label_misalignment_detected@2.json`; keep the
  old file until no supported module template emits it.
- **Manifests** (`manifest_version`): versions the manifest *format*, not any
  particular template. Template evolution is `template_version` in the row.
  Sync accepts every version in `MANIFEST_VERSIONS`, today 1 and 2.
- IDs are immutable: `event_type` strings, `template_id` slugs and taxonomy
  ids never change once an automation or instance references them.

## Namespaces

Module event types are bare snake_case (`cap_missing_detected`). The dotted
form is reserved for non-module platform events (`platform.heartbeat`,
`platform.stream_offline`) — same envelope, no module manifest, arriving in a
later phase.

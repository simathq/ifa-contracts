# IFA contracts

Source of truth for the edge ↔ backend integration seam. Everything an edge box
sends and the backend accepts is defined here. `ifa-edge` vendors a copy of this
directory (manual copy for now); the backend seeds its `event_types` registry
from `event_types/` at seed time and validates every ingested event against
these schemas.

## Files

- `ifa_event.schema.json` — the IFA_EVENT envelope. Universal across all
  modules and factories. The `payload` field is intentionally untyped here.
- `module_manifest.schema.json` — shape of a module template's manifest
  (stored in `module_templates.manifest`).
- `event_types/<type>@<version>.json` — payload schema per event type.
  Standardized per event type **across all factories**: a
  `label_misalignment_detected` payload has the same shape for every customer.
  Manifests reference `(event_type, event_type_version)`; they never embed
  payload schemas.

## Versioning rules

- **Envelope** (`ifa_event_version`): integer, bumped only on a breaking
  envelope change (removing/renaming a field, changing a type). Adding an
  *optional* field is not a bump. The backend accepts the current version;
  an N-1 acceptance window becomes policy once version 2 exists.
- **Event type payloads** (`event_type_version`): versioned independently per
  type, same rule — breaking change bumps, additive optional fields do not.
  A new version is a new file: `label_misalignment_detected@2.json`; keep the
  old file until no supported module template emits it.
- **Manifests** (`manifest_version`): versions the manifest *format*, not any
  particular template. Template evolution is `template_version` in the row.
- IDs are immutable: `event_type` strings, `template_id` slugs and taxonomy
  ids never change once an automation or instance references them.

## Namespaces

Module event types are bare snake_case (`cap_missing_detected`). The dotted
form is reserved for non-module platform events (`platform.heartbeat`,
`platform.stream_offline`) — same envelope, no module manifest, arriving in a
later phase.

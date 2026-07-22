# ifa-contracts

The **single source of truth** for the IFA_EVENT contract: the universal
envelope, the per-event-type payload schemas, and the module-manifest
meta-schema. Both `ifa-backend` (ingest validation + registry seeding) and
`ifa-edge` (local pre-send validation) depend on this package, so the schemas
are defined exactly once.

> Replaces the old arrangement — a source-of-truth copy in
> `ifa-backend/contracts/` plus a manually vendored copy in
> `ifa-edge/contracts/`, kept in sync by convention. There is no copy step
> anymore.

## Layout

```
ifa_contracts/
  __init__.py          # loader/validator API
  schemas/
    README.md          # versioning rules (source of truth)
    ifa_event.schema.json
    module_manifest.schema.json
    event_types/<type>@<version>.json
    examples/example_module.manifest.json
```

## Install (editable, from a consuming repo)

```sh
pip install -e ../ifa-contracts
```

Both `ifa-backend` and `ifa-edge` declare this via `-e ../ifa-contracts` in
their `requirements.txt`. That relative path assumes **the three repos are
checked out as siblings** under a common parent (`.../IFA/ifa-backend`,
`.../IFA/ifa-edge`, `.../IFA/ifa-contracts`); clone one without this repo next
to it and `pip install -r requirements.txt` fails. Publishing a versioned
artifact to a package index (removing the path coupling) is a later item.

## API

```python
import ifa_contracts as c

c.envelope_schema()                       # IFA_EVENT envelope dict
c.manifest_schema()                       # module-manifest meta-schema
c.payload_schema("person_detected", 1)    # payload schema dict, or None
c.iter_event_types()                      # [(type, version, schema), ...] for seeding
c.example_manifest()                       # reference Example Module manifest

c.envelope_validator()                    # cached Draft202012Validator (envelope)
c.payload_validator("person_detected", 1) # cached validator, or None
c.make_validator(schema)                  # validator for a registry-fetched schema
```

## Versioning

See `ifa_contracts/schemas/README.md`. IDs and `event_type` strings are
immutable once referenced; add a new `@N` file for a breaking payload change.

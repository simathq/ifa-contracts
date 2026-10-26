"""IFA contract schemas — the single source of truth, shared by ifa-backend
(ingest validation + registry seeding) and ifa-edge (local pre-send
validation). Previously a source-of-truth copy in ifa-backend/contracts plus a
manually vendored copy in ifa-edge/contracts; this package replaces both.

The raw JSON lives under `schemas/`; this module is the loader/validator API
over it. Versioning rules are in `schemas/README.md`.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_DIR = Path(__file__).parent / "schemas"
EVENT_TYPES_DIR = SCHEMA_DIR / "event_types"


@lru_cache(maxsize=None)
def load_schema(relpath: str) -> dict:
    """Load a schema JSON by path relative to the schemas/ root."""
    return json.loads((SCHEMA_DIR / relpath).read_text())


# Every envelope and manifest version a supported service may still meet. The
# backend accepts each of them during a transition, so boxes and modules move
# one at a time (schemas/README.md, "Versioning rules").
ENVELOPE_VERSIONS = (1, 2)
MANIFEST_VERSIONS = (1, 2)

# Version 1 keeps the file name it had before versions existed.
_ENVELOPE_FILES = {1: "ifa_event.schema.json", 2: "ifa_event@2.schema.json"}
_MANIFEST_FILES = {1: "module_manifest.schema.json", 2: "module_manifest@2.schema.json"}


def envelope_schema_relpath(version: int = 1) -> str:
    """Schema file of an envelope version. The default of 1 keeps callers
    written before version 2 working; pass the version."""
    try:
        return _ENVELOPE_FILES[version]
    except KeyError:
        raise ValueError(f"unknown ifa_event_version {version!r}") from None


def manifest_schema_relpath(version: int = 1) -> str:
    """Schema file of a manifest version; the default is as for envelopes."""
    try:
        return _MANIFEST_FILES[version]
    except KeyError:
        raise ValueError(f"unknown manifest_version {version!r}") from None


def envelope_schema(version: int = 1) -> dict:
    """The IFA_EVENT envelope schema of one ifa_event_version."""
    return load_schema(envelope_schema_relpath(version))


def manifest_schema(version: int = 1) -> dict:
    """The module-manifest meta-schema of one manifest_version."""
    return load_schema(manifest_schema_relpath(version))


def example_manifest() -> dict:
    """The reference Example Module manifest, at the newest manifest_version."""
    return load_schema("examples/example_module.manifest.json")


def payload_schema_relpath(event_type: str, version: int) -> str:
    return f"event_types/{event_type}@{version}.json"


def payload_schema(event_type: str, version: int) -> dict | None:
    """Payload schema for (event_type, version), or None if not registered."""
    p = EVENT_TYPES_DIR / f"{event_type}@{version}.json"
    return json.loads(p.read_text()) if p.exists() else None


def iter_event_types() -> list[tuple[str, int, dict]]:
    """All (event_type, version, schema) triples, for seeding the registry.
    Filename `<type>@<version>.json` is the source of the type/version split."""
    out: list[tuple[str, int, dict]] = []
    for f in sorted(EVENT_TYPES_DIR.glob("*.json")):
        type_, _, version = f.stem.partition("@")
        out.append((type_, int(version), json.loads(f.read_text())))
    return out


@lru_cache(maxsize=None)
def _cached_validator(relpath: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(relpath), format_checker=FormatChecker())


def envelope_validator(version: int = 1) -> Draft202012Validator:
    return _cached_validator(envelope_schema_relpath(version))


def manifest_validator(version: int = 1) -> Draft202012Validator:
    return _cached_validator(manifest_schema_relpath(version))


def payload_validator(event_type: str, version: int) -> Draft202012Validator | None:
    rel = payload_schema_relpath(event_type, version)
    if not (SCHEMA_DIR / rel).exists():
        return None
    return _cached_validator(rel)


def make_validator(schema: dict) -> Draft202012Validator:
    """Validator for an ad-hoc schema (e.g. a payload schema fetched from the
    backend registry rather than from disk)."""
    return Draft202012Validator(schema, format_checker=FormatChecker())

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


def envelope_schema() -> dict:
    """The IFA_EVENT envelope schema (ifa_event.schema.json)."""
    return load_schema("ifa_event.schema.json")


def manifest_schema() -> dict:
    """The module-manifest meta-schema (module_manifest.schema.json)."""
    return load_schema("module_manifest.schema.json")


def example_manifest() -> dict:
    """The reference Example Module manifest."""
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


def envelope_validator() -> Draft202012Validator:
    return _cached_validator("ifa_event.schema.json")


def payload_validator(event_type: str, version: int) -> Draft202012Validator | None:
    rel = payload_schema_relpath(event_type, version)
    if not (SCHEMA_DIR / rel).exists():
        return None
    return _cached_validator(rel)


def make_validator(schema: dict) -> Draft202012Validator:
    """Validator for an ad-hoc schema (e.g. a payload schema fetched from the
    backend registry rather than from disk)."""
    return Draft202012Validator(schema, format_checker=FormatChecker())

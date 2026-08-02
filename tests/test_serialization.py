"""Serialization determinism, digest stability, and the review manifest."""

import dataclasses
import json

from white_line import (
    WHITE_RECORDS,
    canonical_registry,
    registry_digest,
    registry_manifest,
)


def test_canonical_registry_is_id_sorted_json_with_full_fields() -> None:
    payload = json.loads(canonical_registry(WHITE_RECORDS))
    ids = [entry["id"] for entry in payload]
    assert ids == sorted(ids)
    for entry in payload:
        assert set(entry) == {
            "id",
            "title",
            "kind",
            "description",
            "prompt",
            "review_horizon_days",
        }


def test_digest_is_order_independent_and_repeatable() -> None:
    forward = registry_digest(WHITE_RECORDS)
    assert forward == registry_digest(tuple(reversed(WHITE_RECORDS)))
    assert forward == registry_digest(WHITE_RECORDS)
    assert len(forward) == 64


def test_digest_changes_when_a_record_changes() -> None:
    edited = (
        dataclasses.replace(WHITE_RECORDS[0], description="quietly reworded"),
    ) + WHITE_RECORDS[1:]
    assert registry_digest(edited) != registry_digest(WHITE_RECORDS)


def test_registry_manifest_summarizes_the_ledger() -> None:
    manifest = registry_manifest(WHITE_RECORDS)
    assert manifest["record_count"] == 11
    assert manifest["digest"] == registry_digest(WHITE_RECORDS)
    assert manifest["records_by_kind"] == {
        "CONTEMPLATIVE": 3,
        "EPISTEMIC": 4,
        "ETHICAL": 4,
    }
    assert manifest["ledger_version"]


def test_the_three_json_payloads_carry_distinct_schema_identifiers() -> None:
    """A shared ``"1.1"`` made the field useless for telling payloads apart.

    Three structurally different documents declared the same bare version
    string, so a reader could not use it to identify what it was holding.
    Each identifier is now namespaced, and this asserts they are distinct and
    that the manifest actually carries its own.
    """

    from white_line.serialization import (
        FIGURE_REGISTRY_SCHEMA,
        REGISTRY_ARTIFACT_SCHEMA,
        REGISTRY_MANIFEST_SCHEMA,
    )

    identifiers = (
        REGISTRY_MANIFEST_SCHEMA,
        REGISTRY_ARTIFACT_SCHEMA,
        FIGURE_REGISTRY_SCHEMA,
    )
    assert len(set(identifiers)) == len(identifiers)
    assert all(name.startswith("white-line.") for name in identifiers)
    assert registry_manifest(WHITE_RECORDS)["schema_version"] == (
        REGISTRY_MANIFEST_SCHEMA
    )


def test_the_pinned_ledger_digest_matches_the_live_registry() -> None:
    """The pin is what turns "bump LEDGER_VERSION" into an enforceable rule.

    ``tests/test_audit.py`` proves the audit rejects an unpinned edit; this
    asserts the shipped pin is currently correct, so the two together fail on
    a registry change in either direction.
    """

    from white_line.version import LEDGER_VERSION, LEDGER_VERSION_DIGEST

    assert LEDGER_VERSION_DIGEST == registry_digest(WHITE_RECORDS)
    assert len(LEDGER_VERSION_DIGEST) == 64
    assert LEDGER_VERSION

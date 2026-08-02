"""White Line package and ledger version markers.

``__version__`` tracks the installable package. ``LEDGER_VERSION`` tracks the
content of the absence registry itself: bump it whenever a record is added,
removed, or reworded, so that a stored manifest can be compared against a
later checkout during review.

``LEDGER_VERSION_DIGEST`` makes that instruction enforceable instead of merely
stated. It pins the canonical registry digest that ``LEDGER_VERSION`` names.
Any edit to registry content — including a reworded description that leaves
the record count and the per-kind partition untouched — changes the digest, so
the audit gate and the test suite both fail until the two are updated
together. Re-pin it with::

    python -c "from white_line import WHITE_RECORDS, registry_digest; print(registry_digest(WHITE_RECORDS))"
"""

__version__ = "0.7.0"

LEDGER_VERSION = "2026.07"

LEDGER_VERSION_DIGEST = (
    "11047a641a8e80c985f2bbd8a45b67a0e67048b235020aa52aa46da1cc02682a"
)

__all__ = ["LEDGER_VERSION", "LEDGER_VERSION_DIGEST", "__version__"]

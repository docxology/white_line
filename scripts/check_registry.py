"""Check White Line ledger soundness and print its review manifest."""

from __future__ import annotations

import argparse

from white_line import WHITE_RECORDS, __version__, all_ledger_checks, registry_manifest


def main() -> None:
    """Check registry soundness and print the review manifest.

    The parser takes no options. It is still constructed, because a check
    script that accepts an unrecognized flag and exits ``0`` reports success
    for a command it never ran — a typo'd flag in a release sequence would
    read as a passing gate.
    """

    argparse.ArgumentParser(description=__doc__).parse_args()
    failures = [check for check in all_ledger_checks(WHITE_RECORDS) if not check.passed]
    if failures:
        raise SystemExit(
            "; ".join(f"{check.name}: {check.detail}" for check in failures)
        )
    manifest = registry_manifest(WHITE_RECORDS)
    print(
        f"{manifest['record_count']} White Line records; "
        f"package_version={__version__}; "
        f"ledger_version={manifest['ledger_version']}; "
        f"digest={manifest['digest']}"
    )


if __name__ == "__main__":
    main()

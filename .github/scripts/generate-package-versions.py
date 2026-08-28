#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PACKAGES = (
    "luci-app-smartsafehub",
    "safeshield",
    "luci-app-safeshield",
)


def load_arch_versions(index_file: Path) -> tuple[str, dict[str, str]]:
    try:
        payload = json.loads(index_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"failed to read package index {index_file}: {exc}") from exc

    architecture = payload.get("architecture")
    packages = payload.get("packages")
    if not isinstance(architecture, str) or not architecture:
        raise ValueError(f"missing architecture in {index_file}")
    if not isinstance(packages, dict):
        raise ValueError(f"missing packages object in {index_file}")

    versions: dict[str, str] = {}
    for package in PACKAGES:
        version = packages.get(package)
        if not isinstance(version, str) or not version:
            raise ValueError(f"{package} is missing from {index_file}")
        versions[package] = version

    return architecture, versions


def generate_versions(
    packages_root: Path, feed: str, channel: str, output: Path
) -> dict[str, object]:
    indexes = sorted(packages_root.glob(f"*/{feed}/index.json"))
    if not indexes:
        raise ValueError(f"no package indexes found under {packages_root}")

    expected_versions: dict[str, str] | None = None
    architectures: list[str] = []

    for index_file in indexes:
        architecture, versions = load_arch_versions(index_file)
        if architecture in architectures:
            raise ValueError(
                f"duplicate architecture in package indexes: {architecture}"
            )

        if expected_versions is None:
            expected_versions = versions
        elif versions != expected_versions:
            differences = []
            for package in PACKAGES:
                expected = expected_versions[package]
                actual = versions[package]
                if actual != expected:
                    differences.append(
                        f"{package}: expected {expected}, {architecture} has {actual}"
                    )
            raise ValueError(
                "package versions differ between architectures: "
                + "; ".join(differences)
            )

        architectures.append(architecture)

    assert expected_versions is not None
    payload: dict[str, object] = {
        "schema_version": 1,
        "channel": channel,
        "packages": expected_versions,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Generated {output} from {len(architectures)} architecture(s): "
        + ", ".join(sorted(architectures))
    )
    for package in PACKAGES:
        print(f"{package}={expected_versions[package]}")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a channel-wide package version summary from published repo indexes"
    )
    parser.add_argument("--packages-root", type=Path, required=True)
    parser.add_argument("--feed", default="smartsafehub")
    parser.add_argument("--channel", choices=("stable", "beta"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    generate_versions(args.packages_root, args.feed, args.channel, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

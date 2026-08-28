#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

PACKAGE = "luci-app-smartsafehub"
HEADER_RE = re.compile(r"^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})$")
SECTION_RE = re.compile(r"^###\s+(.+?)\s*$")
SAFE_VERSION_RE = re.compile(r"^[A-Za-z0-9._~+-]+$")
MAX_RELEASE_NOTE_BYTES = 65536


@dataclass
class ReleaseSection:
    title: str
    items: list[str] = field(default_factory=list)


@dataclass
class ReleaseNote:
    version: str
    date: str
    summary_lines: list[str] = field(default_factory=list)
    sections: list[ReleaseSection] = field(default_factory=list)

    def as_json(self) -> dict[str, object]:
        summary = " ".join(line.strip() for line in self.summary_lines if line.strip()).strip()
        return {
            "schema_version": 1,
            "package": PACKAGE,
            "version": self.version,
            "date": self.date,
            "summary": summary or None,
            "sections": [
                {"title": section.title, "items": section.items}
                for section in self.sections
                if section.items
            ],
        }


def make_value(makefile: Path, key: str) -> str:
    prefix = f"{key}:="
    for raw_line in makefile.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith(prefix):
            return raw_line[len(prefix) :].strip()
    raise ValueError(f"{key} is missing from {makefile}")


def current_release_version(source: Path) -> str:
    makefile = source / "Makefile"
    version = make_value(makefile, "PKG_VERSION")
    release = make_value(makefile, "PKG_RELEASE")

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid PKG_VERSION: {version}")
    if not release.isdigit() or int(release) <= 0:
        raise ValueError(f"invalid PKG_RELEASE: {release}")

    return f"{version}-r{release}"


def parse_changelog(changelog: Path) -> list[ReleaseNote]:
    releases: list[ReleaseNote] = []
    current: ReleaseNote | None = None
    current_section: ReleaseSection | None = None

    for raw_line in changelog.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        header = HEADER_RE.match(line)
        if header:
            current = ReleaseNote(version=header.group(1), date=header.group(2))
            releases.append(current)
            current_section = None
            continue

        if current is None:
            continue

        section = SECTION_RE.match(line)
        if section:
            current_section = ReleaseSection(title=section.group(1).strip())
            current.sections.append(current_section)
            continue

        if line.startswith("## "):
            current = None
            current_section = None
            continue

        if current_section is not None:
            if line.startswith("- "):
                current_section.items.append(line[2:].strip())
            elif line.startswith(("  ", "\t")) and line.strip() and current_section.items:
                current_section.items[-1] = f"{current_section.items[-1]} {line.strip()}"
            continue

        stripped = line.strip()
        if stripped:
            current.summary_lines.append(stripped)

    return releases


def validate_release(note: ReleaseNote) -> None:
    if not SAFE_VERSION_RE.fullmatch(note.version):
        raise ValueError(f"unsafe release version for filename: {note.version}")

    payload = note.as_json()
    if not payload["summary"] and not payload["sections"]:
        raise ValueError(f"release {note.version} has no summary or section items")


def write_release_notes(source: Path, output: Path) -> str:
    changelog = source / "CHANGELOG.md"
    if not changelog.is_file():
        raise ValueError(f"missing changelog: {changelog}")

    expected = current_release_version(source)
    releases = parse_changelog(changelog)
    by_version = {release.version: release for release in releases}
    if expected not in by_version:
        raise ValueError(
            f"CHANGELOG.md does not contain current package release {expected}"
        )

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    for release in releases:
        validate_release(release)
        destination = output / f"{release.version}.json"
        rendered = json.dumps(release.as_json(), ensure_ascii=False, indent=2) + "\n"
        encoded = rendered.encode("utf-8")
        if len(encoded) > MAX_RELEASE_NOTE_BYTES:
            raise ValueError(
                f"release {release.version} JSON exceeds {MAX_RELEASE_NOTE_BYTES} bytes"
            )
        destination.write_bytes(encoded)

    return expected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SmartSafeHub release-note JSON from CHANGELOG.md"
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    expected = write_release_notes(args.source, args.output)
    generated = sorted(path.name for path in args.output.glob("*.json"))
    print(f"Generated {len(generated)} release note file(s); current={expected}")
    for name in generated:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

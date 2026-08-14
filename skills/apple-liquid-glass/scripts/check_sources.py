#!/usr/bin/env python3
"""Verify Apple API declarations and availability used by the skill.

The expectation manifest records semantic fields rather than whole-page hashes,
so unrelated documentation edits do not create noise. A mismatch means the
affected guidance must be re-read; it is not an instruction to update the
expectation automatically.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "source_expectations.json"
BASE_URL = "https://developer.apple.com/tutorials/data/documentation/"
TIMEOUT_SECONDS = 30


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def load_manifest() -> list[dict]:
    data = json.loads(MANIFEST.read_text())
    if data.get("schema_version") != 1:
        raise ValueError("source_expectations.json has an unsupported schema_version")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_expectations.json must contain a non-empty sources list")

    seen: set[str] = set()
    for source in sources:
        required = {"id", "path", "title", "declaration_contains", "availability"}
        missing = required - set(source)
        if missing:
            raise ValueError(f"{source.get('id', '<unknown>')} missing {sorted(missing)}")
        if source["id"] in seen:
            raise ValueError(f"duplicate source id: {source['id']}")
        seen.add(source["id"])
        if not isinstance(source["availability"], dict):
            raise ValueError(f"{source['id']} availability must be an object")
    return sources


def source_url(source: dict) -> str:
    encoded = quote(source["path"], safe="/():_,")
    return f"{BASE_URL}{encoded}.json"


def fetch(source: dict) -> tuple[dict, dict | None, str | None]:
    request = Request(
        source_url(source),
        headers={"User-Agent": "apple-liquid-glass-source-check/1.0"},
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return source, json.load(response), None
    except HTTPError as error:
        return source, None, f"HTTP {error.code}"
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        return source, None, str(error)


def documented_availability(document: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for platform in document.get("metadata", {}).get("platforms", []):
        value = platform.get("introducedAt", "?")
        if platform.get("beta"):
            value += " beta"
        if platform.get("deprecated"):
            value += " deprecated"
        out[platform.get("name", "?")] = value
    return dict(sorted(out.items()))


def documented_declarations(document: dict) -> list[str]:
    out: list[str] = []
    for section in document.get("primaryContentSections", []):
        if section.get("kind") != "declarations":
            continue
        for declaration in section.get("declarations", []):
            text = "".join(token.get("text", "") for token in declaration.get("tokens", []))
            out.append(normalize(text))
    return out


def compare(source: dict, document: dict) -> list[str]:
    mismatches: list[str] = []
    actual_title = document.get("metadata", {}).get("title")
    if actual_title != source["title"]:
        mismatches.append(f"title: expected {source['title']!r}, got {actual_title!r}")

    expected_availability = dict(sorted(source["availability"].items()))
    actual_availability = documented_availability(document)
    if actual_availability != expected_availability:
        mismatches.append(
            f"availability: expected {expected_availability}, got {actual_availability}"
        )

    needle = normalize(source["declaration_contains"])
    declarations = documented_declarations(document)
    if not any(needle in declaration for declaration in declarations):
        mismatches.append(
            f"declaration missing {needle!r}; documented declarations: {declarations}"
        )
    return mismatches


def check_live(sources: list[dict]) -> int:
    results: dict[str, tuple[dict | None, str | None]] = {}
    with ThreadPoolExecutor(max_workers=min(8, len(sources))) as pool:
        futures = {pool.submit(fetch, source): source["id"] for source in sources}
        for future in as_completed(futures):
            source, document, error = future.result()
            results[source["id"]] = (document, error)

    mismatched = 0
    unreachable = 0
    for source in sources:
        document, error = results[source["id"]]
        if error:
            unreachable += 1
            print(f"UNREACHABLE {source['id']}: {error}")
            continue
        mismatches = compare(source, document or {})
        if mismatches:
            mismatched += 1
            print(f"DRIFT {source['id']} ({source_url(source)})")
            for mismatch in mismatches:
                print(f"  - {mismatch}")

    if unreachable:
        print(f"Unable to verify {unreachable}/{len(sources)} source(s).")
        return 2
    if mismatched:
        print(f"Detected semantic drift in {mismatched}/{len(sources)} source(s).")
        return 1
    print(f"Verified {len(sources)} Apple API expectation(s); no semantic drift.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fetch and compare live docs")
    mode.add_argument("--offline", action="store_true", help="validate the manifest only")
    args = parser.parse_args()

    try:
        sources = load_manifest()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Invalid source manifest: {error}", file=sys.stderr)
        return 2

    if args.offline:
        print(f"Validated {len(sources)} source expectation(s).")
        return 0
    return check_live(sources)


if __name__ == "__main__":
    raise SystemExit(main())

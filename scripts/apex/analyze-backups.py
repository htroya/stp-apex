#!/usr/bin/env python3
"""Inspect local APEX split exports and print a reusable catalog."""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
import zipfile
from typing import Iterable


APP_NAME_RE = re.compile(
    r"p_name=>nvl\(wwv_flow_application_install.get_application_name,'([^']+)'\)"
)
APP_ALIAS_RE = re.compile(
    r"p_alias=>nvl\(wwv_flow_application_install.get_application_alias,'([^']+)'\)"
)
CREATE_CALL_RE = re.compile(
    r"wwv_flow_imp(?:_page|_shared|)\.create_([a-z0-9_]+)\(", re.IGNORECASE
)
PLUG_SOURCE_RE = re.compile(r"p_plug_source_type=>'([^']+)'")
PROCESS_TYPE_RE = re.compile(r"p_process_type=>'([^']+)'")
PAGE_NAME_RE = re.compile(r"create_page\(.*?p_name=>'([^']+)'", re.S)


def read_text(archive: zipfile.ZipFile, member: str) -> str:
    return archive.read(member).decode("utf-8", "ignore")


def matches_tokens(token_hits: dict[str, list[str]], mode: str) -> bool:
    if not token_hits:
        return True
    if mode == "all":
        return all(token_hits.values())
    return any(token_hits.values())


def summarize_zip(path: str, tokens: Iterable[str] | None = None) -> dict[str, object]:
    search_tokens = [token for token in (tokens or []) if token]

    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        sql_members = [name for name in members if name.endswith(".sql")]
        page_members = [
            name
            for name in members
            if "/application/pages/page_" in name and name.endswith(".sql")
        ]
        app_sql = next(
            name for name in members if name.endswith("/application/create_application.sql")
        )
        app_text = read_text(archive, app_sql)

        app_name_match = APP_NAME_RE.search(app_text)
        app_alias_match = APP_ALIAS_RE.search(app_text)

        create_calls: collections.Counter[str] = collections.Counter()
        plug_sources: collections.Counter[str] = collections.Counter()
        process_types: collections.Counter[str] = collections.Counter()
        page_names: list[str] = []
        token_hits: dict[str, list[str]] = {token: [] for token in search_tokens}

        for member in sql_members:
            text = read_text(archive, member)
            create_calls.update(call.lower() for call in CREATE_CALL_RE.findall(text))
            plug_sources.update(PLUG_SOURCE_RE.findall(text))
            process_types.update(PROCESS_TYPE_RE.findall(text))
            lowered = text.lower()
            for token in search_tokens:
                if token.lower() in lowered:
                    token_hits[token].append(member)
            if "/application/pages/" in member:
                page_match = PAGE_NAME_RE.search(text)
                if page_match:
                    page_names.append(page_match.group(1))

        return {
            "zip": os.path.basename(path),
            "app_name": app_name_match.group(1) if app_name_match else None,
            "alias": app_alias_match.group(1) if app_alias_match else None,
            "page_count": len(page_members),
            "shared_component_files": sum(
                1 for name in members if "/application/shared_components/" in name
            ),
            "supporting_object_files": sum(
                1 for name in members if "/supporting_objects/" in name
            ),
            "top_create_calls": create_calls.most_common(12),
            "plug_source_types": plug_sources.most_common(),
            "process_types": process_types.most_common(10),
            "page_names": page_names[:20],
            "token_hits": token_hits,
        }


def to_markdown(
    items: list[dict[str, object]], search_tokens: Iterable[str] | None = None
) -> str:
    search_tokens = [token for token in (search_tokens or []) if token]
    lines = []
    lines.append("# APEX Backup Analysis")
    lines.append("")
    lines.append("| Zip | App | Alias | Pages | Shared files | Supporting files | Main region types | Main process types |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- | --- |")
    for item in items:
        plug_sources = ", ".join(name for name, _ in item["plug_source_types"][:4]) or "-"
        processes = ", ".join(name for name, _ in item["process_types"][:4]) or "-"
        lines.append(
            "| {zip} | {app_name} | {alias} | {page_count} | {shared_component_files} | "
            "{supporting_object_files} | {plug_sources} | {processes} |".format(
                plug_sources=plug_sources,
                processes=processes,
                **item,
            )
        )

    lines.append("")
    lines.append("## Representative Pages")
    lines.append("")
    for item in items:
        lines.append(f"### {item['zip']} - {item['app_name']}")
        pages = ", ".join(item["page_names"][:10]) or "-"
        calls = ", ".join(f"{name} ({count})" for name, count in item["top_create_calls"][:6])
        lines.append(f"- Alias: `{item['alias']}`")
        lines.append(f"- Pages: `{item['page_count']}`")
        lines.append(f"- Representative pages: {pages}")
        lines.append(f"- Top create calls: {calls}")
        if search_tokens:
            lines.append("- Search hits:")
            for token in search_tokens:
                hits = item["token_hits"].get(token, [])
                rendered_hits = ", ".join(hits[:5]) or "-"
                lines.append(f"  - `{token}`: {rendered_hits}")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Directory that contains the f###.zip backups. Defaults to the current directory.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format. Defaults to markdown.",
    )
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help="Only keep backups whose SQL contains this token. Can be repeated.",
    )
    parser.add_argument(
        "--match-mode",
        choices=("any", "all"),
        default="any",
        help="How repeated --contains filters are applied. Defaults to any.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pattern = os.path.join(args.root, "f*.zip")
    paths = sorted(glob.glob(pattern))
    if not paths:
        print(f"No backups found for pattern: {pattern}", file=sys.stderr)
        return 1

    items = [summarize_zip(path, tokens=args.contains) for path in paths]
    if args.contains:
        items = [
            item
            for item in items
            if matches_tokens(item["token_hits"], args.match_mode)
        ]
    if args.format == "json":
        print(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(items, search_tokens=args.contains))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

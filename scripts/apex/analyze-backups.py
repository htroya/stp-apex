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
PAGE_ALIAS_RE = re.compile(r"create_page\(.*?p_alias=>'([^']+)'", re.S)
PAGE_FILE_RE = re.compile(r"page_(\d+)\.sql$", re.IGNORECASE)


def read_text(archive: zipfile.ZipFile, member: str) -> str:
    return archive.read(member).decode("utf-8", "ignore")


def shorten(name: str) -> str:
    return os.path.splitext(name)[0]


def normalize_shared_category(member: str) -> str:
    relative = member.split("/application/shared_components/", 1)[1]
    first = relative.split("/", 1)[0]
    return shorten(first)


def normalize_supporting_category(member: str) -> str:
    relative = member.split("/supporting_objects/", 1)[1]
    first = relative.split("/", 1)[0]
    return shorten(first)


def format_counter(counter_items: list[tuple[str, int]], limit: int = 6) -> str:
    if not counter_items:
        return "-"
    return ", ".join(f"{name} ({count})" for name, count in counter_items[:limit])


def matches_tokens(token_hits: dict[str, list[str]], mode: str) -> bool:
    if not token_hits:
        return True
    if mode == "all":
        return all(token_hits.values())
    return any(token_hits.values())


def infer_capability_tags(item: dict[str, object]) -> list[str]:
    plug_sources = {name for name, _ in item["plug_source_types"]}
    process_types = {name for name, _ in item["process_types"]}
    create_calls = {name for name, _ in item["top_create_calls"]}
    shared_categories = {name for name, _ in item["shared_component_categories"]}
    app_name = (item.get("app_name") or "").lower()

    tags: set[str] = set()

    if item["zip"] in {"f100.zip", "f101.zip"} or "login" in app_name:
        tags.update({"base-app", "login", "navigation"})
    if "blank page" in " ".join(page["name"].lower() for page in item["pages"] if page["name"]):
        tags.add("blank-page")
    if "NATIVE_IG" in plug_sources:
        tags.add("interactive-grid")
    if "NATIVE_IR" in plug_sources:
        tags.add("interactive-report")
    if "NATIVE_CARDS" in plug_sources:
        tags.add("cards")
    if "NATIVE_JET_CHART" in plug_sources or "jet_chart" in create_calls:
        tags.add("charts")
    if "NATIVE_MAP_REGION" in plug_sources or "map_region_layer" in create_calls:
        tags.add("maps")
    if "NATIVE_CSS_CALENDAR" in plug_sources:
        tags.add("calendar")
    if "NATIVE_JSTREE" in plug_sources:
        tags.add("trees")
    if "NATIVE_SEARCH_REGION" in plug_sources or "search_region_source" in create_calls:
        tags.add("search")
    if "NATIVE_DATA_LOADING" in process_types or "data_load_definitions" in shared_categories:
        tags.add("data-loading")
    if "NATIVE_IG_DML" in process_types:
        tags.add("editable-data")
    if "NATIVE_FORM_DML" in process_types or "NATIVE_FORM_PROCESS" in process_types:
        tags.add("forms")
    if "page_da_event" in create_calls or "page_da_action" in create_calls:
        tags.add("dynamic-actions")
    if "web_source_operation" in create_calls or "data_profiles" in shared_categories:
        tags.add("rest-data-sources")
    if "workflow_activity" in create_calls or "NATIVE_WORKFLOW" in process_types:
        tags.add("workflow")
    if "pwa_shortcut" in create_calls or "pwa" in shared_categories:
        tags.add("pwa")
    if "email" in shared_categories or "email" in app_name:
        tags.add("email")
    if "docgen" in app_name or "PLUGIN_COM.ORACLE.APEX.DOCGEN" in process_types:
        tags.add("document-generation")
    if "vector" in app_name or "ai_config" in shared_categories:
        tags.add("vector-search")
    if "collection" in app_name:
        tags.add("collections")
    if "file upload" in app_name or "download" in app_name:
        tags.add("file-transfer")
    if "master detail" in app_name:
        tags.add("master-detail")
    if "theme" in app_name or item["zip"] == "f115.zip":
        tags.add("theme-reference")

    return sorted(tags)


def summarize_zip(path: str, tokens: Iterable[str] | None = None) -> dict[str, object]:
    search_tokens = [token for token in (tokens or []) if token]

    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        sql_members = [name for name in members if name.endswith(".sql")]
        page_members = [
            name
            for name in members
            if "/application/pages/page_" in name
            and name.endswith(".sql")
            and not name.endswith("page_groups.sql")
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
        shared_categories: collections.Counter[str] = collections.Counter()
        supporting_categories: collections.Counter[str] = collections.Counter()
        token_hits: dict[str, list[str]] = {token: [] for token in search_tokens}
        pages: list[dict[str, object]] = []
        supporting_files: list[str] = []

        for member in members:
            if "/application/shared_components/" in member:
                shared_categories.update([normalize_shared_category(member)])
            if "/supporting_objects/" in member and member.endswith(".sql"):
                supporting_categories.update([normalize_supporting_category(member)])
                supporting_files.append(member)

        for member in sql_members:
            text = read_text(archive, member)
            create_calls.update(call.lower() for call in CREATE_CALL_RE.findall(text))
            plug_sources.update(PLUG_SOURCE_RE.findall(text))
            process_types.update(PROCESS_TYPE_RE.findall(text))

            lowered = text.lower()
            for token in search_tokens:
                if token.lower() in lowered:
                    token_hits[token].append(member)

            if member in page_members:
                page_name_match = PAGE_NAME_RE.search(text)
                page_alias_match = PAGE_ALIAS_RE.search(text)
                page_id_match = PAGE_FILE_RE.search(member)
                pages.append(
                    {
                        "file": member.split("/application/pages/", 1)[1],
                        "page_id": int(page_id_match.group(1)) if page_id_match else None,
                        "name": page_name_match.group(1) if page_name_match else None,
                        "alias": page_alias_match.group(1) if page_alias_match else None,
                    }
                )

        item = {
            "zip": os.path.basename(path),
            "app_name": app_name_match.group(1) if app_name_match else None,
            "alias": app_alias_match.group(1) if app_alias_match else None,
            "page_count": len(page_members),
            "shared_component_files": sum(
                1 for name in members if "/application/shared_components/" in name
            ),
            "supporting_object_files": len(supporting_files),
            "top_create_calls": create_calls.most_common(12),
            "plug_source_types": plug_sources.most_common(),
            "process_types": process_types.most_common(10),
            "shared_component_categories": shared_categories.most_common(12),
            "supporting_object_categories": supporting_categories.most_common(12),
            "supporting_object_names": [
                name.split("/supporting_objects/", 1)[1] for name in supporting_files[:12]
            ],
            "pages": pages,
            "token_hits": token_hits,
        }
        item["capability_tags"] = infer_capability_tags(item)
        return item


def render_pages(pages: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    if limit == 0:
        return pages
    return pages[:limit]


def to_markdown(
    items: list[dict[str, object]],
    search_tokens: Iterable[str] | None = None,
    page_limit: int = 10,
) -> str:
    search_tokens = [token for token in (search_tokens or []) if token]
    lines: list[str] = []

    lines.append("# APEX Backup Analysis")
    lines.append("")
    lines.append(
        "| Zip | App | Alias | Pages | Capabilities | Main region types | Main process types | Supporting |"
    )
    lines.append("| --- | --- | --- | ---: | --- | --- | --- | --- |")
    for item in items:
        plug_sources = ", ".join(name for name, _ in item["plug_source_types"][:4]) or "-"
        processes = ", ".join(name for name, _ in item["process_types"][:4]) or "-"
        capabilities = ", ".join(item["capability_tags"][:6]) or "-"
        supporting = format_counter(item["supporting_object_categories"], limit=4)
        lines.append(
            "| {zip} | {app_name} | {alias} | {page_count} | {capabilities} | "
            "{plug_sources} | {processes} | {supporting} |".format(
                capabilities=capabilities,
                plug_sources=plug_sources,
                processes=processes,
                supporting=supporting,
                **item,
            )
        )

    lines.append("")
    lines.append("## Backup Details")
    lines.append("")

    for item in items:
        lines.append(f"### {item['zip']} - {item['app_name']}")
        lines.append(f"- Alias: `{item['alias']}`")
        lines.append(f"- Pages: `{item['page_count']}`")
        lines.append(
            f"- Capability tags: {', '.join(f'`{tag}`' for tag in item['capability_tags']) or '-'}"
        )
        lines.append(
            f"- Main region types: {format_counter(item['plug_source_types'], limit=6)}"
        )
        lines.append(
            f"- Main process types: {format_counter(item['process_types'], limit=6)}"
        )
        lines.append(
            f"- Top create calls: {format_counter(item['top_create_calls'], limit=6)}"
        )
        lines.append(
            f"- Shared component categories: {format_counter(item['shared_component_categories'], limit=8)}"
        )
        lines.append(
            f"- Supporting object categories: {format_counter(item['supporting_object_categories'], limit=6)}"
        )
        lines.append(
            "- Supporting object files: "
            + (", ".join(f"`{name}`" for name in item["supporting_object_names"]) or "-")
        )
        lines.append("- Page index:")
        for page in render_pages(item["pages"], page_limit):
            alias = f" / `{page['alias']}`" if page["alias"] else ""
            lines.append(
                f"  - `{page['file']}` -> `{page['name']}`{alias}"
            )
        if page_limit and len(item["pages"]) > page_limit:
            lines.append(
                f"  - `...` ({len(item['pages']) - page_limit} additional pages omitted; use `--page-limit 0` to list all)"
            )
        if search_tokens:
            lines.append("- Search hits:")
            for token in search_tokens:
                hits = item["token_hits"].get(token, [])
                rendered_hits = ", ".join(hits[:8]) or "-"
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
    parser.add_argument(
        "--page-limit",
        type=int,
        default=10,
        help="How many pages to show per backup in markdown mode. Use 0 for all pages.",
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
        print(
            to_markdown(
                items,
                search_tokens=args.contains,
                page_limit=max(args.page_limit, 0),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

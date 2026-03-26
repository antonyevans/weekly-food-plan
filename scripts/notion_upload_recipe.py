#!/usr/bin/env python3
"""Upload a single recipe to the 'Family Recipes' Notion database.

This targets the database schema discovered from:
  https://www.notion.so/c3abae3069f9432089107078f4b6a5ca

Important: That database does NOT currently have text fields for full
"Ingredients" or "Instructions".

So by default this script:
- writes the recipe Name/metadata into database properties, AND
- appends the full Ingredients + Instructions into the page body as blocks.

Auth:
- Prefer NOTION_TOKEN env
- Else NOTION_API_KEY env
- Else /run/secrets/notion_api_key

Usage:
  python scripts/notion_upload_recipe.py --recipe-json /path/to/recipe.json

Optionally override:
  --database-id <id>
  --week-tag "Week of YYYY-MM-DD"

Recipe JSON shape (flexible):
{
  "title": "...",
  "servings": 4,
  "total_minutes": 35,
  "protein": "Chicken"|"Beef"|"Pork"|"Fish"|"Veg",
  "cuisine": "Italian"|"Mexican"|...,   (optional)
  "effort": "Easy"|"Medium"            (optional)
  "kid_friendly": true|false             (optional)
  "source": "Original"|"HelloFresh-style"|"Other" (optional)
  "store": "Wegmans"                    (optional)
  "tags": ["Weeknight", "One pan"],     (optional)
  "ingredients": ["...", ...] OR "...",
  "instructions": ["...", ...] OR "...",
  "notes": "..." (optional)
}
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

import requests

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
DEFAULT_DATABASE_ID = "c3abae30-69f9-4320-8910-7078f4b6a5ca"

# --- Notion property names in this database ---
PROP_NAME = "Name"  # title
PROP_SERVINGS = "Servings"  # number
PROP_TIME_MIN = "Time (min)"  # number
PROP_PROTEIN = "Protein"  # select
PROP_CUISINE = "Cuisine"  # select
PROP_EFFORT = "Effort"  # select
PROP_KID_FRIENDLY = "Kid-friendly"  # checkbox
PROP_SOURCE = "Source"  # select
PROP_STORE = "Store"  # select
PROP_TAGS = "Tags"  # multi_select
PROP_THIS_WEEK = "This week"  # checkbox

# Optional property (NOT currently present in your DB as of schema fetch)
# If you add a rich_text property called "Ingredients", the script will
# automatically populate it.
PROP_INGREDIENTS = "Ingredients"  # rich_text


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def read_token() -> Optional[str]:
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if token:
        return token.strip()
    p = "/run/secrets/notion_api_key"
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def notion_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def rt(text: str) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}}]


def title_val(text: str) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}}]


def to_select(name: Optional[str]) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    return {"select": {"name": name}}


def to_multi_select(names: List[str]) -> Dict[str, Any]:
    return {"multi_select": [{"name": n} for n in names if n]}


def to_number(n: Any) -> Optional[Dict[str, Any]]:
    if n is None or n == "":
        return None
    return {"number": float(n)}


def normalize_recipe(raw: Dict[str, Any]) -> Dict[str, Any]:
    title = raw.get("title") or raw.get("name")
    if not title:
        raise ValueError("recipe JSON must include 'title' (or 'name')")

    ingredients = raw.get("ingredients")
    if isinstance(ingredients, list):
        ingredients_text = "\n".join(str(x) for x in ingredients)
    else:
        ingredients_text = str(ingredients) if ingredients is not None else ""

    instructions = raw.get("instructions") or raw.get("steps")
    if isinstance(instructions, list):
        instructions_text = "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(instructions)
        )
    else:
        instructions_text = str(instructions) if instructions is not None else ""

    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif not isinstance(tags, list):
        tags = [str(tags)]

    return {
        "title": str(title),
        "servings": raw.get("servings"),
        "total_minutes": raw.get("total_minutes") or raw.get("total_time_minutes"),
        "protein": raw.get("protein"),
        "cuisine": raw.get("cuisine"),
        "effort": raw.get("effort"),
        "kid_friendly": raw.get("kid_friendly"),
        "source": raw.get("source"),
        "store": raw.get("store"),
        "tags": [str(t) for t in tags],
        "ingredients_text": ingredients_text,
        "instructions_text": instructions_text,
        "notes": str(raw.get("notes") or ""),
    }


def build_page_create_payload(
    database_id: str,
    r: Dict[str, Any],
    week_tag: Optional[str],
    mark_this_week: bool,
    schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        PROP_NAME: {"title": title_val(r["title"])},
    }

    # Optional: write Ingredients into a rich_text property if it exists and is the right type.
    if schema:
        db_props = (schema.get("properties") or {})
        ing = db_props.get(PROP_INGREDIENTS)
        if ing and ing.get("type") == "rich_text":
            props[PROP_INGREDIENTS] = {"rich_text": rt(r.get("ingredients_text", ""))}

    n = to_number(r.get("servings"))
    if n:
        props[PROP_SERVINGS] = n

    n = to_number(r.get("total_minutes"))
    if n:
        props[PROP_TIME_MIN] = n

    sel = to_select(r.get("protein"))
    if sel:
        props[PROP_PROTEIN] = sel

    sel = to_select(r.get("cuisine"))
    if sel:
        props[PROP_CUISINE] = sel

    sel = to_select(r.get("effort"))
    if sel:
        props[PROP_EFFORT] = sel

    if r.get("kid_friendly") is not None:
        props[PROP_KID_FRIENDLY] = {"checkbox": bool(r.get("kid_friendly"))}

    sel = to_select(r.get("source"))
    if sel:
        props[PROP_SOURCE] = sel

    sel = to_select(r.get("store"))
    if sel:
        props[PROP_STORE] = sel

    tags = list(r.get("tags") or [])
    if week_tag:
        tags.append(week_tag)
    if tags:
        props[PROP_TAGS] = to_multi_select(tags)

    if mark_this_week:
        props[PROP_THIS_WEEK] = {"checkbox": True}

    # Page content blocks: Ingredients + Instructions + Notes
    children: List[Dict[str, Any]] = []

    def heading(text: str) -> Dict[str, Any]:
        return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(text)}}

    def paragraph(text: str) -> Dict[str, Any]:
        # Notion has max length per rich text; chunk if needed.
        return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}

    def chunk_text(s: str, limit: int = 1800) -> List[str]:
        s = s or ""
        if len(s) <= limit:
            return [s]
        out = []
        i = 0
        while i < len(s):
            out.append(s[i:i+limit])
            i += limit
        return out

    children.append(heading("Ingredients"))
    for chunk in chunk_text(r.get("ingredients_text", "")):
        children.append(paragraph(chunk))

    children.append(heading("Instructions"))
    for chunk in chunk_text(r.get("instructions_text", "")):
        children.append(paragraph(chunk))

    if r.get("notes"):
        children.append(heading("Notes"))
        for chunk in chunk_text(r.get("notes", "")):
            children.append(paragraph(chunk))

    return {
        "parent": {"database_id": database_id},
        "properties": props,
        "children": children,
    }


def get_database_schema(token: str, database_id: str) -> Dict[str, Any]:
    """Fetch database schema so we can safely write optional properties."""
    url = f"{NOTION_API_BASE}/databases/{database_id.replace('-', '')}"
    resp = requests.get(url, headers=notion_headers(token), timeout=30)
    if resp.status_code >= 400:
        eprint(f"Notion API error fetching schema {resp.status_code}:")
        try:
            eprint(json.dumps(resp.json(), indent=2))
        except Exception:
            eprint(resp.text)
        resp.raise_for_status()
    return resp.json()


def create_page(token: str, payload: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
    if dry_run:
        return {"dry_run": True, "payload": payload}

    resp = requests.post(
        f"{NOTION_API_BASE}/pages",
        headers=notion_headers(token),
        data=json.dumps(payload),
        timeout=30,
    )

    if resp.status_code >= 400:
        eprint(f"Notion API error {resp.status_code}:")
        try:
            eprint(json.dumps(resp.json(), indent=2))
        except Exception:
            eprint(resp.text)
        resp.raise_for_status()

    return resp.json()


def default_week_tag() -> str:
    # Matches your DB convention: "Week of YYYY-MM-DD"
    today = dt.date.today().isoformat()
    return f"Week of {today}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-id", default=DEFAULT_DATABASE_ID)
    ap.add_argument("--recipe-json", required=True)
    ap.add_argument("--week-tag", default=None, help="e.g., 'Week of 2026-03-23' (defaults to today)")
    ap.add_argument("--no-week-tag", action="store_true")
    ap.add_argument("--mark-this-week", action="store_true", help="Set 'This week' checkbox")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = read_token()
    if not token:
        eprint("No Notion token found. Set NOTION_TOKEN/NOTION_API_KEY or mount /run/secrets/notion_api_key")
        return 2

    with open(args.recipe_json, "r", encoding="utf-8") as f:
        raw = json.load(f)

    recipe = normalize_recipe(raw)

    week_tag = None if args.no_week_tag else (args.week_tag or default_week_tag())

    schema = None
    try:
        schema = get_database_schema(token, args.database_id)
    except Exception as ex:
        # Non-fatal: we can still create the page with required properties.
        eprint(f"Warning: could not fetch schema; skipping optional properties ({ex})")

    payload = build_page_create_payload(
        database_id=args.database_id,
        r=recipe,
        week_tag=week_tag,
        mark_this_week=bool(args.mark_this_week),
        schema=schema,
    )

    result = create_page(token, payload, dry_run=bool(args.dry_run))
    print(json.dumps(result, indent=2))

    if not args.dry_run and isinstance(result, dict) and result.get("url"):
        eprint(f"Created: {result['url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

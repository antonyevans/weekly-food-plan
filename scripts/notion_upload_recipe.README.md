# Upload one recipe to the Family Recipes Notion database

Database: **Family Recipes** (`c3abae3069f9432089107078f4b6a5ca`)

## Key point about your schema

Your Notion database currently has **no** dedicated properties for full-text **Ingredients** or **Instructions**.

So the uploader does:
- Put metadata in database properties (Name, Servings, Time (min), Protein, Tags, etc.)
- Put the full Ingredients + Instructions (and Notes) into the **page body** as blocks.

If you *want* ingredients as a searchable property, add a Rich text property:
- `Ingredients` (rich_text)

This uploader will automatically detect it and populate it **in addition to** putting ingredients in the page body.

(Instructions remain in the page body.)

## Install

```bash
cd /var/lib/openclaw/workspace/skills/weekly-food-plan
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Recipe JSON

See `scripts/recipe.example.json`.

## Dry run (recommended)

```bash
python3 scripts/notion_upload_recipe.py \
  --recipe-json scripts/recipe.example.json \
  --dry-run
```

## Create the page

```bash
python3 scripts/notion_upload_recipe.py \
  --recipe-json scripts/recipe.example.json
```

## Optional flags

- `--week-tag "Week of YYYY-MM-DD"` (otherwise defaults to today)
- `--no-week-tag`
- `--mark-this-week` (checks the `This week` checkbox)

## Field mapping used

Properties in your DB:
- Name (title)
- Servings (number)
- Time (min) (number)
- Protein (select: Chicken/Beef/Pork/Fish/Veg)
- Cuisine (select)
- Effort (select: Easy/Medium)
- Kid-friendly (checkbox)
- Source (select)
- Store (select)
- Tags (multi_select)
- This week (checkbox)

Ingredients/Instructions are stored in the **page content**.

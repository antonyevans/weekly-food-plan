# Recipe sink adapters (publish recipes somewhere phone-accessible)

Goal: create a single “Week of YYYY-MM-DD” container and publish recipe cards into it.

## Universal recipe card fields
- Title
- Servings
- Total time
- Ingredients (with quantities)
- Steps
- Notes (kid-friendly tweaks, make-ahead, leftovers)
- Source link (optional)

## Notion

### API (preferred when available)
- Use a Notion integration token (env `NOTION_TOKEN` / `NOTION_API_KEY`, or `/run/secrets/notion_api_key`).
- Dump schema (helps map property names/types):
  - `node scripts/notion_schema.js --database-id <dbid>`
- Upload one recipe into the Family Recipes database and store full ingredients/instructions in the **page body**:
  - `node scripts/notion_upload_recipe.js --recipe-json scripts/recipe.json --mark-this-week`
  - or `python scripts/notion_upload_recipe.py ...` when Python is available.

### Browser fallback
- If API auth fails, use logged-in Notion in browser and create a “Week of YYYY-MM-DD” page and paste recipe cards.

## Google Drive / Google Docs (example)
- Create a folder “Cooking/Week of YYYY-MM-DD”.
- Create one Google Doc per recipe (or one doc with headings, if user prefers).
- Share/access: ensure user can open on phone.

## Apple Notes (example)
- Create a folder “Cooking”.
- Create a note “Week of YYYY-MM-DD” with each recipe under a heading.

## Output requirements
- Provide a link to the container (folder/page/note) if available.
- Confirm count of recipes published.

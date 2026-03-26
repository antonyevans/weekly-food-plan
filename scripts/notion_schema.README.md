# Notion schema dump (for mapping recipe fields)

This prints the property names + types for a Notion database so we can map:
- title/name
- ingredients
- instructions
- tags
- source URL
- etc.

## Run

```bash
cd /var/lib/openclaw/workspace/skills/weekly-food-plan
node scripts/notion_schema.js --database-id "<DATABASE_ID>"
```

Auth lookup order:
1) `NOTION_TOKEN`
2) `NOTION_API_KEY`
3) `/run/secrets/notion_api_key`

If you paste a full Notion database URL, extract the database id (32 hex chars) from it.

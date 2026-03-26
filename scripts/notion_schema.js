#!/usr/bin/env node
/**
 * Print Notion database schema (properties + types).
 *
 * Auth precedence:
 *   1) NOTION_TOKEN env
 *   2) NOTION_API_KEY env
 *   3) /run/secrets/notion_api_key
 *
 * Usage:
 *   node scripts/notion_schema.js --database-id <id>
 */

const fs = require('fs');

function getArg(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1) return null;
  return process.argv[idx + 1] || null;
}

function readToken() {
  if (process.env.NOTION_TOKEN) return process.env.NOTION_TOKEN.trim();
  if (process.env.NOTION_API_KEY) return process.env.NOTION_API_KEY.trim();
  const p = '/run/secrets/notion_api_key';
  if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').trim();
  return null;
}

async function main() {
  const databaseId = getArg('--database-id');
  if (!databaseId) {
    console.error('Missing --database-id');
    process.exit(2);
  }

  const token = readToken();
  if (!token) {
    console.error('No Notion token found. Set NOTION_TOKEN/NOTION_API_KEY or mount /run/secrets/notion_api_key');
    process.exit(2);
  }

  const url = `https://api.notion.com/v1/databases/${databaseId.replace(/-/g, '')}`;

  const resp = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Notion-Version': '2022-06-28',
    },
  });

  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }

  if (!resp.ok) {
    console.error(`Notion API error ${resp.status}`);
    console.error(JSON.stringify(data, null, 2));
    process.exit(1);
  }

  const props = data.properties || {};
  const out = Object.entries(props)
    .sort((a,b) => a[0].localeCompare(b[0]))
    .map(([name, def]) => ({
      name,
      type: def.type,
      id: def.id,
      // useful hints for select/multi_select
      options: (def.type === 'select' && def.select && def.select.options)
        ? def.select.options.map(o => o.name)
        : (def.type === 'multi_select' && def.multi_select && def.multi_select.options)
          ? def.multi_select.options.map(o => o.name)
          : undefined,
    }));

  console.log(JSON.stringify({
    database_id: data.id,
    title: (data.title || []).map(t => t.plain_text).join(''),
    properties: out,
  }, null, 2));
}

main().catch((err) => {
  console.error('Unhandled error:', err);
  process.exit(1);
});

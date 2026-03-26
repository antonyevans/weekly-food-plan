#!/usr/bin/env node
/**
 * Upload one recipe to the Family Recipes Notion database.
 *
 * Why Node?
 * - This runtime has Node available by default; Python may not be installed.
 *
 * Behavior:
 * - Writes metadata to DB properties.
 * - Writes full Ingredients + Instructions (+ Notes) into the page body.
 * - If the DB has a rich_text property named "Ingredients", also fills it.
 *
 * Auth precedence:
 *  1) NOTION_TOKEN env
 *  2) NOTION_API_KEY env
 *  3) /run/secrets/notion_api_key
 */

const fs = require('fs');

const NOTION_VERSION = '2022-06-28';
const DEFAULT_DATABASE_ID = 'c3abae3069f9432089107078f4b6a5ca';

const PROP = {
  NAME: 'Name',
  SERVINGS: 'Servings',
  TIME_MIN: 'Time (min)',
  PROTEIN: 'Protein',
  CUISINE: 'Cuisine',
  EFFORT: 'Effort',
  KID_FRIENDLY: 'Kid-friendly',
  SOURCE: 'Source',
  STORE: 'Store',
  TAGS: 'Tags',
  THIS_WEEK: 'This week',
  INGREDIENTS: 'Ingredients', // optional rich_text
};

function getArg(name, fallback = null) {
  const i = process.argv.indexOf(name);
  if (i === -1) return fallback;
  return process.argv[i + 1] ?? fallback;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function readToken() {
  if (process.env.NOTION_TOKEN) return process.env.NOTION_TOKEN.trim();
  if (process.env.NOTION_API_KEY) return process.env.NOTION_API_KEY.trim();
  const p = '/run/secrets/notion_api_key';
  if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').trim();
  return null;
}

function richText(text) {
  return [{ type: 'text', text: { content: text || '' } }];
}

function titleText(text) {
  return [{ type: 'text', text: { content: text } }];
}

function toSelect(name) {
  if (!name) return null;
  return { select: { name } };
}

function toMultiSelect(arr) {
  return { multi_select: (arr || []).filter(Boolean).map(name => ({ name })) };
}

function toNumber(n) {
  if (n === undefined || n === null || n === '') return null;
  const f = Number(n);
  if (Number.isNaN(f)) return null;
  return { number: f };
}

function normalizeRecipe(raw) {
  const title = raw.title || raw.name;
  if (!title) throw new Error("recipe JSON must include 'title' (or 'name')");

  const ingredients = raw.ingredients;
  const ingredients_text = Array.isArray(ingredients)
    ? ingredients.map(String).join('\n')
    : (ingredients ?? '') + '';

  const inst = raw.instructions || raw.steps;
  const instructions_text = Array.isArray(inst)
    ? inst.map((s, idx) => `${idx + 1}. ${s}`).join('\n')
    : (inst ?? '') + '';

  let tags = raw.tags || [];
  if (typeof tags === 'string') tags = tags.split(',').map(s => s.trim()).filter(Boolean);
  if (!Array.isArray(tags)) tags = [String(tags)];

  return {
    title: String(title),
    servings: raw.servings,
    total_minutes: raw.total_minutes ?? raw.total_time_minutes,
    protein: raw.protein,
    cuisine: raw.cuisine,
    effort: raw.effort,
    kid_friendly: raw.kid_friendly,
    source: raw.source,
    store: raw.store,
    tags: tags.map(String),
    ingredients_text,
    instructions_text,
    notes: String(raw.notes || ''),
  };
}

async function notionFetch(url, token, init = {}) {
  const resp = await fetch(url, {
    ...init,
    headers: {
      ...(init.headers || {}),
      Authorization: `Bearer ${token}`,
      'Notion-Version': NOTION_VERSION,
      'Content-Type': 'application/json',
    },
  });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!resp.ok) {
    const err = new Error(`Notion API error ${resp.status}`);
    err.data = data;
    throw err;
  }
  return data;
}

function chunk(s, limit = 1800) {
  s = s || '';
  const out = [];
  for (let i = 0; i < s.length; i += limit) out.push(s.slice(i, i + limit));
  return out.length ? out : [''];
}

async function main() {
  const databaseId = (getArg('--database-id', DEFAULT_DATABASE_ID) || '').trim();
  const recipeJsonPath = getArg('--recipe-json');
  if (!recipeJsonPath) {
    console.error('Missing --recipe-json');
    process.exit(2);
  }

  const dryRun = hasFlag('--dry-run');
  const markThisWeek = hasFlag('--mark-this-week');
  const weekTag = hasFlag('--no-week-tag')
    ? null
    : (getArg('--week-tag') || `Week of ${new Date().toISOString().slice(0,10)}`);

  const token = readToken();
  if (!token) {
    console.error('No Notion token found (NOTION_TOKEN/NOTION_API_KEY or /run/secrets/notion_api_key)');
    process.exit(2);
  }

  const raw = JSON.parse(fs.readFileSync(recipeJsonPath, 'utf8'));
  const r = normalizeRecipe(raw);

  const db = await notionFetch(`https://api.notion.com/v1/databases/${databaseId.replace(/-/g,'')}`, token);
  const dbProps = db.properties || {};

  const props = {};
  props[PROP.NAME] = { title: titleText(r.title) };

  const nServ = toNumber(r.servings); if (nServ) props[PROP.SERVINGS] = nServ;
  const nTime = toNumber(r.total_minutes); if (nTime) props[PROP.TIME_MIN] = nTime;

  const selProtein = toSelect(r.protein); if (selProtein) props[PROP.PROTEIN] = selProtein;
  const selCuisine = toSelect(r.cuisine); if (selCuisine) props[PROP.CUISINE] = selCuisine;
  const selEffort = toSelect(r.effort); if (selEffort) props[PROP.EFFORT] = selEffort;

  if (r.kid_friendly !== undefined && r.kid_friendly !== null) {
    props[PROP.KID_FRIENDLY] = { checkbox: !!r.kid_friendly };
  }

  const selSource = toSelect(r.source); if (selSource) props[PROP.SOURCE] = selSource;
  const selStore = toSelect(r.store); if (selStore) props[PROP.STORE] = selStore;

  const tags = [...(r.tags || [])];
  if (weekTag) tags.push(weekTag);
  if (tags.length) props[PROP.TAGS] = toMultiSelect(tags);
  if (markThisWeek) props[PROP.THIS_WEEK] = { checkbox: true };

  if (dbProps[PROP.INGREDIENTS] && dbProps[PROP.INGREDIENTS].type === 'rich_text') {
    props[PROP.INGREDIENTS] = { rich_text: richText(r.ingredients_text) };
  }

  const children = [];
  const heading2 = (t) => ({ object: 'block', type: 'heading_2', heading_2: { rich_text: richText(t) } });
  const para = (t) => ({ object: 'block', type: 'paragraph', paragraph: { rich_text: richText(t) } });

  children.push(heading2('Ingredients'));
  for (const c of chunk(r.ingredients_text)) children.push(para(c));

  children.push(heading2('Instructions'));
  for (const c of chunk(r.instructions_text)) children.push(para(c));

  if (r.notes) {
    children.push(heading2('Notes'));
    for (const c of chunk(r.notes)) children.push(para(c));
  }

  const payload = {
    parent: { database_id: databaseId },
    properties: props,
    children,
  };

  if (dryRun) {
    console.log(JSON.stringify({ dry_run: true, payload }, null, 2));
    return;
  }

  const page = await notionFetch('https://api.notion.com/v1/pages', token, {
    method: 'POST',
    body: JSON.stringify(payload),
  });

  console.log(JSON.stringify(page, null, 2));
  if (page.url) console.error(`Created: ${page.url}`);
}

main().catch((err) => {
  console.error(err?.message || String(err));
  if (err?.data) console.error(JSON.stringify(err.data, null, 2));
  process.exit(1);
});

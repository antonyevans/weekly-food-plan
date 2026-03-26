---
name: weekly-food-plan
description: Create a weekly meal plan, propose recipes, collect explicit human approval, then automate grocery-cart entry in a user’s preferred online grocery store via logged-in browser and upload/save recipes to a phone-accessible system (e.g., Notion, Google Docs/Drive, Apple Notes). Use for: meal planning, recipe selection, consolidated grocery lists, adding items to an online cart, and publishing recipes to a chosen notes system. Do NOT use for: restaurant recommendations, nutrition coaching/macros-only planning without recipes, or one-off cooking questions unrelated to a weekly plan.
---

# Weekly Food Plan (packaged, reusable)

## Operating rules (non-negotiable)
1) Require explicit user approval before any browser automation that adds items to a cart or uploads/publishes recipes.
2) Use progressive disclosure: keep this file as the workflow “spine”. Read adapter/reference files only when needed.
3) Use the templates in `assets/` to format outputs.

## Inputs to collect (ask only for missing pieces)
- Planning window (e.g., 5 dinners, 7 dinners, include lunches?)
- Household + servings
- Constraints (dietary, allergies, dislikes)
- Weeknight cook-time limit and equipment constraints
- Budget sensitivity (low/medium/high)
- Leftovers preference (none/some/heavy)
- Grocery store provider (for cart automation)
- Recipe destination provider (for recipe publishing)

If the user has no preferences, default to: 4 dinners, 2 servings, <=35 minutes weeknights, moderate budget, some leftovers.

## Workflow

### Step 0) First-run onboarding (only if config is missing)
1) If a complete config is not available yet, run onboarding.
2) Read `references/user-config.schema.md` and collect only the required fields:
   - dinnersPerWeek, servings (or household size), maxWeeknightMinutes
   - allergies/dislikes/dietaryStyle
   - leftoversPreference, budget, kidFriendly
   - storeProvider (support Wegmans and Whole Foods (Amazon pickup) as first-class), storeLocation if needed
   - substitutionsOk
   - recipeSinkProvider + destinationIdOrUrl
   - weeklyRunDay, weeklyRunTime, weeklyRunTimezone (fixed weekly time)
3) Confirm the config back to the user in 5 to 10 bullets.
4) Ask if any pantry staples should be assumed (or if the user wants a “staples check” section in the grocery list).

### Step 1) Propose week 1 plan (no automation)
1) Draft a weekly plan using `assets/meal-plan.template.md`.
2) Produce recipe cards using `assets/recipe-card.template.md`.
3) Produce a consolidated grocery list using `assets/grocery-list.template.md`.
4) If there are options or uncertainty, offer 2 variants (e.g., “quick week” vs “more adventurous”) but keep it compact.

**Novice-friendly cooking requirement:**
- Assume the user may be a novice cook unless they say otherwise.
- In every recipe card, include:
  - clear oven/stovetop settings (temps, rack position)
  - what prep actually means (e.g., “trim asparagus: snap off woody ends”)
  - visual doneness cues (e.g., salmon flakes easily; potatoes fork-tender)
  - timing checkpoints and what to do while waiting
  - “common mistakes” notes (overcooking salmon, crowding the pan, under-seasoning)
  - kid-friendly serving suggestions (sauce on side, mild seasonings)

### Step 3) Approval gate (hard stop)
1) Ask the user to reply with one of:
   - `APPROVE`
   - “Swap X for Y”
   - “Remove recipe Z”
   - “Change servings to N”
2) Do not proceed until the user explicitly approves.

### Step 4) Add groceries to cart (browser automation)
1) Read `references/grocery-adapters.md`.
2) Select the correct adapter for the user’s store.
3) Use the logged-in browser to add items with quantities.
4) Apply substitution policy from config.
5) If login, store selection, or delivery/pickup selection blocks progress, stop and ask the user for the minimal action needed.

**Wegmans reliability notes (from real runs):**
- Prefer driving a **single, already-attached Browser Relay tab**.
- Avoid opening new tabs mid-flow.
- If you see **"tab not found"**, ask user to toggle Relay OFF/ON on that tab, then continue.
- Prefer DOM-driven clicks (e.g., match `button` by aria-label "Add … to cart") over brittle role refs.

### Step 5) Publish recipes to the user’s system
1) Read `references/recipe-sink-adapters.md`.
2) Publish each recipe card to the chosen destination.
3) Create a single “Week of YYYY-MM-DD” container (page/folder/note) and store all recipes there.

**Notion (API) quick path (when configured):**
- Schema: `node scripts/notion_schema.js --database-id <dbid>`
- Upload: `node scripts/notion_upload_recipe.js --recipe-json <file> --mark-this-week`

### Step 6) Confirm and archive
1) Provide:
   - Cart link (or instructions to find it)
   - Destination link (Notion page / Drive folder / etc.)
   - List of any items skipped or substituted
2) Save the resolved config and “favorites” list (store this as a short summary in the destination system if available).

### Step 7) Set weekly cadence (schedule from onboarding)
1) Use the onboarding fields weeklyRunDay, weeklyRunTime, weeklyRunTimezone.
2) If the runtime supports scheduling, create a weekly schedule using the platform’s scheduler.
3) Confirm the schedule back to the user.

## Error handling
Read `references/error-handling.md` when:
- an item can’t be found
- the store site UI changes
- login/store selection blocks automation
- uploads fail or destination permissions are unclear

## Concrete examples (for discovery)
Should trigger:
- “Plan 5 dinners this week, then add everything to my grocery cart and put the recipes in Notion.”
- “Make a kid-friendly weekly meal plan and build the cart for Walmart pickup.”
- “I want a HelloFresh-style week but cheaper, and I need the grocery list added to my Instacart cart.”

Should NOT trigger:
- “What can I cook with chicken thighs tonight?”
- “Give me macro targets for a cut.”
- “Recommend restaurants near me.”

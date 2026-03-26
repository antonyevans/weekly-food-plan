# weekly-food-plan (OpenClaw skill)

A reusable OpenClaw / AgentSkills-compatible skill that:

- drafts a weekly meal plan + recipe cards + consolidated grocery list
- **requires explicit approval** before any automation
- can automate adding items to an online grocery cart (via a logged-in browser)
- can publish recipes to a notes system (Notion adapters included)

> Skill entrypoint: `SKILL.md`

## What you get

- `SKILL.md` – the workflow spine (onboarding → plan → approval gate → cart automation → publish → scheduling)
- `assets/` – output templates (meal plan, recipe cards, grocery list)
- `references/` – adapters + error-handling notes
- `scripts/` – optional helpers for Notion schema + recipe upload

## Install

Pick **one** of these options.

### Option A: Install for all OpenClaw workspaces (recommended)

Clone into your managed skills directory:

```bash
mkdir -p ~/.openclaw/skills
cd ~/.openclaw/skills
git clone https://github.com/antonyevans/weekly-food-plan.git weekly-food-plan
```

Restart OpenClaw (or start a new chat/session) so it reloads skills.

### Option B: Install into a single workspace

Clone into your specific OpenClaw workspace:

```bash
cd /path/to/your/openclaw/workspace
mkdir -p skills
git clone https://github.com/antonyevans/weekly-food-plan.git skills/weekly-food-plan
```

Restart OpenClaw (or start a new chat/session).

### Option C: Install in Claude Code / Codex (AgentSkills-compatible)

This repo is **AgentSkills-compatible**: the skill is the folder that contains `SKILL.md` at its root.

Most “coding agent” runtimes (including Claude Code and Codex) support *either* (a) AgentSkills directly, or (b) a “skills/prompts” folder you can point at.

Generic install steps:

1) Clone the repo anywhere convenient:

```bash
git clone https://github.com/antonyevans/weekly-food-plan.git
```

2) Configure your agent tool to load skills from that folder **or** copy/link it into the tool’s skills directory so the path looks like:

```text
<your-skills-dir>/weekly-food-plan/SKILL.md
```

3) Restart the tool / start a new session so it reindexes skills.

If your Claude Code / Codex setup expects a different skills directory convention, tell me what it’s using and I’ll tailor the instructions.

## Use

In chat, ask something like:

- “Plan 5 dinners this week, then add everything to my grocery cart and put the recipes in Notion.”
- “Make a kid-friendly weekly meal plan for 4 and give me a consolidated grocery list.”

The skill will:

1. collect missing preferences (servings, time limits, allergies, store, etc.)
2. propose the plan + grocery list (no automation)
3. stop and wait for you to reply **APPROVE** (or edits)
4. only then automate cart entry / publishing

## Notes / prerequisites

- **Browser cart automation** requires that your OpenClaw setup supports browser control and you are logged in to your store site in that browser.
- **Notion publishing** uses scripts under `scripts/` (Node + optional Python). You can ignore these if you don’t use Notion.

## License

MIT (see `LICENSE`).

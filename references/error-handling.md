# Error handling and fallbacks

## Login / access blockers
- If the site requires login and the agent cannot proceed, stop and ask the user to login in the attached/active browser tab.
- If the wrong store/location is selected, stop and ask the user to pick the correct store.

## Missing items
- If substitutionsOk=yes: choose closest substitute and record it.
- If substitutionsOk=no: leave un-added and record it under “Needs human pick”.

## Quantity ambiguity
- Prefer common retail units (1 bunch, 1 lb, 1 jar).
- If a recipe needs an unusual amount, round up to a purchasable package size.

## UI changes
- If selectors/labels differ, fall back to the universal add-item algorithm in `references/grocery-adapters.md`.

## Partial success reporting
Always return:
- Added
- Substituted
- Skipped/needs human
- Next action required (if any)

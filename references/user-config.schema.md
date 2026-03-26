# User configuration schema (minimal, extendable)

Use this as a checklist. Store it wherever the user prefers (Notion, a note, etc.).

## Planning defaults
- dinnersPerWeek:
- servings:
- maxWeeknightMinutes:
- leftoversPreference: none | some | heavy
- budget: low | medium | high

## Food constraints
- allergies:
- dislikes:
- dietaryStyle: none | vegetarian | pescatarian | keto | halal | etc.
- kidFriendly: yes/no

## Grocery store (browser automation)
- storeProvider: (examples) instacart | walmart | kroger | wegmans | amazon-wholefoods | heb | tesco | other
- storeLocation: zip/city (if needed for store selection)
- substitutionsOk: yes/no
- brandPreference: (optional)

## Recipe destination (publishing)
- recipeSinkProvider: notion | google-drive | google-docs | apple-notes | obsidian | other
- destinationIdOrUrl: (page URL, folder URL, etc.)

## Weekly cadence (fixed)
- weeklyRunDay: (Mon/Tue/Wed/Thu/Fri/Sat/Sun)
- weeklyRunTime: (e.g., 09:00)
- weeklyRunTimezone: (e.g., America/New_York)

## Notes
- If the user can’t provide destinationIdOrUrl, create a new top-level container named "Cooking" or "Family Recipes" in their chosen system and use it.

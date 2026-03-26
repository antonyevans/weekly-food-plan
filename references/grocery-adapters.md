# Grocery store adapters (browser automation playbooks)

Goal: add the consolidated list to an online cart using a logged-in browser.

## Universal preflight (all stores)
1) Confirm user is logged in.
2) Confirm delivery vs pickup mode (if applicable) and that a store/location is selected.
3) If any preflight fails, STOP and ask user to fix it.

## Universal add-item algorithm
For each grocery item:
1) Search by the most specific term first (e.g., “thin sliced chicken breast cutlets”).
2) If multiple results:
   - Prefer the closest match to the ingredient form (cutlets vs whole breast).
   - Prefer the smallest package that meets quantity unless config says value-size.
3) Set quantity.
4) If item not found:
   - If substitutionsOk=yes, pick the closest reasonable substitute and record it.
   - If substitutionsOk=no, record as “needs human pick”.

## Store-specific notes

### Instacart (example)
- Preconditions: delivery address + retailer chosen.
- Pattern: search -> select item -> add -> adjust qty in cart.

### Walmart (example)
- Preconditions: pickup/delivery selected and store set.
- Pattern: search -> Add -> open cart to adjust weights/qty as needed.

### Kroger (example)
- Preconditions: store selected; pickup/delivery chosen.
- Pattern: search -> Add -> sometimes requires choosing brand/size.

### Wegmans (first-class)

#### Preconditions
- User is logged in
- Correct store selected (if prompted)
- Delivery vs pickup chosen (if prompted)

#### Browser Relay stability (important)
- Prefer working in **one already-attached tab**.
- Avoid opening new tabs/windows during automation; Wegmans can invalidate the Relay target.
- If the tool starts returning **"tab not found"** mid-run:
  1) Ask user to toggle Relay OFF/ON on the current tab
  2) Ask user to paste the current URL
  3) Continue in that same tab

#### Navigation + add-item pattern
1) Navigate in-place to `https://www.wegmans.com/shop/search?query=<url-encoded>`.
2) Prefer clicking "Add … to cart" buttons by **aria-label text** (DOM `button[aria-label*="Add"]`) instead of brittle role refs.
3) For produce (lemons, garlic bulbs), re-click the same Add button to increment quantity.
4) After adding several items, navigate to `https://www.wegmans.com/cart` and verify cart count/subtotal changed.

#### Selecting the right product
- Avoid prepared-meal items (e.g., **Gold Pan**, **Ready to Cook**) when the intent is raw ingredients.
- For ambiguous queries, prefer:
  - fresh vs frozen (unless requested)
  - plain/unflavored for yogurt
  - whole garlic (bulk/1 bulb) rather than garlic powder

#### Removing mistakes
- Use the cart page remove control (often "Remove <item> from the cart"); confirm deletion in modal ("Yes, delete item").

#### Example items successfully added in a prior session
- salmon fillet, asparagus, baby potatoes, lemons, dijon mustard, garlic bulb, plain Greek yogurt

### Whole Foods via Amazon (pickup) (first-class)
- Preconditions:
  - Logged in to Amazon
  - Shopping mode is set to Whole Foods (not standard Amazon shipping)
  - Pickup is selected (not delivery)
  - Pickup store/location is selected
  - If Amazon requires scheduling a pickup window, ensure one is selected
- Navigation pattern:
  1) Ensure you are in the Whole Foods storefront with pickup enabled.
  2) Search item.
  3) If multiple variants (organic/non-organic, different weights), pick the closest match to the recipe and the smallest package that meets quantity.
  4) Click Add.
  5) Open cart to adjust quantities and confirm updates.
- Common blockers:
  - If Amazon prompts for pickup location or a pickup window, STOP and ask the user to complete that step.

## Output requirements
- Return a short summary:
  - Added successfully (count)
  - Substituted (list)
  - Not found / needs human pick (list)
  - Cart link (if available)

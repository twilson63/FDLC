---
type: golden-brief
id: brief-01
title: Harbor Ledger, freelance invoicing dashboard
status: draft
---

# Golden brief 01: Harbor Ledger

A fictional product used to test the design factory. Not a real company.

## Input brief (YAML)

```yaml
brief_id: brief-01-harbor-ledger
product:
  name: Harbor Ledger
  type: saas-dashboard
  summary: Freelancer invoicing web app. Freelancers create invoices, track payments, and see what's overdue.
audience:
  primary: Solo freelancers, 28-50, non-designers
  context: Checking cash flow on a laptop between client calls
platforms:
  - web (desktop first, responsive down to 375px)
brand:
  assets: none
  existing_site: none
  personality: calm, trustworthy, a little warm
  avoid: neon accents, gradients as decoration, crypto-style dark mode
accessibility:
  target: WCAG 2.2 AA
  color_modes: light required, dark optional
stack:
  framework: React
  styling: CSS variables (no Tailwind)
  component_library: none, build from scratch
  docs: Storybook
constraints:
  - Overdue status must not rely on color alone
  - Currency and dates must be tabular numerals
  - No more than two typefaces
```

## Required outputs

- `tokens/primitive.json`, `tokens/semantic.json`, `tokens/component.json` in DTCG format, per the token schema
- `dist/tokens.css` compiled from the semantic and component tiers
- Button component (primary, secondary, danger, disabled, loading) built only from component tokens
- Input component (default, focus, error, disabled) built only from component tokens
- Status badge component (paid, pending, overdue, draft) with text labels
- Storybook stories for all of the above

## Expected-output checklist

Each item is pass or fail. A run passes only if every item passes.

### Structure
- [ ] All three token tiers exist and validate against the schema
- [ ] `dist/tokens.css` contains a CSS variable for every semantic token
- [ ] No semantic token references a primitive that is missing from the primitive tier

### Tokens
- [ ] Color roles include at least: surface, surface-raised, text-primary, text-secondary, border, action-primary, action-danger, status-success, status-warning, status-danger
- [ ] Type scale has at least 5 steps with defined line heights
- [ ] Spacing scale is defined on a single base unit
- [ ] Focus ring token exists and is distinct from border

### Accessibility
- [ ] Contrast check passes for every text/background pair in light mode
- [ ] Non-text UI (input borders, focus ring) meets 3:1 against its adjacent background
- [ ] Overdue badge includes the word "Overdue" in its label, not only a red color
- [ ] Focus-visible state is present on button, input, and badge where interactive

### Components
- [ ] Button and input contain no hex, rgb, or px literals for color; they reference component tokens only
- [ ] Button hover state uses a named hover token (e.g. `interactive-primary-hover`), not a filter or opacity shortcut
- [ ] Button has loading state that keeps its width stable
- [ ] Input error state includes a text message, not only a border color change

### Anti-defaults
- [ ] No gradient used as decoration
- [ ] No neon or saturated accent above the chroma limit defined in the brief's brand section (agent must state the limit it used)
- [ ] Typefaces used: 2 or fewer

### Responsiveness
- [ ] Button and input render without overflow at 375px width

## Notes for the evaluator

- Checks marked with a color rule are deterministic. Run the contrast script, do not eyeball it.
- Visual judgment items (calm, warm) are scored by a human reviewer on a 1 to 3 scale and are not gating.

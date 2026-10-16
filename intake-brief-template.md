# Design System Intake Brief (v0 template)

The factory takes this structured brief, not a free-form chat prompt. Missing required fields stop the run and return a list of what's missing.

## Required

```yaml
brief_id: <short-slug, e.g. acme-dashboard-2026-10>
product:
  name: <string>
  type: <saas-dashboard | marketing-site | mobile-app | dev-tool | e-commerce | other>
  summary: <one or two sentences on what the product does>
audience:
  primary: <who uses it day to day>
  secondary: <optional>
platforms: [web | ios | android | desktop]   # at least one
accessibility:
  target: <WCAG 2.2 AA | AAA>            # default AA if blank
  notes: <known needs, e.g. color-blind-safe charts>
stack:
  framework: <react | vue | svelte | web-components | other>
  styling: <tailwind | css-modules | vanilla-css | other>
  component_library: <none | radix | mui | other>
```

## Optional

```yaml
brand:
  logo_url: <string>
  primary_color_hex: <string>            # seed for the palette, not a final value
  fonts: [<string>]
  live_site_url: <string>                # factory may read current colors and fonts from here
  guidelines_url: <string>
constraints:
  must_keep: [<string>]                  # existing tokens or components that cannot change
  must_avoid: [<string>]                 # e.g. gradients, rounded corners, a specific green
tone:
  adjectives: [<string>]                 # e.g. calm, dense, playful
  reference_products: [<string>]         # products to look like, and how
scope:
  components_needed: [<string>]          # default: the 8-12 core set from the playbook
  modes: [light | dark | high-contrast]  # default: light
```

## Validation before the run starts

1. All required fields present, `platforms` non-empty.
2. `primary_color_hex`, if given, is a valid 6-digit hex.
3. If `stack.framework` is `web-components`, `component_library` must be `none`.
4. `brief_id` is unique within the run store.

## Golden brief examples (to write next)

- Early-stage SaaS analytics dashboard, dense, light and dark
- Consumer marketing site, editorial tone, light only
- Developer CLI docs, monospace-heavy, high contrast

Each golden brief gets an expected-output checklist: contrast pass, token coverage, and no anti-default patterns from `frontend-design`.

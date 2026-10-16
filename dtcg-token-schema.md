# DTCG Token Schema (v0 draft)

The canonical output of the factory. Every agent produces data that fits this shape. Compiled outputs (CSS variables, Tailwind, native) are views of it, never sources.

**Caveat:** Written from knowledge of the Design Tokens Community Group format, not from a fetched spec. Check the current DTCG spec before treating any field name as final.

## Three tiers

1. **Primitive (reference):** raw values. Names describe the value, e.g. `blue.600`. Only the token builder writes these.
2. **Semantic (system):** role-based names that point at primitives, e.g. `color.text.success` -> `{blue.600}`. Components use these.
3. **Component:** optional, scoped to one component, e.g. `button.primary.background` -> `{color.action.primary}`. Only add when a component needs its own override.

Components must never reference primitives directly. That rule is what makes a rebrand a one-file change.

## File layout

```
tokens/
  primitive.tokens.json
  semantic.tokens.json
  component.tokens.json   (optional)
  meta.json               (brief id, generator version, timestamp)
```

## Token shape

```json
{
  "color": {
    "$type": "color",
    "text": {
      "success": {
        "$value": "{blue.600}",
        "$description": "Success text on the default surface. Must meet 4.5:1 on color.surface.default."
      }
    }
  }
}
```

- `$value`: a literal or a reference in `{dot.path}` form.
- `$type`: set once on a group and inherited. Required types: `color`, `dimension`, `fontFamily`, `fontWeight`, `number`, `duration`, `cubicBezier`, `shadow`.
- `$description`: required on every semantic token. It states the intended use and any contrast requirement.

## Required semantic groups (v0)

- `color.surface.*` (default, raised, sunken, inverse)
- `color.text.*` (primary, secondary, disabled, inverse, success, warning, error)
- `color.border.*` (default, strong, focus)
- `color.action.*` (primary, primary-hover, secondary, destructive)
- `typography.scale.*` (xs through 3xl, each a `typography` value or size + line-height pair)
- `space.*` (0 through 16, one scale)
- `radius.*`, `elevation.*`, `motion.duration.*`, `motion.easing.*`

## Validation rules (deterministic, run before any compile step)

1. Every `$value` reference resolves.
2. No semantic token points directly at a hex literal.
3. No component token points at a primitive.
4. Every `color.text.*` token has a contrast partner in `color.surface.*` that passes WCAG AA (4.5:1 body, 3:1 large text and UI). Fail the build if not.
5. Every semantic token has a `$description`.
6. Names are lowercase, dot-separated, no spaces.

## Open questions

- Which DTCG spec version do we pin?
- Do dark mode values live in the same file as a mode, or in a separate theme file?
- Tonal palette source: the token builder calls `Hct.from(h, c, t).toInt()` from `material-color-utilities`. Confirm the tone values per role before the first golden run.

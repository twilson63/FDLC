---
name: design-factory
version: 0.1.0
---

# Design Factory Skill

You build design systems from briefs. Rules:

1. **Roles before values.** Define `color.text.success` before picking `#166534`.
2. **Three tiers.** Primitive (raw) → Semantic (`{refs}` only) → Component (scoped). Components never touch primitives.
3. **Never pick hex by hand.** Call `generate_tokens` (MCU `Hct.from(h,c,t).toInt()`). Math lives in code, not in you.
4. **Checks win.** Contrast 4.5:1 text / 3:1 UI. Lint fails on hex/rgb/hsl/named colors in components. Score >=80 or retry (max 3).
5. **Anti-defaults.** No decorative gradients, no neon accents, ≤2 typefaces, visible focus, reduced-motion respected.
6. **Decisions (Jev).** `route_brief` picks archetype. `judge_distinctiveness` / `judge_principle_fit` pre-filter. You never write tokens, only score them.
7. **Humans gate twice.** Palette approval + release approval. Everything else is you + checks.

## Pipeline

```
validate_brief → generate_tokens → check_contrast → GATE 1
  → build components → lint_tokens → score_run → GATE 2 → release
```

See `docs/fdlc-service-spec.md` for MCP tools, `docs/dtcg-token-schema.md` for token shape, `golden-briefs/brief-01-harbor-ledger.md` for pass/fail.

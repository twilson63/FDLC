# FDLC — Factory Design Life Cycle

**Agents generate, checks reject, humans approve.**

FDLC turns a brief into a shippable design system. Agent-executed, human-gated.

```
brief → validate_brief → generate_tokens → check_contrast → HUMAN GATE 1 (palette)
  → build components → lint_tokens → score_run → HUMAN GATE 2 (release)
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

# 1. validate the brief (YAML inside golden brief md)
python checks/validate_brief.py --help

# 2. contrast check (resolved tokens)
python checks/contrast-check.py tokens/semantic.resolved.json golden-briefs/brief-01-harbor-ledger.pairs.json

# 3. lint components for hardcoded colors
python checks/lint-no-hardcoded-colors.py components/

# 4. score the run
python checks/score_run.py --help
```

## Layout

```
FDLC/
  SKILL.md                 # the brain — playbook, schema, rules
  pyproject.toml
  checks/                  # deterministic gates (exit 0 pass / 1 fail / 2 bad input)
    validate_brief.py
    contrast-check.py
    lint-no-hardcoded-colors.py
    score_run.py
  tokens/
    primitive.tokens.json  # raw values only
    semantic.tokens.json   # roles → {primitive refs}, never hex
    semantic.resolved.json # resolved hex for checks (generated)
  golden-briefs/
    brief-01-harbor-ledger.md
    brief-01-harbor-ledger.pairs.json
  components/
    button.css             # tokens only, no hex
  docs/
    dtcg-token-schema.md
    intake-brief-template.md
    fdlc-service-spec.md
```

## Rules

1. Components never reference primitives. Semantic only.
2. Semantic never holds hex. `{refs}` only.
3. Deterministic checks always beat model judgment.
4. Two human gates: palette + release. Everything else is agents + checks.

## Status

v0.1 starter — Harbor Ledger golden brief passes contrast + lint. Primitive/semantic split done. Next: `generate_tokens.py` (brief → tokens via MCU), `build_css.py`, brief-02.

# FDLC Service Spec — Design System Life Cycle Factory

Status: draft v0.2 — 2026-10-15
Related: `design-system-playbook.md` (procedures), `dtcg-token-schema.md`, `intake-brief-template.md`, `brief-01-harbor-ledger.md`, `contrast-check.py`, `lint-no-hardcoded-colors.py`, `brief_to_tokens.py` (unsaved), `button.css`

## 1. What it is

FDLC = Factory Design Life Cycle. Agent-executed, human-gated pipeline that turns a brief into a shippable design system.

Rule: **agents generate, checks reject, humans approve.**

Two human gates only:
1. Approve token palette (after `check_contrast` passes)
2. Approve PR / release (after `lint` + `score_run` pass)

## 2. Three parts — skill, MCP, agent

### 2.1 Skill: `design-factory`
The brain. No code, just judgment. Any agent loads it.

Contains:
- 9-phase playbook (audit → validation)
- DTCG schema (primitive / semantic / component)
- Brief template + validation rules
- Role→tone map rules (from `brief_to_tokens.py` ROLE_MAP)
- Anti-default checklist (from `frontend-design`)
- Golden briefs as few-shot examples

### 2.2 MCP server: `fdlc-tools`
The hands. Deterministic work LLMs suck at. Wraps the .py scripts so any runner (Claude, Codex, Hyperclaw) calls the same tools.

| Tool | Input | Output | Exit / fail |
|---|---|---|---|
| `validate_brief` | brief YAML | pass/fail + missing fields | fail = stop, ask human |
| `generate_tokens` | seed hex + brief constraints | `semantic.json` (DTCG) | fail on bad hex (exit 2) |
| `check_contrast` | semantic.json + pairs.json | ratios per pair, pass/fail | fail <4.5 text, <3.0 non-text |
| `lint_tokens` | css / component dir | violations list | fail on hex, rgb/hsl/oklch, named colors in color props |
| `build_css` | semantic.json | css variables + tailwind config | fail on unresolved alias |
| `score_run` | outputs + golden checklist | 0-100 + per-item pass/fail | <80 = retry, 3x max then escalate |

All tools: stdin JSON → stdout JSON, exit 0 pass / 1 fail / 2 bad input.

### 2.3 Agent: `fdlc-runner`
The foreman. Runs the loop, not the math.

```
brief → validate_brief
  → generate_tokens → check_contrast → HUMAN GATE 1 (palette)
  → build components → lint_tokens → score_run
  → fail? retry (max 3, tweak tones/roles) → pass? HUMAN GATE 2 (release)
  → publish versioned system
```

Roles = prompts inside runner, not separate agents:
- strategist (brief → direction + token plan)
- token-builder (calls `generate_tokens`, never picks hex by hand)
- component-author (tokens only, anatomy + states first)
- critic (runs checks, flags defaults/drift)
- documenter (decisions + when-not-to rules)

## 3. Repo layout V1

```
design-factory/
  SKILL.md
  mcp-server/
    validate_brief.py
    generate_tokens.py      # = brief_to_tokens.py
    check_contrast.py
    lint_tokens.py          # = lint-no-hardcoded-colors.py
    build_css.py
    score_run.py
  runner/
    prompts/ (5 roles)
    loop.py (retry + gates)
  artifacts/
    semantic.json, pairs.json, button.css
  golden-briefs/
    brief-01-harbor-ledger.md (+ 2 more)
```

## 4. Build order

1. Skill + scripts (now — 70% / 50% done)
2. MCP wrap (when 2nd agent needs it)
3. Runner last (needs `validate_brief` + `score_run` first — without those loop can't fail cleanly)

## 5. Open gaps

- `brief_to_tokens.py` unsaved, ROLE_MAP + chroma floors are author picks, not MCU defaults
- seed not in brief template yet — add `brand.seed_hex`
- no `validate_brief.py` or `score_run.py`
- `button.css` hover token added (rev 720) but no transition, reduced-motion rule is dead code
- contrast + lint only tested on sandbox copies, not saved files — run locally to confirm
- thresholds 4.5/3.0 from WCAG 2 knowledge, not fetched WCAG 2.2 text
- round-one brain pages unverified (no fetch calls in conversation)

## 6. Decisions layer — Jev (TypeSafe)

Decision model, not LLM. Input + fixed options → probabilities. No text essay. For software to consume.

Why here: half the FDLC loop is decisions, not generation. Using a $500/mo reasoning model for yes/no is dumb.

### 6.1 Where it lives
Wrapped behind MCP `fdlc-tools` so vendor is swappable. Skill defines options + thresholds. Runner calls it to fail fast before human looks.

Never writes tokens. Only scores them. Deterministic checks always win over Jev.

Checkpoint note: Jev breaks like an LLM — prompt injection works against typed decisions. Treat output as untrusted.

### 6.2 Tools

| Tool | Input | Options | Use |
|---|---|---|---|
| `route_brief` | brief YAML | [saas-dashboard, consumer-warm, fintech-dense, marketing-bold] | picks ROLE_MAP + golden brief to test against, ~200ms |
| `judge_distinctiveness` | tokens + screenshot | [distinctive / generic] | <0.7 distinctive = retry |
| `judge_principle_fit` | tokens + principles | [on-principle / off-principle] | off-principle = retry |

### 6.3 Rules
```yaml
decisions:
  - route_brief: [archetype probabilities]
  - judge_distinctiveness: [distinctive vs generic, threshold 0.7 reject]
  - judge_principle_fit: [on-principle vs off-principle]
rules:
  - deterministic checks override Jev always
  - Jev never outputs hex, tokens, or CSS
  - below threshold = retry max 3, then escalate to human
  - human gates unchanged: palette + release still need approval
```

### 6.4 Loop with decisions
```
brief → validate_brief → route_brief (Jev)
  → generate_tokens → check_contrast → judge_principle_fit (Jev) → GATE 1
  → build → lint → judge_distinctiveness (Jev) → score_run → GATE 2
```

"""Deterministic contrast check for the design factory.

Reads a DTCG semantic token file, resolves each declared text/background
pair, and fails any pair below its WCAG 2.2 threshold.

Thresholds (from WCAG 2 contrast definitions, verify against the current spec):
  normal text: 4.5:1
  large text (>= 24px, or >= 18.66px bold): 3:1
  non-text UI (borders, focus rings, icons that carry meaning): 3:1

Usage:
  python contrast-check.py tokens/semantic.json pairs.json

pairs.json is a list of objects:
  {"fg": "text-primary", "bg": "surface", "kind": "text" | "large-text" | "non-text"}

Exit code 0 if all pass, 1 if any fail, 2 on input error.
"""
import json
import sys

THRESHOLDS = {"text": 4.5, "large-text": 3.0, "non-text": 3.0}


def flatten(node, prefix="", out=None):
    """Collect DTCG tokens into {name: hex} keyed by the last path segment."""
    if out is None:
        out = {}
    if isinstance(node, dict):
        if "$value" in node and node.get("$type") == "color":
            out[prefix.strip(".")] = node["$value"]
            return out
        for key, child in node.items():
            if key.startswith("$"):
                continue
            flatten(child, f"{prefix}.{key}", out)
    return out


def parse_hex(value):
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"Only 6-digit hex is supported in this check: {value}")
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))


def linear(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(hex_a, hex_b):
    la, lb = luminance(parse_hex(hex_a)), luminance(parse_hex(hex_b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        with open(argv[1]) as f:
            tokens = flatten(json.load(f))
        with open(argv[2]) as f:
            pairs = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"input error: {e}")
        return 2

    failed = False
    for pair in pairs:
        fg_name, bg_name, kind = pair["fg"], pair["bg"], pair.get("kind", "text")
        fg = next((v for k, v in tokens.items() if k.endswith("." + fg_name) or k == fg_name), None)
        bg = next((v for k, v in tokens.items() if k.endswith("." + bg_name) or k == bg_name), None)
        if fg is None or bg is None:
            print(f"FAIL missing token: {fg_name} or {bg_name}")
            failed = True
            continue
        try:
            r = ratio(fg, bg)
        except ValueError as e:
            print(f"FAIL {fg_name} on {bg_name}: {e}")
            failed = True
            continue
        need = THRESHOLDS.get(kind, THRESHOLDS["text"])
        status = "PASS" if r >= need else "FAIL"
        failed |= status == "FAIL"
        print(f"{status} {fg_name} on {bg_name} ({kind}): {r:.2f}:1, need {need}:1")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

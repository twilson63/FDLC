"""Resolve semantic {refs} against the primitive tier.

Writes a copy of the semantic file with every {dot.path} reference replaced
by the primitive's literal value, for checks that need hex (contrast-check,
score_run --resolved). Also enforces DTCG schema rule 1: every $value
reference resolves.

Usage:
  python resolve_tokens.py tokens/primitive.tokens.json tokens/semantic.tokens.json [out.json]

Writes to out.json if given, else stdout.
Exit code 0 if all refs resolve, 1 if any do not, 2 on input error.
"""
import json
import re
import sys

REF = re.compile(r"^\{([^{}]+)\}$")


def lookup(primitives, path):
    node = primitives
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node.get("$value") if isinstance(node, dict) else None


def resolve(node, primitives, errors, prefix=""):
    if not isinstance(node, dict):
        return node
    out = {}
    for key, child in node.items():
        if key == "$value" and isinstance(child, str) and REF.match(child):
            value, seen = child, set()
            while isinstance(value, str) and REF.match(value):
                path = REF.match(value).group(1)
                if path in seen:
                    errors.append(f"{prefix.strip('.')}: circular ref {child}")
                    break
                seen.add(path)
                value = lookup(primitives, path)
                if value is None:
                    errors.append(f"{prefix.strip('.')}: unresolved ref {child}")
                    break
            out[key] = value if value is not None else child
        elif key.startswith("$"):
            out[key] = child
        else:
            out[key] = resolve(child, primitives, errors, f"{prefix}.{key}")
    return out


def main(argv):
    if len(argv) not in (3, 4):
        print(__doc__)
        return 2
    try:
        with open(argv[1]) as f:
            primitives = json.load(f)
        with open(argv[2]) as f:
            semantic = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"input error: {e}", file=sys.stderr)
        return 2

    errors = []
    resolved = json.dumps(resolve(semantic, primitives, errors), indent=2) + "\n"
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)
    if errors:
        return 1
    if len(argv) == 4:
        with open(argv[3], "w") as f:
            f.write(resolved)
    else:
        sys.stdout.write(resolved)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

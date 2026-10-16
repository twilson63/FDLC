"""validate_brief.py - FDLC gate 1. Validates intake brief YAML before any work starts.
Usage: python validate_brief.py --brief brief.yaml [--known-ids a,b,c]
Exit 0 = valid, 1 = invalid, 2 = bad input/file. Rules from intake-brief-template.md rev 711.
"""
import argparse, re, sys
try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required: pip install pyyaml", file=sys.stderr); sys.exit(2)
HEX6 = re.compile(r'^#[0-9a-fA-F]{6}$')
VALID_TYPES = {"saas-dashboard","marketing-site","mobile-app","dev-tool","e-commerce","other"}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--known-ids", default="")
    a = ap.parse_args()
    try:
        with open(a.brief) as f: b = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"ERROR: brief file not found: {a.brief}", file=sys.stderr); sys.exit(2)
    except Exception as e:
        print(f"ERROR: bad YAML: {e}", file=sys.stderr); sys.exit(2)
    errs = []
    bid = b.get("brief_id")
    if not bid or not isinstance(bid, str): errs.append("missing: brief_id (short-slug)")
    elif a.known_ids and bid in [x.strip() for x in a.known_ids.split(",") if x.strip()]:
        errs.append(f"duplicate: brief_id '{bid}' already in run store")
    prod = b.get("product") or {}
    if not prod.get("name"): errs.append("missing: product.name")
    pt = prod.get("type")
    if not pt: errs.append("missing: product.type")
    elif pt not in VALID_TYPES: errs.append(f"invalid: product.type '{pt}' must be one of {sorted(VALID_TYPES)}")
    if not prod.get("summary"): errs.append("missing: product.summary")
    aud = b.get("audience") or {}
    if not aud.get("primary"): errs.append("missing: audience.primary")
    plats = b.get("platforms")
    if not plats or not isinstance(plats, list) or not len(plats): errs.append("missing: platforms (at least one)")
    acc = b.get("accessibility") or {}
    tgt = acc.get("target", "WCAG 2.2 AA")
    if tgt not in ("WCAG 2.2 AA", "AAA", "WCAG 2.2 AAA"): errs.append(f"invalid: accessibility.target '{tgt}'")
    stack = b.get("stack") or {}
    fw = stack.get("framework")
    if not fw: errs.append("missing: stack.framework")
    if not stack.get("styling"): errs.append("missing: stack.styling")
    if not stack.get("component_library"): errs.append("missing: stack.component_library")
    if fw == "web-components" and stack.get("component_library") != "none":
        errs.append("invalid: web-components requires component_library: none")
    brand = b.get("brand") or {}
    hx = brand.get("primary_color_hex")
    if hx and not HEX6.match(str(hx)): errs.append(f"invalid: brand.primary_color_hex '{hx}' must be #RRGGBB")
    if errs:
        print("BRIEF INVALID:")
        for e in errs: print(f" - {e}")
        sys.exit(1)
    print(f"BRIEF VALID: {bid}")
    sys.exit(0)
if __name__ == "__main__": main()

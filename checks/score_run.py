"""score_run.py - FDLC gate 2. Scores a run against golden-brief-01 deterministic checklist.
Usage: python score_run.py --tokens semantic.json --css dist/tokens.css --components components/ [--pairs pairs.json]
Exit 0 = all pass, 1 = any fail, 2 = bad input.
"""
import argparse, json, re, sys, os, glob
HEX_RE = re.compile(r'#[0-9a-fA-F]{3,8}\\b')
RGB_RE = re.compile(r'\\b(rgb|hsl|oklch|oklab)\\s*\\(', re.I)
NAMED = {"red","blue","green","black","white","gray","grey","navy","teal","orange","purple","pink","yellow","brown","beige","ivory","maroon","olive","lime","aqua","silver"}
COLOR_PROP = re.compile(r'(?<![a-zA-Z-])(color|background(?:-color)?|border(?:-top|-right|-bottom|-left)?(?:-color)?|outline-color|fill|stroke|box-shadow|text-decoration-color)\\s*:', re.I)
def load_json(p):
    with open(p) as f: return json.load(f)
def flatten_tokens(node, prefix=""):
    out = {}
    if isinstance(node, dict) and "$value" in node:
        out[prefix.rstrip(".")] = node
        return out
    if isinstance(node, dict):
        for k,v in node.items():
            if k.startswith("$"): continue
            out.update(flatten_tokens(v, prefix+k+"."))
    return out
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--css")
    ap.add_argument("--components")
    ap.add_argument("--pairs")
    a = ap.parse_args()
    try: sem = load_json(a.tokens)
    except Exception as e: print(f"ERROR: bad tokens: {e}", file=sys.stderr); sys.exit(2)
    flat = flatten_tokens(sem)
    checks = []
    def chk(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
    req = ["surface","surface-raised","text-primary","text-secondary","border-strong","interactive-primary","interactive-primary-hover","text-on-primary","focus-ring"]
    keys = " ".join(flat.keys()).lower()
    for r in req:
        chk(f"token:{r}", r.lower() in keys, "present" if r.lower() in keys else "missing")
    nodes = list(flat.values())
    missing_desc = [k for k,v in flat.items() if not v.get("$description")]
    chk("tokens:descriptions", not missing_desc, f"{len(missing_desc)} missing" if missing_desc else f"{len(nodes)} described")
    hex_hits = [k for k,v in flat.items() if isinstance(v.get("$value"), str) and HEX_RE.search(v["$value"])]
    chk("tokens:no-hex-literals", not hex_hits, "; ".join(hex_hits[:5]) if hex_hits else "all refs")
    if a.css:
        try:
            css = open(a.css).read()
            uncovered = [k for k in flat if "--"+k.replace(".","-").lower() not in css.lower() and "--"+k.split(".")[-1].lower() not in css.lower()]
            chk("css:covers-tokens", not uncovered, f"{len(uncovered)} uncovered" if uncovered else "all covered")
        except Exception as e: chk("css:covers-tokens", False, str(e))
    if a.components:
        files = []
        if os.path.isfile(a.components): files=[a.components]
        else: files=glob.glob(os.path.join(a.components,"**","*.css"), recursive=True)
        viols=[]
        allcss=""
        for fp in files:
            txt=open(fp).read(); allcss+=txt+"\\n"
            for i,line in enumerate(txt.splitlines(),1):
                if COLOR_PROP.search(line) and (HEX_RE.search(line) or RGB_RE.search(line)):
                    viols.append(f"{os.path.basename(fp)}:{i}")
                if COLOR_PROP.search(line):
                    for w in re.findall(r':\\s*([a-z]+)', line.lower()):
                        if w in NAMED: viols.append(f"{os.path.basename(fp)}:{i}:{w}")
        chk("components:no-hardcoded-colors", not viols, "; ".join(viols[:5]) if viols else f"{len(files)} files clean")
        chk("components:hover-token", "interactive-primary-hover" in allcss, "found" if "interactive-primary-hover" in allcss else "missing")
    if a.pairs:
        try:
            pairs = load_json(a.pairs)
            plist = pairs.get("pairs", pairs if isinstance(pairs, list) else [])
            def lum(h):
                h=h.lstrip("#"); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
                f=lambda c: c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
                r,g,b=f(r),f(g),f(b)
                return 0.2126*r+0.7152*g+0.0722*b
            def ratio(x,y):
                l1,l2=lum(x),lum(y); hi,lo=max(l1,l2),min(l1,l2); return (hi+0.05)/(lo+0.05)
            hexmap={}
            for k,v in flat.items():
                val=v.get("$value","")
                if isinstance(val,str) and HEX_RE.fullmatch(val.strip()): hexmap[k]=val.strip(); hexmap[k.split(".")[-1]]=val.strip()
            fails=[]
            for p in plist:
                t=p.get("text",{}); bg=p.get("background",{})
                th=p.get("threshold",4.5)
                thx=hexmap.get(t.get("token","")); bgx=hexmap.get(bg.get("token",""))
                if not thx or not bgx: fails.append(f"{t.get('token')}/{bg.get('token')}:unresolved"); continue
                if ratio(thx,bgx) < th: fails.append(f"{t.get('token')}/{bg.get('token')}:{ratio(thx,bgx):.2f}<{th}")
            chk("contrast:pairs", not fails, "; ".join(fails[:5]) if fails else f"{len(plist)} pairs pass")
        except Exception as e: chk("contrast:pairs", False, str(e))
    fails=[c for c in checks if not c["pass"]]
    print(json.dumps({"pass": len(fails)==0, "failed": len(fails), "total": len(checks), "checks": checks}, indent=2))
    sys.exit(0 if not fails else 1)
if __name__=="__main__": main()

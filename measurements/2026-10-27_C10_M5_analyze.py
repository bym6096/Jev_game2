import json, os
D=os.path.dirname(os.path.abspath(__file__))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M5.jsonl")]
by={r["id"]:r["answers"] for r in rows}
print("alpha08: item desc | tariff probs | false")
for r in rows:
    if r["id"].startswith("a08") and r["id"].endswith("tariff"):
        base=r["id"][:-7]; p=r["answers"]["tariff"]["probabilities"]
        print(f"{base:18s}"," ".join(f"{k[:5]}={v:.2f}" for k,v in p.items()), f"| false={by[base+'-false']['false']['noul']:.2f}")
for pre in ("a03","b05","b01","a06"):
    print("\n"+pre)
    for r in rows:
        if r["id"].startswith(pre):
            v=[a["noul"] for a in r["answers"].values()]
            print(f"{r['id']:30s}"," ".join(f"{x:.2f}" for x in v))
print("\nbeta04")
for r in rows:
    if r["id"].startswith("b04"):
        print(r["id"]," ".join(f"{k}={a['noul']:.2f}" for k,a in r["answers"].items()))
print("\nbeta06")
for r in rows:
    if r["id"].startswith("b06"):
        print(r["id"])
        for k,a in r["answers"].items():
            print("  ",k,a["choice"]," ".join(f"{n[:8]}={v:.2f}" for n,v in a["probabilities"].items()))

import json, os
D=os.path.dirname(os.path.abspath(__file__))
def load(f): return [json.loads(l) for l in open(f"{D}/{f}")]
print("beta01 (items 1..5; item4 = me)")
for r in load("2026-10-27_C10_M3.jsonl"):
    v=[r["answers"][f"e{k}"]["noul"] for k in range(1,6)]
    print(f"{r['id']:40s}"," ".join(f"{x:.2f}" for x in v),f"rng={max(v)-min(v):.2f}")
print("\nbeta03 / alpha06")
for r in load("2026-10-27_C10_M4.jsonl"):
    v=[a["noul"] for a in r["answers"].values()]
    print(f"{r['id']:28s}"," ".join(f"{x:.2f}" for x in v))

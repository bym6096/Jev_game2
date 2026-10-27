import json, sys, os
D=os.path.dirname(os.path.abspath(__file__))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M1a.jsonl")]
def vals(r): return [r["answers"][f"c{i}"]["noul"] for i in range(1,13)]
by={r["id"]:vals(r) for r in rows}
print("alpha01: id | values | gray<=30%? yes-share | range")
for k,v in by.items():
    gray=sum(0.35<=x<=0.65 for x in v); yes=sum(x>0.5 for x in v)
    print(f"{k:12s} {' '.join(f'{x:.2f}' for x in v)} | gray {gray}/12 yes {yes}/12 | rng {max(v)-min(v):.2f}")
for s in "ABC":
    a,b=by[f"a01-{s}-S1"],by[f"a01-{s}-P1"]
    print(s,"S1-P1 mean|d|",round(sum(abs(x-y) for x,y in zip(a,b))/12,3),
          "S1 rep",round(sum(abs(x-y) for x,y in zip(a,by[f"a01-{s}-S1-r"]))/12,3),
          "KO dir agree",sum((x>0.5)==(y>0.5) for x,y in zip(a,by[f"a01-{s}-KO"])),"/12",
          "KO mean|d|",round(sum(abs(x-y) for x,y in zip(a,by[f"a01-{s}-KO"]))/12,3))
    x=by[f"a01-{s}-X1"]; print("  X1 low-high", round(sum(x[:6])/6-sum(x[6:])/6,3))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M1b.jsonl")]
print("\nbeta02")
qs=list(rows[0]["answers"])
print("room      "+" ".join(f"{q:>6s}" for q in qs))
for r in rows:
    print(f"{r['id']:9s} "+" ".join(f"{r['answers'][q]['noul']:6.2f}" for q in qs))

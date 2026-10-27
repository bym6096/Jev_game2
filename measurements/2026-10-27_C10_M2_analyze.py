import json, os
D=os.path.dirname(os.path.abspath(__file__))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M2.jsonl")]
by={r["id"]:r["answers"] for r in rows}
print("alpha04 meters s1 s2 u1 u2")
for r in rows:
    if r["id"].startswith("a04"):
        a=r["answers"]; print(f"{r['id']:14s}", " ".join(f"{a[q]['noul']:.2f}" for q in ("s1","s2","u1","u2")))
print("\nbeta07")
def tvd(p,q): return sum(abs(p[k]-q[k]) for k in p)/2
for r in rows:
    if r["id"].startswith("b07"):
        a=r["answers"]["office"]; p=a["probabilities"]
        base=by[r["id"].split("-")[0]+"-"+r["id"].split("-")[1]+"-orig"]["office"]["probabilities"]
        print(f"{r['id']:30s} top={a['choice']:15s}", " ".join(f"{k[:6]}={v:.2f}" for k,v in p.items()), f"TVD={tvd(p,base):.2f}")

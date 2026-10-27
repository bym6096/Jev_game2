import json, os
D=os.path.dirname(os.path.abspath(__file__))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M10.jsonl")]
prev={json.loads(l)["id"]:json.loads(l)["answers"] for l in open(f"{D}/2026-10-27_C10_M2.jsonl")}
by={r["id"]:r["answers"] for r in rows}; by.update({k:v for k,v in prev.items() if k not in by})
def tvd(p,q): return sum(abs(p[k]-q[k]) for k in p)/2
for r in rows:
    a=r["answers"]
    if r["id"].startswith("b07"):
        L=r["id"].split("-")[1]; base=by[f"b07-{L}-orig"]["office"]["probabilities"]; p=a["office"]["probabilities"]
        print(f"{r['id']:26s} top={a['office']['choice']:15s}"," ".join(f"{k[:5]}={v:.2f}" for k,v in p.items()),f"TVD={tvd(p,base):.2f}")
    elif r["id"].startswith("b01"):
        print(f"{r['id']:26s}"," ".join(f"{v['noul']:.2f}" for v in a.values()))
allr=by["b04-int-all"]; d=[]
for j in range(4):
    for k,v in by[f"b04-int-only{j}"].items():
        d.append(abs(v["noul"]-allr[k]["noul"])); print(k, f"alone={v['noul']:.2f} together={allr[k]['noul']:.2f}")
print("b04 interference mean|d|",round(sum(d)/len(d),3),"max",round(max(d),2))

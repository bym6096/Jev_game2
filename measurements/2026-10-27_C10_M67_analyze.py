import json, os
D=os.path.dirname(os.path.abspath(__file__))
rows=[json.loads(l) for l in open(f"{D}/2026-10-27_C10_M67.jsonl")]
for r in rows:
    a=r["answers"]; out=[]
    for k,v in a.items():
        if v["type"]=="noul": out.append(f"{k}={v['noul']:.2f}")
        elif v["type"]=="choice": out.append(f"{k}:{v['choice']} "+" ".join(f"{n[:5]}={p:.2f}" for n,p in v["probabilities"].items()))
        else: out.append(f"{k}:{v}")
    print(f"{r['id']:28s}"," ".join(out))

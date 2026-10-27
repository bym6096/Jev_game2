import json, math, statistics as stt
rows = [json.loads(l) for l in open("2026-10-27_C9-M1x_fire.jsonl")]
lg = lambda p: math.log(min(.99, max(.01, p)) / (1 - min(.99, max(.01, p))))
sg = lambda x: 1 / (1 + math.exp(-x))
V = {}
for r in rows:
    key = r["id"] + ("#rep" if r["cond"] == "AB_rep" else "")
    V[key] = r["answers"]["target"]["noul"]
res = []
for cid in ["I1", "I2", "I3", "I4", "I5", "C1", "C2", "C3"]:
    p0, pa, pb, pab = (V[f"F-{cid}-{c}"] for c in ["base", "A", "B", "AB"])
    pab2, psw = V[f"F-{cid}-AB#rep"], V[f"F-{cid}-AB_swap"]
    pred = sg(lg(pa) + lg(pb) - lg(p0))
    nor = 1 - (1 - pa) * (1 - pb)
    pabm = (pab + pab2) / 2
    res.append((cid, pabm - pred, abs(pab - pab2), abs(psw - pabm)))
    print(f"{cid}: base {p0:.2f} A {pa:.2f} B {pb:.2f} AB {pab:.2f}/{pab2:.2f} swap {psw:.2f} | logit-add pred {pred:.2f} resid {pabm-pred:+.2f} | noisyOR {nor:.2f} diff {pabm-nor:+.2f}")
I = [r for r in res if r[0].startswith("I")]; C = [r for r in res if r[0].startswith("C")]
print("interaction |resid|>=0.15:", sum(abs(r[1]) >= .15 for r in I), "/5; control:", sum(abs(r[1]) >= .15 for r in C), "/3")
print("AB rep mean|d|", round(stt.mean(r[2] for r in res), 3), "swap mean|d|", round(stt.mean(r[3] for r in res), 3), "max swap", round(max(r[3] for r in res), 3))

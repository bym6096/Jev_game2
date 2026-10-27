import json, statistics as stt
LV = {"crash": -2, "fall": -1, "flat": 0, "rise": 1, "surge": 2}
R = {}
for l in open("2026-10-27_C9-M1x_market.jsonl"):
    r = json.loads(l); R[r["id"]] = {k: sum(LV[c] * p for c, p in a["probabilities"].items()) for k, a in r["answers"].items()}
G = list(R["M-base"])
avg = lambda c: {g: (R[f"M-{c}"][g] + R[f"M-{c}#rep"][g]) / 2 for g in G} if f"M-{c}#rep" in R else R[f"M-{c}"]
b = avg("base")
print("goods   " + " ".join(f"{g[:7]:>7}" for g in G))
for c in ["base", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "P1", "P2", "P3", "P4"]:
    print(f"{c:7} " + " ".join(f"{avg(c)[g]:+7.2f}" for g in G))
noise = [abs(R[f"M-{c}"][g] - R[f"M-{c}#rep"][g]) for c in ["base", "H1", "H2", "P1"] for g in G]
print("rep noise mean", round(stt.mean(noise), 3), "max", round(max(noise), 3))
EXP = {"H1": {"fans", "coolers", "sunscreen"}, "H2": {"candles"}, "H3": {"umbrellas", "peaches", "candles"}, "H4": {"vinyl"}, "H5": {"locks"}, "H6": {"peaches"}}
ok = rng = 0
for h, e in EXP.items():
    d = {g: avg(h)[g] - b[g] for g in G}; top = max(d, key=lambda g: abs(d[g])); r_ = max(d.values()) - min(d.values())
    ok += top in e; rng += r_ >= .8; print(f" {h}: top mover {top} {d[top]:+.2f} expected {sorted(e)} range {r_:.2f}")
print(f"differentiation {ok}/6, range>=0.8 {rng}/6")
d0 = {g: avg("H0")[g] - b[g] for g in G}; print("H0 max|d|", round(max(map(abs, d0.values())), 2), max(d0, key=lambda g: abs(d0[g])))
clip = lambda x: max(-2, min(2, x))
for p, (x, y) in {"P1": ("H1", "H2"), "P2": ("H3", "H4"), "P3": ("H1", "H3"), "P4": ("H2", "H5")}.items():
    res = {g: avg(p)[g] - clip(b[g] + (avg(x)[g] - b[g]) + (avg(y)[g] - b[g])) for g in G}
    resm = {g: avg(p)[g] - (avg(x)[g] + avg(y)[g]) / 2 for g in G}
    big = [f"{g} {v:+.2f}" for g, v in res.items() if abs(v) > .5]
    bigm = sum(abs(v) > .5 for v in resm.values())
    print(f" {p}: additive-resid>0.5: {big} | (A's mean-null would flag {bigm} goods)")

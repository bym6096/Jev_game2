import json, statistics as stt
LV = {"vanishes": -2, "shrinks": -1, "holds": 0, "grows": 1, "takes_over": 2}
R = {}
for l in open("2026-10-27_C9-M1x_tank.jsonl"):
    r = json.loads(l)
    R[r["id"]] = {k: (sum(LV[c] * p for c, p in a["probabilities"].items()) if a["type"] == "choice" else a["noul"]) for k, a in r["answers"].items()}
noise = []; hits = 0
for t in ["T1", "T2", "T3"]:
    keys = list(R[f"T-{t}-base"]); avg = lambda c: {k: (R[f"T-{t}-{c}"][k] + R[f"T-{t}-{c}#rep"][k]) / 2 for k in keys} if f"T-{t}-{c}#rep" in R else R[f"T-{t}-{c}"]
    b, x, y, xy = avg("base"), avg("X"), avg("Y"), avg("XY")
    for c in ["base", "XY"]: noise += [abs(R[f"T-{t}-{c}"][k] - R[f"T-{t}-{c}#rep"][k]) for k in keys if k != "clear"]
    big = []
    print(t)
    for k in keys:
        res = xy[k] - (x[k] + y[k] - b[k])
        print(f"  {k:14} base {b[k]:+.2f} X {x[k]:+.2f} Y {y[k]:+.2f} XY {xy[k]:+.2f} resid {res:+.2f}")
        if k != "clear" and abs(res) > .5: big.append(k)
    hits += bool(big); print("  resid>0.5:", big)
print(f"tanks with 3-way effect {hits}/3; rep noise |dEV| mean {stt.mean(noise):.3f} max {max(noise):.2f}")
b = {k: (R["T-T1-base"][k] + R["T-T1-base#rep"][k]) / 2 for k in R["T-T1-base"]}
for j in ["salt", "oak", "radio", "castle", "diver", "magnet"]:
    d = {k: R[f"T-T1-junk-{j}"][k] - b[k] for k in b}
    mx = max((abs(v), k) for k, v in d.items() if k != "clear")
    print(f" junk {j:7} max|dEV| {mx[0]:.2f} ({mx[1]}) clear d {d['clear']:+.2f} | " + " ".join(f"{k[:6]} {v:+.2f}" for k, v in d.items()))

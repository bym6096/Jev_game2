import json, statistics as stt
R = {}
for l in open("2026-10-27_C9-M1x_a03.jsonl"):
    r = json.loads(l); R[r["id"]] = {j: a["probabilities"]["grant_claim"] + .5 * a["probabilities"]["partial"] for j, a in r["answers"].items()}
J = ["yoon", "kang", "park"]; C = ["final", "kia", "eunbi"]
m = lambda c, k: {j: (R[f"J-{c}-{k}"][j] + R[f"J-{c}-{k}#rep"][j]) / 2 for j in J}
noise = [abs(R[f"J-{c}-{k}"][j] - R[f"J-{c}-{k}#rep"][j]) for c in C for k in ["base", "direct", "indirect", "irrelevant"] for j in J]
print(f"rep noise |ds| mean {stt.mean(noise):.3f} max {max(noise):.2f}")
for c in C:
    print(c, "base", {j: round(v, 2) for j, v in m(c, "base").items()})
for k in ["direct", "indirect", "irrelevant", "indirect_facts"]:
    d = []
    for c in C:
        b = m(c, "base"); x = m(c, k) if k != "indirect_facts" else R[f"J-{c}-{k}"]
        d += [x[j] - b[j] for j in J]
    print(f"{k:15} mean ds {stt.mean(d):+.3f} mean|ds| {stt.mean(map(abs, d)):.3f} positive {sum(v > 0 for v in d)}/9 cells: " + " ".join(f"{v:+.2f}" for v in d))

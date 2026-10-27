"""Analysis for C9-M01 (latency) and C9-M02 (top-1 flip under accumulated history).
Reads the JSONL outputs next to this file; prints tables and writes 2026-10-27_C9-M0x.summary.json."""
import json, os
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda n: [json.loads(l) for l in open(os.path.join(HERE, n))]
out = {}

# ---- M01
m01 = [r for r in load("2026-10-27_C9-M01.jsonl") if r["cond"] != "warmup"]
def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]
out["M01"] = {}
print("== C9-M01 latency (warm-up excluded)")
for cell in ("short_q1", "short_q5", "long_q1", "long_q5"):
    xs = [r["latency_ms"] for r in m01 if r["cond"] == cell]
    tok = median(r["usage"]["input_tokens"] for r in m01 if r["cond"] == cell)
    d = dict(n=len(xs), p50=median(xs), p95=pct(xs, 0.95), max=max(xs), min=min(xs), input_tokens=tok)
    out["M01"][cell] = d; print(cell, d)
allx = [r["latency_ms"] for r in m01]
out["M01"]["all"] = dict(n=len(allx), p50=median(allx), p95=pct(allx, 0.95), max=max(allx))
print("all", out["M01"]["all"])

# ---- M02
P = lambda r: r["answers"]["q"]["probabilities"]
top = lambda p: max(p, key=p.get)
tvd = lambda a, b: 0.5 * sum(abs(a[k] - b.get(k, 0)) for k in a)
items = {(i["id"], i["cond"]): i for i in json.load(open(os.path.join(HERE, "2026-10-27_C9-M02.items.json")))}
m = {(r["id"], r["cond"]): P(r) for r in load("2026-10-27_C9-M02.jsonl")}
rp = {(r["id"], r["cond"]): P(r) for r in load("2026-10-27_C9-M02.repeat.jsonl")}
ids = list(dict.fromkeys(k[0] for k in items))
conds = ["rel1", "rel3", "rel5", "irr5"]

print("\n== C9-M02 per situation: base top (p) | cond top (p, target p) ; * = flip")
rows = []
for sid in ids:
    tgt = items[(sid, "base")]["target"]; b = m[(sid, "base")]; bt = top(b)
    row = dict(id=sid, cand=items[(sid, "base")]["cand"], target=tgt, base_top=bt,
               base_p=b[bt], base_target_p=b[tgt], base_is_target=(bt == tgt))
    line = f"{sid:13s} base {bt}({b[bt]:.2f}) tgt {b[tgt]:.2f} |"
    for c in conds:
        p = m[(sid, c)]; t = top(p)
        row[c] = dict(top=t, p=p[t], target_p=p[tgt], flip=t != bt, to_target=t == tgt and bt != tgt, tvd=tvd(b, p))
        line += f" {c}:{t}({p[t]:.2f},t{p[tgt]:.2f},d{tvd(b,p):.2f}){'*' if t != bt else ''}"
    # noise floor
    row["noise"] = {c: dict(tvd=tvd(m[(sid, c)], rp[(sid, c)]), top_changed=top(m[(sid, c)]) != top(rp[(sid, c)]))
                    for c in ("base", "rel5", "irr5")}
    rows.append(row); print(line)

n = len(rows)
summ = {}
for c in conds:
    summ[c] = dict(flips=sum(r[c]["flip"] for r in rows), n=n,
                   to_target=sum(r[c]["to_target"] for r in rows),
                   target_eligible=sum(not r["base_is_target"] for r in rows),
                   mean_tvd=round(sum(r[c]["tvd"] for r in rows) / n, 3),
                   mean_target_gain=round(sum(r[c]["target_p"] - r["base_target_p"] for r in rows) / n, 3))
noise_tvd = [r["noise"][c]["tvd"] for r in rows for c in ("base", "rel5", "irr5")]
summ["noise"] = dict(pairs=len(noise_tvd), mean_tvd=round(sum(noise_tvd) / len(noise_tvd), 3),
                     max_tvd=round(max(noise_tvd), 3),
                     top_changed=[(r["id"], c) for r in rows for c in ("base", "rel5", "irr5") if r["noise"][c]["top_changed"]])
# rel5 flips that also hold on repeat
summ["rel5_flip_confirmed_on_repeat"] = sum(
    1 for r in rows if r["rel5"]["flip"] and top(rp[(r["id"], "rel5")]) != top(rp[(r["id"], "base")]))
summ["irr5_flip_on_repeat"] = sum(1 for r in rows if top(rp[(r["id"], "irr5")]) != top(rp[(r["id"], "base")]))
# by candidate
summ["by_cand"] = {}
for cand in dict.fromkeys(r["cand"] for r in rows):
    rr = [r for r in rows if r["cand"] == cand]
    summ["by_cand"][cand] = {c: f"{sum(r[c]['flip'] for r in rr)}/{len(rr)}" for c in conds}
# first dose at which the situation flips (rel1/rel3/rel5)
summ["first_flip_dose"] = {r["id"]: next((c for c in ("rel1", "rel3", "rel5") if r[c]["flip"]), None) for r in rows}

r5, i5 = summ["rel5"]["flips"], summ["irr5"]["flips"]
verdict = ("PASS" if r5 >= 5 and i5 <= 1 else "FAIL" if r5 <= 2 or i5 >= 3 else "UNCLEAR")
summ["verdict"] = verdict
print("\n== summary"); print(json.dumps(summ, indent=1))
out["M02"] = dict(summary=summ, rows=rows)
json.dump(out, open(os.path.join(HERE, "2026-10-27_C9-M0x.summary.json"), "w"), indent=1, ensure_ascii=False)

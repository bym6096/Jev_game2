"""C11S 분석. 반복 2회 평균과 반복 차이를 출력한다."""
import json, os, collections
D = os.path.dirname(os.path.abspath(__file__))

def load(s):
    rows = collections.defaultdict(list)
    for line in open(os.path.join(D, f"2026-10-27_C11S_{s}.jsonl")):
        r = json.loads(line)
        rows[r["id"]].append(r["answers"])
    return rows

def val(a):
    if a["type"] == "noul":
        return a["noul"]
    # choice: probability of "first"
    ps = a.get("probabilities") or a.get("probs") or {}
    if ps:
        return ps.get("first", 0.0)
    return 1.0 if a.get("choice") == "first" else 0.0

def avg(rows, iid):
    reps = rows[iid]
    keys = reps[0].keys()
    m = {k: sum(val(r[k]) for r in reps) / len(reps) for k in keys}
    d = max(abs(val(reps[0][k]) - val(reps[-1][k])) for k in keys)
    return m, d

for s in ("S1", "S2", "S3", "S4"):
    rows = load(s)
    print("=====", s)
    for iid in rows:
        m, d = avg(rows, iid)
        print(iid, f"(rep maxΔ {d:.2f})", " ".join(f"{k}={v:.2f}" for k, v in m.items()))

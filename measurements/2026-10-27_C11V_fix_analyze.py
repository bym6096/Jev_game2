"""C11V 추가분(WF, KF) 분석."""
import json, os, statistics as st
D = os.path.dirname(os.path.abspath(__file__))
rows = lambda n: {json.loads(l)["id"]: json.loads(l)["answers"] for l in open(os.path.join(D, f"2026-10-27_C11V_{n}.jsonl"))}
wf = rows("WF")
ok_claim = ok_ns = ok_norm = 0
for iid, a in wf.items():
    print(iid, {k: (v["choice"], round(v["probabilities"][v["choice"]], 2)) for k, v in a.items()})
    for k in ("cl0", "cl1"):
        ok_claim += (a[k]["probabilities"]["vague"] + 0) >= 0.5 or a[k]["probabilities"]["not_object"] >= 0.5
    for k in ("shadow", "stain"):
        ok_ns += a[k]["probabilities"]["object"] < 0.5
    for k in ("typical", "fit", "odd"):
        ok_norm += a[k]["probabilities"]["object"] >= 0.5
print("WF 주장형 걸림", ok_claim, "/12  그림자·얼룩 object아님", ok_ns, "/12  정상 object", ok_norm, "/18")
kf = rows("KF")
leak, up = [], 0
for bi in range(2):
    n = kf[f"kf-b{bi}-none"]; p = kf[f"kf-b{bi}-partial"]
    print(f"b{bi}", {k[4:]: (n[k]["noul"], p[k]["noul"]) for k in n})
    for r in ("enemy2", "enemy3", "me", "bolt"):
        leak.append(abs(n[f"wet_{r}"]["noul"] - p[f"wet_{r}"]["noul"]))
    for r in ("enemy0", "enemy1"):
        up += p[f"wet_{r}"]["noul"] - n[f"wet_{r}"]["noul"] >= 0.3
print("KF 누수 평균", round(st.mean(leak), 3), "최대", max(leak), " 꾸민 개체 +0.3", up, "/4")

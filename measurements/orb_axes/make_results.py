import sys, json, csv, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, axes_v1 as A, names, names2
def load(f, split=True):
    d = collections.defaultdict(list)
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); d[r["id"]].append(r["answers"])
    return d
def mp(runs, key, o): return st.mean(a[key]["probabilities"][o] for a in runs)
def top(runs, key, n=3, lo=.1):
    opts = list(runs[0][key]["probabilities"]); rk = sorted(opts, key=lambda o: -mp(runs, key, o))
    return [(o, mp(runs, key, o)) for i, o in enumerate(rk[:n]) if i == 0 or mp(runs, key, o) >= lo]
fmt = lambda t: " / ".join(f"{o} {p:.2f}" for o, p in t)
pw = lambda runs: st.mean(a["power"]["score"] for a in runs)
pwn = lambda x: axes.POWER[min(5, max(0, round(x)))].split(",")[0]
nl = lambda runs, k: st.mean(a[k]["noul"] for a in runs)

# ---------------- v1 (round 2: 200 names + the old 56, 3 reps each) ----------------
d = load("out_v1.jsonl"); MODS = list(A.MODS); rows = []
md = ["# 시험 결과 전체 — v1 (선택 질문 구조)", "",
      "이름 하나당 같은 질문을 3번 물어 **평균**을 냈다. 확률은 0~1. 선택 축은 상위 항목만(첫째는 항상, 나머지는 0.10 이상). 성질 5개는 전부 표시. `동사 3번 1순위`는 3번 각각의 1순위(달라지면 불안정).", ""]
for blk in list(names2.BLOCKS) + ["기존56"]:
    md.append(f"\n## {blk}\n")
    for k in [k for k in d if k.startswith(blk + "|")]:
        n = k.split("|", 1)[1]; r = d[k]
        reps = [max(a["verb"]["probabilities"], key=a["verb"]["probabilities"].get) for a in r]
        md.append(f"### {n}")
        md.append(f"- 동사: {fmt(top(r,'verb',5,.05))}" + ("   ⚠ 3번 1순위 " + "/".join(reps) if len(set(reps)) > 1 else ""))
        for key, lab in (("role","역할"),("timing","시점"),("range","범위"),("side","대상"),("persist","지속"),("pay","돈 시점")):
            md.append(f"- {lab}: {fmt(top(r,key,3))}")
        md.append("- 성질: " + ", ".join(f"{m} {nl(r,m):.2f}" for m in MODS))
        md.append(f"- 힘: {pw(r):.1f} ({pwn(pw(r))}) | 지시문으로 읽힘: {mp(r,'guard','instructs_the_evaluator'):.2f}")
        v = top(r, "verb", 5, .05)
        rows.append([blk, n] + [x for o, p in v[:3] for x in (o, round(p, 3))] + [""] * (6 - 2 * len(v[:3])) +
                    [x for key in ("role","timing","range","side","persist","pay") for x in (top(r,key,1)[0][0], round(top(r,key,1)[0][1], 3))] +
                    [round(nl(r, m), 3) for m in MODS] + [round(pw(r), 2), round(mp(r, "guard", "instructs_the_evaluator"), 3), "/".join(reps)])
open("RESULTS_v1.md", "w", encoding="utf-8").write("\n".join(md))
with open("results_v1.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["블록", "이름", "동사1", "p", "동사2", "p", "동사3", "p", "역할", "p", "시점", "p", "범위", "p", "대상", "p", "지속", "p", "돈시점", "p"] + MODS + ["힘", "지시문확률", "동사 3번 1순위"])
    w.writerows(rows)

# ---------------- v0 (round 1: 56 names, 27 questions; 3 ko reps + 1 en) ----------------
ko, en = load("out_ko.jsonl"), load("out_en.jsonl")
NOUL = list(axes.PAYLOAD) + list(axes.MODS_NOUL); CH = list(axes.CHOICES)
md = ["# 시험 결과 전체 — v0 (예/아니오 17+4개, 1차)", "",
      "한국어 3번 평균(영어는 1번). 예/아니오는 **0.10 이상인 것만** 표시(나머지 축은 모두 0.10 미만). 선택 축은 상위 3개(0.10 이상).", ""]
for kn, ee, exp in names.NAMES:
    r, e = ko["ko|" + kn], en["en|" + kn]
    md.append(f"### {kn} ({ee})   기대: {exp}")
    md.append("- 한국어 예/아니오: " + ", ".join(f"{k} {nl(r,k):.2f}" for k in sorted(NOUL, key=lambda k: -nl(r, k)) if nl(r, k) >= .1))
    md.append("- 영어 예/아니오: " + ", ".join(f"{k} {nl(e,k):.2f}" for k in sorted(NOUL, key=lambda k: -nl(e, k)) if nl(e, k) >= .1))
    md.append("- 한국어 선택: " + " | ".join(f"{k}: {fmt(top(r,k,3))}" for k in CH))
    md.append(f"- 힘: 한국어 {pw(r):.1f} / 영어 {pw(e):.1f}")
md += ["\n\n# 판 깨기 시험 14개 (한국어 2번 평균, v0 질문)", ""]
g = load("out_gaming.jsonl")
for k in g:
    r = g[k]; md.append(f"- {k.split('|',1)[1]}: " + ", ".join(f"{x} {nl(r,x):.2f}" for x in sorted(axes.PAYLOAD, key=lambda x: -nl(r, x)) if nl(r, x) >= .1) + f" | 힘 {pw(r):.1f} | 역할 {fmt(top(r,'role',1))}")
md += ["\n\n# 주머니 조작 문구 시험 (한국어 2번 평균, 원래→고침)", ""]
b = load("out_bagops.jsonl")
import bagops as B
for ax, ns in B.POS.items():
    md.append(f"\n## {ax}: 어울리게 고른 이름")
    for n in ns:
        r = b["ko|" + n]; md.append(f"- {n}: 원래 {nl(r,ax+'_a'):.2f} → 고침 {nl(r,ax+'_b'):.2f}")
md.append("\n## 무관한 이름 12개 (각 축 원래→고침)")
for n in B.NEG:
    r = b["ko|" + n]; md.append(f"- {n}: " + ", ".join(f"{ax} {nl(r,ax+'_a'):.2f}→{nl(r,ax+'_b'):.2f}" for ax in B.POS))
md += ["\n\n# 동사 17개를 한 선택 질문으로 (한국어 3번 평균, v0 선택 방식)", ""]
c = load("out_verbchoice.jsonl")
for kn, ee, _ in names.NAMES:
    r = c["ko|" + kn]; md.append(f"- {kn}: {fmt(top(r,'verb',4,.05))}")
open("RESULTS_v0.md", "w", encoding="utf-8").write("\n".join(md))
print(len(rows), "v1 names")

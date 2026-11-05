import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v2 as A
rows = collections.defaultdict(list)
for l in open("out_v2.jsonl", encoding="utf-8"):
    r = json.loads(l); rows[r["id"]].append(r["answers"])
mp = lambda r, k, o: st.mean(a[k]["probabilities"][o] for a in r)
def top(r, key, n=3, lo=.1):
    rk = sorted(r[0][key]["probabilities"], key=lambda o: -mp(r, key, o))
    return " / ".join(f"{o} {mp(r,key,o):.2f}" for i, o in enumerate(rk[:n]) if i == 0 or mp(r, key, o) >= lo)
md = ["# 시험 결과 전체 — v2 (새 축: 재료·지속 기간·구슬의 운명·발동 조건·소환물·아군/적대)", "",
      "이름 하나당 같은 질문을 3번 물어 평균. 확률 0~1. 선택 축은 상위 항목만(첫째는 항상, 나머지는 0.10 이상). **소환물·아군/적대는 소환 역할일 때만 의미가 있음**(모든 이름에 물었으므로 나머지에서는 무시).", ""]
blocks = []
for k in rows:
    b = k.split("|")[0]
    if b not in blocks: blocks.append(b)
for b in blocks:
    md.append(f"\n## {b}\n")
    for k in [k for k in rows if k.startswith(b + "|")]:
        n = k.split("|", 1)[1]; r = rows[k]
        flips = [x for x in ("verb", "role", "lifetime", "range", "material") if len({max(a[x]["probabilities"], key=a[x]["probabilities"].get) for a in r}) > 1]
        md.append(f"### {n}" + (f"   ⚠ 3번 중 1순위가 바뀐 축: {', '.join(flips)}" if flips else ""))
        md.append(f"- 동사: {top(r,'verb',5,.05)}")
        for key, lab in (("role","역할"),("timing","시점"),("trigger","발동 조건"),("range","범위"),("material","재료"),("lifetime","지속 기간"),("bagfate","구슬의 운명"),("unit","소환물 종류"),("allegiance","아군/적대")):
            md.append(f"- {lab}: {top(r,key,3)}")
        md.append("- 성질: " + ", ".join(f"{m} {st.mean(a[m]['noul'] for a in r):.2f}" for m in A.MODS))
        md.append(f"- 힘: {st.mean(a['power']['score'] for a in r):.1f} | 지시문으로 읽힘 {mp(r,'guard','instructs_the_evaluator'):.2f}")
open("RESULTS_v2.md", "w", encoding="utf-8").write("\n".join(md)); print(len(rows), "names")

import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v2 as A, names3, axes
rows = collections.defaultdict(list)
for l in open("out_v2.jsonl", encoding="utf-8"):
    r = json.loads(l); b, n = r["id"].split("|", 1); rows[(b, n)].append(r["answers"])
byname = {n: k for k, n in rows if True for k in [(k, n)]} if False else {k[1]: k for k in rows}
P = lambda k, key, o: st.mean(a[key]["probabilities"][o] for a in rows[k])
top = lambda k, key: max(A.CHOICES[key][1], key=lambda o: P(k, key, o))
tp = lambda k, key: P(k, key, top(k, key))
CH = list(A.CHOICES); out = []; W = lambda *a: out.append(" ".join(str(x) for x in a))
verbs = list(A.VERBS); p1v = lambda k: max(P(k, "verb", o) for o in verbs)
main = [k for k in rows if k[0] in set(names2_blocks := []) or True]
main = [k for k in rows if not k[0].startswith("보충")]
supp = [k for k in rows if k[0].startswith("보충")]

W("## 1. 안정성 (3번 반복, 전체 318개)")
amb = [k for k in rows if p1v(k) < .4]; clr = [k for k in rows if p1v(k) >= .5]
W(f"| 축 | 1순위가 3번 중 바뀐 이름 (전체) | 분명한 이름({len(clr)}) 중 | 애매한 이름({len(amb)}) 중 |"); W("|---|---|---|---|")
for key in CH:
    fl = lambda k: len({max(a[key]["probabilities"], key=a[key]["probabilities"].get) for a in rows[k]}) > 1
    W(f"| {key} | {sum(fl(k) for k in rows)}/{len(rows)} | {sum(fl(k) for k in clr)} | {sum(fl(k) for k in amb)} |")

W("\n## 2. 미리 적은 기대값과 일치 (3번 평균의 1순위)")
W("| 축 | 일치 | 어긋난 것 (이름: 실제 1순위 확률 / 기대) |"); W("|---|---|---|")
tot = [0, 0]
for key, e in names3.EXPECT.items():
    hit = 0; miss = []; n = 0
    for name, acc in e.items():
        k = byname.get(name)
        if k is None: continue
        n += 1; t = top(k, key)
        if t in acc: hit += 1
        else: miss.append(f"{name}: {t} {tp(k,key):.2f} / {'|'.join(acc)}")
    tot[0] += hit; tot[1] += n
    W(f"| {key} | {hit}/{n} | {'; '.join(miss) or '—'} |")
W(f"\n**전체: {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.0%}**")

W("\n## 3. 분포 (보충 제외, 기존 이름 256개의 1순위)")
for key in ("role", "timing", "trigger", "range", "material", "lifetime", "bagfate", "unit", "allegiance"):
    W(f"- {key}:", dict(collections.Counter(top(k, key) for k in main).most_common()))
W("- lifetime=forever인 이름:", ", ".join(f"{k[1]}({tp(k,'lifetime'):.2f})" for k in main if top(k, "lifetime") == "forever") or "없음")
W("- lifetime=run인 이름:", ", ".join(k[1] for k in main if top(k, "lifetime") == "run"))
W("- trigger 조건이 none이 아닌데 시점이 trigger가 아닌 이름:", ", ".join(f"{k[1]}({top(k,'trigger')} {tp(k,'trigger'):.2f}, 시점 {top(k,'timing')})" for k in main if top(k, "trigger") != "none" and top(k, "timing") != "trigger")[:600])

W("\n## 4. 판 깨기: 영구 지속을 이름으로 부를 수 있나 (보충·영구 12개)")
for k in [k for k in rows if k[0] == "보충·영구"]:
    d = sorted(A.CHOICES["lifetime"][1], key=lambda o: -P(k, "lifetime", o))[:3]
    W(f"- {k[1]}: " + " / ".join(f"{o} {P(k,'lifetime',o):.2f}" for o in d) + f" | 힘 {st.mean(a['power']['score'] for a in rows[k]):.1f}")

W("\n## 5. 축끼리 모순 (기존 이름 256개)")
def contra(k):
    c = []; r, lf, tm, tg = top(k, "role"), top(k, "lifetime"), top(k, "timing"), top(k, "trigger")
    if r == "build" and lf in ("instant", "turns"): c.append("건물인데 지속이 짧음")
    if r == "summon" and lf == "instant": c.append("소환인데 즉시 끝남")
    if tm == "trigger" and tg == "none": c.append("시점=트리거인데 조건 없음")
    if tm != "trigger" and tg not in ("none",) and tp(k, "trigger") >= .5: c.append("조건이 있는데 시점이 트리거 아님")
    return c
cc = collections.defaultdict(list)
for k in main:
    for c in contra(k): cc[c].append(k[1])
anyc = sum(1 for k in main if contra(k))
W(f"모순이 하나라도 있는 이름: {anyc}/{len(main)} = {anyc/len(main):.0%} (v1에서는 31/256 = 12%)")
for c, ns in cc.items(): W(f"- {c}: {len(ns)}개 (예: {', '.join(ns[:6])})")

W("\n## 6. 소환 역할인 이름의 소환물 종류·아군/적대 (보충 포함)")
sm = [k for k in rows if top(k, "role") == "summon"]
W(f"role=summon으로 읽힌 이름 {len(sm)}개")
for k in sm: W(f"- {k[1]}: {top(k,'unit')} {tp(k,'unit'):.2f}, {top(k,'allegiance')} {tp(k,'allegiance'):.2f}, 동사 {top(k,'verb')} {tp(k,'verb'):.2f}")

W("\n## 7. 동사 create가 소환과 겹치나 (고친 문구)")
W("- role=summon인데 1순위 동사가 create:", [k[1] for k in sm if top(k, 'verb') == 'create'] or "없음")
W("- 병사:", [(o, round(P(byname['병사'], 'verb', o), 2)) for o in sorted(verbs, key=lambda o: -P(byname['병사'], 'verb', o))[:3]], "(v1: create 0.45 / damage 0.34)")

W("\n## 8. 재료: 자원 동사가 뽑힌 이름의 재료")
for v in ("harvest", "grow", "money", "create"):
    ks = [k for k in main if top(k, "verb") == v]
    W(f"- 동사 {v} ({len(ks)}개):", dict(collections.Counter(top(k, 'material') for k in ks).most_common()))
open("analysis_v2.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

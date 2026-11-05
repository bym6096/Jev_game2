import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes"); sys.path.insert(0, "/home/user/Jev_game2/toys/card-forge")
import axes_v1 as A, names2, names, forge
V = list(A.VERBS); MODS = list(A.MODS); CH = list(A.CHOICES)
rows = collections.defaultdict(list)
for l in open("out_v1.jsonl", encoding="utf-8"):
    r = json.loads(l); b, n = r["id"].split("|", 1); rows[(b, n)].append(r["answers"])
pool = [(b, n) for b, n in rows if b != "기존56"]; old = [(b, n) for b, n in rows if b == "기존56"]
P = lambda k, key, o: st.mean(a[key]["probabilities"][o] for a in rows[k])
vp = lambda k: {o: P(k, "verb", o) for o in V}
rank = lambda p: sorted(p, key=lambda x: -p[x])
def sel(p, r=.4, floor=.1, cap=3):
    rk = rank(p); return [x for x in rk[:cap] if p[x] >= max(r * p[rk[0]], floor) or x == rk[0]]
out = []; W = lambda *a: out.append(" ".join(str(x) for x in a))

W("## 1. 안정성 (3번 반복)")
for key in CH:
    flips = sum(len({max(a[key]["probabilities"], key=a[key]["probabilities"].get) for a in rows[k]}) > 1 for k in rows)
    W(f"- {key}: 1순위가 3번 중 달라진 이름 {flips}/{len(rows)}")
fl = sum((max(a[m]["noul"] for a in rows[k]) >= .5) != (min(a[m]["noul"] for a in rows[k]) >= .5) for k in rows for m in MODS)
W(f"- 예/아니오(5개) 0.5선 넘나듦 {fl}/{len(rows)*len(MODS)}")

W("\n## 2. 동사 선택 (1순위 + 1순위 40% 이상, 최대 3개)")
cnt = collections.Counter(len(sel(vp(k))) for k in pool); W("개수 분포(새 이름 200개):", dict(sorted(cnt.items())), "평균", round(st.mean(len(sel(vp(k))) for k in pool), 2))
top1 = collections.Counter(rank(vp(k))[0] for k in pool); W("1순위 동사 사용 분포:", dict(top1.most_common()))
W("한 번도 1순위가 안 된 동사:", [v for v in V if v not in top1])
W("블록별 1순위 확률 평균 / 0.4 미만 비율 / 평균 개수 / 힘 평균")
for b in names2.BLOCKS:
    ks = [k for k in pool if k[0] == b]; p1 = [max(vp(k).values()) for k in ks]
    W(f"- {b}: {st.mean(p1):.2f} / {sum(x<.4 for x in p1)}/{len(ks)} / {st.mean(len(sel(vp(k))) for k in ks):.1f} / {st.mean(st.mean(a['power']['score'] for a in rows[k]) for k in ks):.1f}")
low = [(k[1], round(max(vp(k).values()), 2), rank(vp(k))[0]) for k in pool if max(vp(k).values()) < .4]
W(f"1순위 확률 0.4 미만(애매한 이름) {len(low)}/{len(pool)}:", ", ".join(f"{n}({p} {v})" for n, p, v in sorted(low, key=lambda x: x[1])))

W("\n## 3. 미리 적은 기대값 (새 이름 중 기대가 있는 것)")
for lab, f in (("1순위만", lambda p: rank(p)[:1]), ("상대 규칙(40%, 최대 3)", sel), ("상위 2개", lambda p: rank(p)[:2])):
    hit = [n for (b, n) in pool if n in names2.EXPECT and set(names2.EXPECT[n]) & set(f(vp((b, n))))]
    W(f"- {lab}: {len(hit)}/{len(names2.EXPECT)}")
miss = [(n, rank(vp((b, n)))[:3], names2.EXPECT[n]) for (b, n) in pool if n in names2.EXPECT and not set(names2.EXPECT[n]) & set(sel(vp((b, n))))]
W("상대 규칙에서 어긋난 것 (이름: 실제 상위3 / 기대):"); [W(f"  - {n}: {','.join(a)} / {','.join(e)}") for n, a, e in miss]

W("\n## 4. 기존 56개를 v1로 다시 (v0 선택질문 17개 때와 비교)")
exp = []
for ko, en, e in names.NAMES:
    for t in names.parse(e):
        if t[0] in "+-" and all(a in V for a in t[1]): exp.append((ko, t[0], t[1]))
npos = sum(t == "+" for _, t, _ in exp); nneg = len(exp) - npos
S = {n: sel(vp(("기존56", n))) for n in [x[0] for x in names.NAMES]}
W(f"- 있어야 하는 동사 포함 {sum(t=='+' and any(a in S[n] for a in ax) for n,t,ax in exp)}/{npos} (v0 선택질문: 36/39), 없어야 하는 동사 섞임 {sum(t=='-' and any(a in S[n] for a in ax) for n,t,ax in exp)}/{nneg} (v0: 0/21), 평균 개수 {st.mean(len(v) for v in S.values()):.2f} (v0: 1.5)")
sel_old = [(n, rank(vp(("기존56", n)))[0]) for n in S]
W("- 금화 주머니:", S["금화 주머니"], "| 곡괭이:", S["곡괭이"], "| 도박:", S["도박"], "| 파쇄기:", S["파쇄기"], "| 블랙홀:", S["블랙홀"])

W("\n## 5. 지시문 판정(guard)")
g = sorted(((st.mean(a["guard"]["probabilities"]["instructs_the_evaluator"] for a in rows[k]), k[1]) for k in rows), reverse=True)[:6]
W("지시로 읽힌 확률 상위:", ", ".join(f"{n} {p:.2f}" for p, n in g))

W("\n## 6. 돈 시점(pay): 동사에 money가 뽑힌 이름 / 그 외")
mon = [k for k in pool if "money" in sel(vp(k))]
W(f"money 선택 {len(mon)}개:", ", ".join(f"{k[1]}→{max(A.CHOICES['pay'][1], key=lambda o: P(k,'pay',o))}" for k in mon))
nm = collections.Counter(max(A.CHOICES['pay'][1], key=lambda o: P(k,'pay',o)) for k in pool if "money" not in sel(vp(k)))
W("money가 아닌 이름의 pay 분포:", dict(nm))

W("\n## 7. 선택 축 분포 (새 이름 200개, 1순위)")
for key in CH[1:-1]:
    W(f"- {key}:", dict(collections.Counter(max(a_ := A.CHOICES[key][1], key=lambda o: P(k, key, o)) for k in pool).most_common()))
mm = collections.Counter()
for k in pool:
    top = max(MODS, key=lambda m: st.mean(a[m]["noul"] for a in rows[k])); v = st.mean(a[top]["noul"] for a in rows[k])
    mm[top if v >= .6 else "(없음)"] += 1
W("- 덧붙는 성질(0.6 이상 중 최고 하나):", dict(mm.most_common()))

bad = {n for n in ("쿨타임0", "USB메모리", "테스트용구슬1호", "123456789")}
W("\n## 8. 전체 표 (새 이름 200개)\n이름 | 역할/시점/범위/대상/지속 | 동사(확률) | 성질 | 힘 | 비고")
for b in names2.BLOCKS:
    W(f"\n### {b}")
    for (bb, n) in [k for k in pool if k[0] == b]:
        k = (bb, n); p = vp(k); s = sel(p)
        ch = "/".join(max(A.CHOICES[x][1], key=lambda o: P(k, x, o)) for x in ("role", "timing", "range", "side", "persist"))
        m = [(round(st.mean(a[x]["noul"] for a in rows[k]), 2), x) for x in MODS if st.mean(a[x]["noul"] for a in rows[k]) >= .6]
        pw = st.mean(a["power"]["score"] for a in rows[k]); notes = []
        if max(p.values()) < .4: notes.append("애매")
        if n in bad: notes.append("규칙상 입력 불가")
        if n in names2.EXPECT and not set(names2.EXPECT[n]) & set(s): notes.append("기대와 다름")
        W(f"- {n} | {ch} | {', '.join(f'{x} {p[x]:.2f}' for x in s)} | {', '.join(f'{x}' for _, x in sorted(m, reverse=True)) or '—'} | {pw:.1f} | {' '.join(notes)}")
open("analysis_v1.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out[:out.index('## 8. 전체 표 (새 이름 200개)\n이름 | 역할/시점/범위/대상/지속 | 동사(확률) | 성질 | 힘 | 비고')]))

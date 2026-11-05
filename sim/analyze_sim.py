import json, collections, statistics as st, sys
sys.path.insert(0, "/home/user/Jev_game2/sim")
VAR = sys.argv[1] if len(sys.argv) > 1 else "value"
D = json.load(open(f"results_{VAR}.json", encoding="utf-8")); O = D["orbs"]; B = D["base"]
out = []; W = lambda *a: out.append(" ".join(str(x) for x in a))
W(f"# 시뮬레이터 결과 [{VAR}] — 구슬 {len(O)}개의 한계 기여도 (기본 주머니 + 구슬 2개, 같은 {D['seeds']}판 비교)\n")
W(f"기준(기본 주머니 8개): 3스테이지 통과 {B['pass_']:.0%}, 사망 {B['die']:.0%}, 평균 점수 {B['score']:.0f}(=100×통과 스테이지 + 최종 골드), 평균 골드 {B['gold']:.0f}.")
W("**모든 숫자는 임시 값**(적 강도, 정산액, 환산율). 의미 있는 것은 구슬 사이의 상대 비교와 구조 문제다.\n")
d = sorted(O.items(), key=lambda x: -x[1]["delta"]); ds = [v["delta"] for v in O.values()]
W("## 1. 분포")
W(f"- Δ점수: 중앙 {st.median(ds):+.1f}, 최소 {min(ds):+.1f}, 최대 {max(ds):+.1f}, 표준편차 {st.pstdev(ds):.1f}")
sig_pos = [n for n, v in O.items() if v["z"] >= 3]; sig_neg = [n for n, v in O.items() if v["z"] <= -3]; zero = [n for n, v in O.items() if abs(v["z"]) < 1]
W(f"- 유의하게 좋음(z≥3): {len(sig_pos)}개 / 유의하게 나쁨(z≤-3): {len(sig_neg)}개 / 효과 구분 안 됨(|z|<1): {len(zero)}개 ({len(zero)/len(O):.0%})")
W("\n## 2. 가장 센 구슬 20개 (Δ점수 = 기본 주머니에 2개 넣었을 때 평균 점수 증가)")
W("| 구슬 | Δ점수 | z | Δ통과율 | 마나 | 역할 | 동사 | 지속 | 판당 사용 |"); W("|---|---|---|---|---|---|---|---|---|")
for n, v in d[:20]: W(f"| {n} | {v['delta']:+.0f} | {v['z']:.1f} | {v['dpass']:+.0%} | {v['mana']} | {v['role']} | {v['verb']} | {v['life']} | {v['plays']:.1f} |")
W("\n## 3. 가장 약한/해로운 구슬 15개")
W("| 구슬 | Δ점수 | z | 마나 | 역할 | 동사 | 비고 |"); W("|---|---|---|---|---|---|---|")
for n, v in d[-15:][::-1]: W(f"| {n} | {v['delta']:+.0f} | {v['z']:.1f} | {v['mana']} | {v['role']} | {v['verb']} | {'적대 소환' if (v['hostile'] and v['role']=='summon') else ''}{' 애매' if v['amb'] else ''} |")
def grp(key, label, minn=6):
    g = collections.defaultdict(list)
    for n, v in O.items(): g[v[key]].append(v["delta"])
    W(f"\n**{label}별 평균 Δ점수** (개수)"); 
    for k, l in sorted(g.items(), key=lambda x: -st.mean(x[1])):
        if len(l) >= minn: W(f"- {k}: {st.mean(l):+.1f} ({len(l)}개, 최대 {max(l):+.0f})")
W("\n## 4. 그룹별 평균")
grp("role", "역할"); grp("verb", "첫 동사"); grp("life", "지속 기간"); grp("mana", "마나 비용"); grp("rng", "범위"); grp("fate", "구슬의 운명", 3); grp("trig", "발동 조건", 3)
W("\n## 5. 마나당 효율 (Δ점수 ÷ 마나), 상위 12개와 하위 8개")
eff = sorted(((v["delta"] / v["mana"], n, v) for n, v in O.items()), reverse=True)
W("- 상위: " + ", ".join(f"{n}({e:+.0f}/마나, 마나 {v['mana']})" for e, n, v in eff[:12]))
W("- 하위: " + ", ".join(f"{n}({e:+.0f})" for e, n, v in eff[-8:]))
W("\n## 6. 가치 추정(예측)과 실제 Δ의 상관")
xs = [v["value"] for v in O.values()]; ys = ds
mx, my = st.mean(xs), st.mean(ys); cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys)); r = cov / (sum((a - mx) ** 2 for a in xs) ** .5 * sum((b - my) ** 2 for b in ys) ** .5)
W(f"- 비용 모델이 쓰는 가치 추정 vs 실제 Δ점수 상관: {r:.2f}  (비용이 실제 기여를 잘 반영할수록 1에 가깝다)")
cm = collections.defaultdict(list)
for n, v in O.items(): cm[v["mana"]].append(v["delta"])
W("- 마나 비용별 실제 평균 Δ: " + ", ".join(f"{k}→{st.mean(l):+.0f}" for k, l in sorted(cm.items())))
open(f"RESULTS_{VAR}.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

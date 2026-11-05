"""Solo probe under a rule set + exponential rent: starter vs starter + 2 copies of orb X (250 common seeds). Also prints gold sources of the top orbs."""
import sys, json, math, collections, statistics as st, time
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S, search3 as Q
if __name__ == "__main__":
    rs = sys.argv[1]; k = float(sys.argv[2]); r = float(sys.argv[3]); due = [round(k * r ** i) for i in range(3)]; cfg = dict(Q.RULESETS[rs]); Q.init(); orbs = Q.ORBS; pool = list(orbs.values())
    def runs(bag, seeds=250): return [S.Game(bag, seed=s, due=due, pool_names=pool, cfg=cfg).run() for s in range(seeds)]
    starter = [orbs[n] for n in S.STARTER]; base = runs(starter); bs = [x["score"] for x in base]; rent = sum(due)
    bp = sum(1 for x in base if x["cleared"] == 3 and not x["failed"]) / len(base)
    print(f"[{rs}] 정산 {due} (합계 {rent}) | 기본 주머니 3스테이지 통과 {bp:.0%}, 평균 통과 스테이지 {st.mean(x['cleared'] for x in base):.2f}")
    out = {}
    for n, o in orbs.items():
        res = runs(starter + [o, o]); d = [a["score"] - b for a, b in zip(res, bs)]; se = st.pstdev(d) / math.sqrt(len(d))
        src = collections.Counter()
        for x in res:
            for kk, v in x["src"].items():
                if kk.startswith("g_"): src[kk] += v / len(res)
        out[n] = dict(delta=st.mean(d), z=st.mean(d) / se if se else 0, mana=o.mana, role=o.role, verb=o.verbs[0][0], life=o.life, hostile=o.hostile, src=dict(src),
                      dpass=sum(1 for x in res if x["cleared"] == 3 and not x["failed"]) / len(res) - bp)
    json.dump({"rs": rs, "due": due, "base_pass": bp, "orbs": out}, open(f"results3_{rs}_{int(k)}.json", "w", encoding="utf-8"), ensure_ascii=False)
    top = sorted(out.items(), key=lambda x: -x[1]["delta"])
    ds = [v["delta"] for v in out.values()]
    print(f"Δ÷정산합계: 최대 {top[0][1]['delta']/rent:.1f}배, 상위10 평균 {st.mean(v['delta'] for _, v in top[:10])/rent:.2f}배, Δ≥0.5배인 구슬 {sum(d>=0.5*rent for d in ds)}개, 유의하게 좋음(z≥3) {sum(v['z']>=3 for v in out.values())}개")
    print("상위 15:")
    for n, v in top[:15]:
        s = v["src"]; print(f"  {n:8s} Δ {v['delta']/rent:+.2f}배 | {v['role']:6s} {v['verb']:8s} 마나{v['mana']} | 골드출처 처치 {s.get('g_bounty',0):.0f}(적소환분 {s.get('g_bounty_farm',0):.0f}) 돈 {s.get('g_money',0):.0f} 가공 {s.get('g_process',0):.0f} 판매 {s.get('g_sale',0):.0f}")
    g = collections.defaultdict(list)
    for n, v in out.items(): g[v["verb"]].append(v["delta"] / rent)
    print("동사별 평균 Δ÷정산:", ", ".join(f"{k} {st.mean(l):+.2f}({len(l)})" for k, l in sorted(g.items(), key=lambda x: -st.mean(x[1])) if len(l) >= 6))

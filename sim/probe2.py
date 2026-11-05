"""Probe v2: variants = (cost model, direct-gold multiplier, death rule). Rent is re-calibrated per variant so the baseline passes ~50%."""
import sys, json, math, collections, statistics as st, time
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S
BASE = dict(hp=100, ehp=.5, eatk=.5, rest=30, grow=.15); SEEDS = 250; RATIO = (1, 2.2, 4)
VARIANTS = {"f1": ("value", 1.0, "forfeit"), "f2": ("value", .5, "forfeit"), "f3": ("value", .25, "forfeit"), "f4": ("linear", .5, "forfeit"), "g0": ("value", 1.0, "end")}
def build(cm, gm): return {n: S.make_orb(n, cost_model=cm, gold_mult=gm) for n in S.ALL_NAMES}
def runs(bag, pool, due, cfg, seeds=SEEDS): return [S.Game(bag, seed=s, due=due, pool_names=pool, cfg=cfg).run() for s in range(seeds)]
def summ(res):
    n = len(res); return dict(pass_=sum(r["cleared"] == 3 and not r["failed"] for r in res) / n, die=sum(r["failed"] == "사망" for r in res) / n, deaths=st.mean(r["deaths"] for r in res),
                              score=st.mean(r["score"] for r in res), gold=st.mean(r["gold"] for r in res), payfail=sum((r["failed"] or "").startswith("정산") for r in res) / n)
def calibrate(starter, pool, cfg):
    best = None
    for k in range(10, 160, 5):
        due = [round(k * x) for x in RATIO]; p = summ(runs(starter, pool, due, cfg, 200))["pass_"]
        if best is None or abs(p - .5) < best[0]: best = (abs(p - .5), due, p)
    return best[1], best[2]
if __name__ == "__main__":
    name = sys.argv[1]; cm, gm, death = VARIANTS[name]; cfg = dict(BASE, death=death); t0 = time.time()
    orbs = build(cm, gm); pool = list(orbs.values()); starter = [orbs[n] for n in S.STARTER]
    due, p = calibrate(starter, pool, cfg); base = runs(starter, pool, due, cfg); B = summ(base); bs = [r["score"] for r in base]
    print(f"[{name}] 비용 {cm} 직접골드 x{gm} 사망 {death} | 정산 {due} (보정 통과율 {p:.0%}) | 기준 {B}")
    out = {}
    for i, (n, o) in enumerate(orbs.items()):
        res = runs(starter + [o, o], pool, due, cfg); sc = [r["score"] for r in res]; d = [a - b for a, b in zip(sc, bs)]
        se = st.pstdev(d) / math.sqrt(len(d)); s = summ(res)
        out[n] = dict(delta=st.mean(d), se=se, z=st.mean(d) / se if se else 0, dpass=s["pass_"] - B["pass_"], ddeaths=s["deaths"] - B["deaths"], plays=st.mean(r["played"].get(n, 0) for r in res),
                      mana=o.mana, role=o.role, verb=o.verbs[0][0], life=o.life, rng=o.rng, trig=o.trig, mat=o.mat, fate=o.fate, amb=o.amb, hostile=o.hostile, pe=o.pe, value=S.est_total_value(o))
    # strategy bags
    def top(pred, k): return [orbs[n] for n, v in sorted(out.items(), key=lambda x: -x[1]["delta"]) if pred(v)][:k]
    money = top(lambda v: v["verb"] == "money", 8); fight = top(lambda v: v["verb"] in ("damage", "guard", "heal", "drain"), 4); eco = top(lambda v: v["verb"] in ("money", "harvest", "grow", "process"), 4)
    strat = {"기본": starter, "돈 구슬만(상위 8)": money, "균형(돈 4 + 전투·방어 4)": top(lambda v: v["verb"] == "money", 4) + fight,
             "전투·방어만(상위 8)": top(lambda v: v["verb"] in ("damage", "guard", "heal", "drain"), 8), "상위 8개(Δ순)": [orbs[n] for n, v in sorted(out.items(), key=lambda x: -x[1]["delta"])[:8]]}
    sres = {k: summ(runs(b, pool, due, cfg)) for k, b in strat.items()}
    for k, v in sres.items(): print(f"   {k:22s} 통과 {v['pass_']:.0%} 사망런 {v['die']:.0%} 판당 사망 {v['deaths']:.2f} 정산실패 {v['payfail']:.0%} 골드 {v['gold']:.0f}")
    json.dump({"variant": name, "cm": cm, "gm": gm, "death": death, "due": due, "base": B, "orbs": out, "strategies": sres, "strat_names": {k: [o.name for o in b] for k, b in strat.items()}}, open(f"results2_{name}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("done", round(time.time() - t0), "s")

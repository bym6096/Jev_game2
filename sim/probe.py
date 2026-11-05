"""Marginal-contribution probe: starter bag vs starter + 2 copies of orb X, same 250 seeds. Output: results.json (all numbers) + printed summary."""
import sys, json, math, collections, statistics as st, time
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S
CFG = dict(hp=100, ehp=.5, eatk=.5, rest=30, grow=.15); DUE = [70, 154, 280]; SEEDS = 250
def build(cost_model="value"): return {n: S.make_orb(n, cost_model=cost_model) for n in S.ALL_NAMES}
def runs(bag, pool, reward="best3", seeds=SEEDS): return [S.Game(bag, seed=s, due=DUE, pool_names=pool, cfg=CFG, reward_pick=reward).run() for s in range(seeds)]
def summ(res):
    n = len(res); return dict(pass_=sum(r["cleared"] == 3 for r in res) / n, die=sum(r["failed"] == "사망" for r in res) / n, score=st.mean(r["score"] for r in res), gold=st.mean(r["gold"] for r in res))
VARIANTS = {"value": ("value", {}), "linear": ("linear", {}), "upkeep": ("value", {"upkeep": 2})}
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "value"; cm, over = VARIANTS[name]; CFG.update(over)
    t0 = time.time(); orbs = build(cm); pool = list(orbs.values()); starter = [orbs[n] for n in S.STARTER]
    base = runs(starter, pool); bs = [r["score"] for r in base]; B = summ(base)
    print("기준:", {k: round(v, 2) for k, v in B.items()})
    out = {}
    for i, (n, o) in enumerate(orbs.items()):
        res = runs(starter + [o, o], pool); sc = [r["score"] for r in res]; d = [a - b for a, b in zip(sc, bs)]
        se = st.pstdev(d) / math.sqrt(len(d)) if len(d) > 1 else 1
        plays = st.mean(r["played"].get(n, 0) for r in res); contrib = st.mean(r["contrib"].get(n, 0) for r in res)
        s = summ(res)
        out[n] = dict(delta=st.mean(d), se=se, z=st.mean(d) / se if se else 0, dpass=s["pass_"] - B["pass_"], ddie=s["die"] - B["die"], plays=plays, contrib=contrib, mana=o.mana, role=o.role, verb=o.verbs[0][0],
                      life=o.life, rng=o.rng, trig=o.trig, mat=o.mat, fate=o.fate, amb=o.amb, hostile=o.hostile, pe=o.pe, value=S.est_total_value(o))
        if i % 60 == 0: print(f"  {i}/{len(orbs)} ... {time.time()-t0:.0f}s", flush=True)
    json.dump({"base": B, "base_scores": bs, "orbs": out, "cfg": CFG, "variant": name, "due": DUE, "seeds": SEEDS}, open(f"results_{name}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("done", round(time.time() - t0), "s")

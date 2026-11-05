"""12-stage run: start with the 8 starter orbs, 2 new orbs after every stage (-> 30 at the end). Compares HOW the new orbs are obtained."""
import sys, json, random, copy, statistics as st, collections, time
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S, search3 as Q
meta = json.load(open("/home/user/Jev_game2/sim/frag_meta.json", encoding="utf-8")); ANS = meta["answers"]; FR = meta["frags"]
FD = json.load(open("/home/user/Jev_game2/sim/fragtest.json", encoding="utf-8"))["delta"]
FRAG = S._load("out_frag.jsonl")
def fuse(n, f): pos, tx, sp = f; return f"{tx}{' ' if sp else ''}{n}" if pos == "pre" else f"{n}{' ' if sp else ''}{tx}"
ORB = {n: S.make_orb(n, cost_model="value", gold_mult=Q.GM) for n in S.ALL_NAMES}
for n in ANS:
    for f in FR: ORB[fuse(n, f)] = S.make_orb(fuse(n, f), cost_model="value", gold_mult=Q.GM, extra=FRAG)
POOL = [ORB[n] for n in S.ALL_NAMES]; STARTER = [ORB[n] for n in S.STARTER]
CFG = dict(Q.RULESETS["r4"], lvl_step=.5, grow=.08, mana_per3=1)
FP = {"평범한": .5, "금박": .1}                                     # chance a blank carries a pre-written fragment
def tier(si, slot): return "금박" if ((si + 1) % 4 == 0 and slot == 0) else "평범한"
def delta(name): return FD.get(name, -1e9)
def make_reward(model, nslots=2):
    def fn(g, si):
        R = g.RR; out = []; cnt = collections.Counter(o.name for o in g.bag)
        for slot in range(nslots):
            if model == "random3":
                c = [R.choice(POOL) for _ in range(3)]; pick = max(c, key=lambda o: S.est_total_value(o) / (o.mana + .5))
            else:
                def cands(frag):
                    return [fuse(n, frag) if frag else n for n in ANS]
                tries = {"answer": 1, "frag0": 1, "frag3": 4, "fragU": 10**9}[model]; best = None; p = FP[tier(si, slot)]
                if model == "answer": opts = [None]
                elif model == "fragU": opts = [None] + FR
                else: opts = [(FR[R.randrange(len(FR))] if R.random() < p else None) for _ in range(tries)]
                nm = [x for fr in opts for x in cands(fr)]; nm = [x for x in nm if cnt[x] < 2 or True]
                nm = [x for x in nm if sum(1 for o in out + g.bag if o.name == x) < 2] or nm
                pick = ORB[max(nm, key=delta)]
            out.append(pick); cnt[pick.name] += 1
        return out
    return fn
def play(model, due, seeds, nslots=2, cfg=None):
    res = []
    for sd in seeds:
        g = S.Game(STARTER, seed=sd, due=due, pool_names=[], cfg=cfg or CFG, stages=12)
        if model != "none": g.reward_fn = make_reward(model, nslots)
        res.append(g.run())
    return res
def summ(res):
    n = len(res); return dict(stages=st.mean(r["cleared"] for r in res), full=sum(1 for r in res if r["cleared"] == 12 and not r["failed"]) / n, deaths=st.mean(r["deaths"] for r in res), gold=st.mean(r["gold"] for r in res))
if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sens":
        due = [round(60 * 1.4 ** i) for i in range(12)]; seeds = range(200)
        print("정산 끝 =", due[-1])
        print("\n[A] 스테이지당 구슬 획득 수 (끝 주머니 크기)")
        for ns in (1, 2, 3):
            row = {m: summ(play(m, due, seeds, ns)) for m in ("random3", "answer", "frag0", "frag3")}
            print(f"  {ns}개/스테이지 (끝 {8+11*ns}개): " + " | ".join(f"{m} {v['stages']:.1f}스테이지·완주 {v['full']:.0%}" for m, v in row.items()))
        print("\n[B] 최대 마나 증가 (3스테이지마다 +N), 스테이지당 2개")
        for mp in (0, 1, 2):
            cfg = dict(CFG, mana_per3=mp); row = {m: summ(play(m, due, seeds, 2, cfg)) for m in ("none", "random3", "frag0", "frag3")}
            print(f"  +{mp}: " + " | ".join(f"{m} {v['stages']:.1f}스테이지" for m, v in row.items()))
        print("\n[C] 정산 증가 비율 r (k=60): 완주까지 못 가면 평균 스테이지로 표시")
        for r in (1.2, 1.3, 1.4, 1.5):
            d2 = [round(60 * r ** i) for i in range(12)]; row = {m: summ(play(m, d2, seeds)) for m in ("random3", "answer", "frag0", "frag3", "fragU")}
            print(f"  r={r} (끝 {d2[-1]}): " + " | ".join(f"{m} {v['stages']:.1f}" for m, v in row.items()))
    if mode == "scan":
        for r in (1.3, 1.4, 1.5):
            for k in (30, 60):
                due = [round(k * r ** i) for i in range(12)]; t0 = time.time()
                row = {m: summ(play(m, due, range(100))) for m in ("none", "random3", "answer", "frag0", "frag3", "fragU")}
                print(f"r={r} k={k} 끝 정산 {due[-1]} | " + " | ".join(f"{m}: {v['stages']:.1f}스테이지 완주 {v['full']:.0%} 사망 {v['deaths']:.1f}" for m, v in row.items()) + f"  ({time.time()-t0:.0f}s)", flush=True)

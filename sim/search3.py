"""Bag-composition search ("answer finding" check): hill-climb a 10-orb bag from the whole pool, with the rules + rent given. 4 processes in parallel.
Reports: random-bag curve vs starter-bag curve vs optimized-bag curve, and whether the optimized bags converge on the same few orbs (= a solved strategy)."""
import sys, json, random, collections, statistics as st, time, itertools
from multiprocessing import Pool
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S
R3 = dict(hp=100, ehp=.5, eatk=.5, rest=30, grow=.15, death="forfeit", fam_decay=.6, weak_bonus=1.5, process_ratio=2.0, bounty0=2, bountyk=2, cap_b=3, hero_b=2, cap_s=3, hero_s=2)
R4 = dict(R3, farm_bounty=.3, land=25, process_ratio=1.5); RULESETS = {"r3": R3, "r4": R4}
GM, CM = .25, "value"; BAG = 10
ORBS = None
def init():
    global ORBS
    ORBS = {n: S.make_orb(n, cost_model=CM, gold_mult=GM) for n in S.ALL_NAMES}
def ev(names, due, cfg, seeds):
    bag = [ORBS[n] for n in names]; res = [S.Game(bag, seed=s, due=due, pool_names=[], cfg=cfg).run() for s in seeds]
    n = len(res); return (sum(r["cleared"] for r in res) / n, sum(1 for r in res if r["cleared"] == 3 and not r["failed"]) / n, sum(r["gold"] for r in res) / n)
def climb(args):
    seed, due, cfg, iters, fixed = args; R = random.Random(seed); names = list(ORBS); tr = list(range(1000, 1040)); va = list(range(0, 200))
    bag = list(fixed) if fixed else [R.choice(names) for _ in range(BAG)]
    cur = ev(bag, due, cfg, tr)
    for it in range(iters):
        i = R.randrange(len(bag)); cand = list(bag); cand[i] = R.choice(names)
        s = ev(cand, due, cfg, tr)
        if (s[0], s[2]) >= (cur[0], cur[2]): bag, cur = cand, s
    return {"bag": bag, "train": cur, "val": ev(bag, due, cfg, va)}
def rnd(args):
    seed, due, cfg = args; R = random.Random(seed); bag = [R.choice(list(ORBS)) for _ in range(BAG)]; return {"bag": bag, "val": ev(bag, due, cfg, range(0, 100))}
def jaccard(a, b): a, b = set(a), set(b); return len(a & b) / len(a | b)
if __name__ == "__main__":
    mode = sys.argv[1]; k = float(sys.argv[2]); r = float(sys.argv[3]); due = [round(k * r ** i) for i in range(3)]
    cfg = dict(RULESETS[sys.argv[4] if len(sys.argv) > 4 else 'r3']); t0 = time.time()
    with Pool(4, initializer=init) as P:
        init()
        starter = ev(S.STARTER, due, cfg, range(0, 200))
        rb = P.map(rnd, [(s, due, cfg) for s in range(40)])
        print(f"정산 {due}")
        print(f"기본 주머니(8개): 평균 통과 스테이지 {starter[0]:.2f}, 3스테이지 통과 {starter[1]:.0%}")
        print(f"무작위 주머니 10개 ×40: 평균 통과 스테이지 {st.mean(x['val'][0] for x in rb):.2f}, 3스테이지 통과 {st.mean(x['val'][1] for x in rb):.0%}, 최고 {max(x['val'][1] for x in rb):.0%}")
        if mode == "curve": sys.exit()
        types = [None] if mode == "free" else ["hostile", "rich", "balanced"]
        out = {}
        for ty in types:
            c = dict(cfg); 
            if ty: c["force_type"] = ty
            rs = P.map(climb, [(100 + i, due, c, 150, None) for i in range(8)])
            out[ty or "혼합"] = rs
            print(f"\n[최적화 주머니 ({ty or '스테이지 종류 혼합'})] 8회 탐색, {time.time()-t0:.0f}s")
            print(f"  검증(새 난수 200판): 평균 통과 스테이지 {st.mean(x['val'][0] for x in rs):.2f}, 3스테이지 통과 {st.mean(x['val'][1] for x in rs):.0%} (최저 {min(x['val'][1] for x in rs):.0%}, 최고 {max(x['val'][1] for x in rs):.0%})")
            cnt = collections.Counter(n for x in rs for n in set(x["bag"])); 
            print("  여러 탐색에 공통으로 등장한 구슬:", ", ".join(f"{n}({c}/8)" for n, c in cnt.most_common(8)))
            js = [jaccard(a["bag"], b["bag"]) for a, b in itertools.combinations(rs, 2)]; print(f"  탐색 간 구슬 겹침(자카드): 평균 {st.mean(js):.2f}")
            fam = [len({S.FAM.get(ORBS[n].payload[0][0], 'misc') for n in x["bag"]}) for x in rs]; print(f"  최적 주머니의 계열 수(평균): {st.mean(fam):.1f}")
            print("  주머니 예:", rs[0]["bag"])
        json.dump({"due": due, "out": out}, open(f"search3_{mode}_{int(k)}_{r}_{sys.argv[4] if len(sys.argv) > 4 else 'r3'}.json", "w", encoding="utf-8"), ensure_ascii=False)
        if len(types) > 1:
            print("\n스테이지 종류별 최적 주머니의 겹침(자카드 평균):")
            for a, b in itertools.combinations(types, 2):
                print(f"  {a} vs {b}: {st.mean(jaccard(x['bag'], y['bag']) for x in out[a] for y in out[b]):.2f}  (같은 종류 안: {st.mean(jaccard(x['bag'], y['bag']) for x, y in itertools.combinations(out[a], 2)):.2f})")

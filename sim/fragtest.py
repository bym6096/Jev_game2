"""Fragment test: 20 'answer' names x 40 pre-written fragments. How much of the answer name's solo value survives when the blank forces a fragment?"""
import sys, json, math, collections, statistics as st, time
from multiprocessing import Pool
sys.path.insert(0, "/home/user/Jev_game2/sim")
import orbsim as S, search3 as Q
meta = json.load(open("/home/user/Jev_game2/sim/frag_meta.json", encoding="utf-8")); ANS = meta["answers"]; FR = meta["frags"]
FRAG = S._load("out_frag.jsonl")
def fuse(n, f): pos, tx, sp = f; return f"{tx}{' ' if sp else ''}{n}" if pos == "pre" else f"{n}{' ' if sp else ''}{tx}"
DUE = [90, 225, 562]; CFG = dict(Q.RULESETS["r4"]); SEEDS = range(0, 150)
def run(bag): return [S.Game(bag, seed=s, due=DUE, pool_names=[], cfg=CFG).run() for s in SEEDS]
def init():
    global ORB, ST, BS
    ORB = {n: S.make_orb(n, cost_model="value", gold_mult=Q.GM) for n in S.ALL_NAMES}; ST = [ORB[n] for n in S.STARTER]; BS = [r["score"] for r in run(ST)]
def job(full):
    n = full
    o = S.make_orb(full, cost_model="value", gold_mult=Q.GM, extra=FRAG) if full in FRAG else ORB[full]
    res = run(ST + [o, o]); sc = [r["score"] for r in res]
    return full, st.mean(a - b for a, b in zip(sc, BS)), dict(role=o.role, verb=o.verbs[0][0], mana=o.mana, life=o.life, pe=round(o.pe, 2), amb=o.amb, hostile=o.hostile)
if __name__ == "__main__":
    t0 = time.time(); names = list(ANS) + [fuse(n, f) for n in ANS for f in FR]
    with Pool(4, initializer=init) as P: out = P.map(job, names, chunksize=8)
    D = {k: (d, m) for k, d, m in out}; rent = sum(DUE)
    json.dump({"due": DUE, "delta": {k: v[0] for k, v in D.items()}, "meta": {k: v[1] for k, v in D.items()}}, open("fragtest.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(names)} orbs in {time.time()-t0:.0f}s | 정산 합계 {rent}")

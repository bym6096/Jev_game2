"""런(여러 스테이지) 난이도 비교 봇 — Jev 호출 없음. balance_bot.py의 단순 봇으로 런을 끝까지(사망·정산 실패·12스테이지 클리어) 돌리고, 도달 스테이지를 설정별로 비교한다.
  python3 -I proto/tests/run_bot.py            # 현재 설정 + 정산 곡선 후보
  python3 -I proto/tests/run_bot.py 60         # 설정당 60런
봇은 이름 구슬을 안 쓰고(시작 구슬 10개뿐, 보상 빈 구슬은 건너뜀) 출구는 무작위로 고른다. 그래서 절대 수치보다 **설정 사이의 차이**와 "어디서 막히는가"를 본다.
사람·모델은 보상 빈 구슬로 주머니를 키우므로 봇보다 멀리 가야 정상이다."""
import os, sys, random, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..")
for p in (P, os.path.join(P, "vendor"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import engine, orbs
from balance_bot import pri

def play_stage(g):
    for _ in range(300):
        if g.phase != "play": return
        for _ in range(10):
            ok = [x for x in g.view()["hand"] if not x["why"] and x["o"]["role"] != "move"]
            if not ok: break
            x = sorted(ok, key=pri)[0]
            tile = (x["hint"][0] if x["hint"] else x["tiles"][0]) if x["need_tile"] and x["tiles"] else None
            if x["need_tile"] and not tile: break
            tg = None
            if x["need_target"] and x["target_ids"]:
                hp = {e["id"]: e["hp"] for e in g.enemies}; tg = min(x["target_ids"], key=lambda i: hp[i])
            if "error" in g.play(x["idx"], tile, tg): break
        # 다 쓴 채집 건물은 철거(칸 한도를 비움)
        for b in list(g.buildings):
            vs = [p[0] for p in b["o"]["payload"]]
            if g.mana >= 1 and "process" not in vs and any(p[0] == "harvest" and p[2] in ("wood", "ore") for p in b["o"]["payload"]):
                kind = {"wood": "tree", "ore": "ore"}[next(p[2] for p in b["o"]["payload"] if p[0] == "harvest")]
                if not any(g.tiles.get(n, {}).get("t") == kind and g.tiles[n]["amt"] > 0 for n in engine.nb((b["q"], b["r"]))): g.demolish(b["id"])
        g.end_turn()

def play_run(cfg, seed, bag=None):
    R = random.Random(seed); g = engine.HexGame(bag or orbs.starter_orbs(), stage_type=R.choice(list(engine.STAGE_TYPES)), seed=seed, cfg=cfg); g.start()
    while True:
        play_stage(g)
        if g.phase == "exit": g.choose_exit(R.choice(g.exits)["i"]); g.start(); continue
        return g

def run(label, cfg, n=40):
    reach = []; why = collections.Counter(); gold_at = collections.defaultdict(list)
    for s in range(n):
        g = play_run(cfg, 5000 + s); r = g.result; reach.append(r["stage"] if not r["clear"] else r["stages"] + 1)
        why["클리어" if r["clear"] else "사망" if r["died"] else "정산 실패"] += 1
        for h in g.history: gold_at[h["stage"]].append(1)
    dist = collections.Counter(reach); stages = (cfg.get("stages") or engine.CFG["stages"])
    line = " ".join(f"{k}:{dist.get(k, 0)}" for k in range(1, stages + 2))
    print(f"{label:28} 도달 평균 {st.mean(reach):4.1f} 중앙 {st.median(reach):4.1f} | {dict(why)} | 막힌 스테이지 분포 {line}")
    return st.mean(reach)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    c = engine.CFG
    print("정산액:", [engine.due_for(k) for k in range(1, c["stages"] + 1)])
    run("현재 설정", {}, n)
    for due, r in ((120, 1.4), (100, 1.5), (120, 1.3), (150, 1.3), (100, 1.4)):
        run(f"정산 {due} × {r}ⁿ", dict(due=due, due_r=r), n)

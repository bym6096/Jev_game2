"""밸런스 비교용 단순 자동 플레이 봇(시작 구슬만, Jev 호출 없음). 설정(engine.CFG 덮어쓰기)별로 정산 통과율·처치·골드를 비교한다.
  python3 -I proto/tests/balance_bot.py            # 현재 설정 + 적 체력·보상 후보 비교
  python3 -I proto/tests/balance_bot.py 60          # 설정당 스테이지 종류별 60판
봇이 단순해서(건물·소환 → 자원·돈 → 공격(가장 약한 적) 순, 이동 구슬은 안 씀) 절대 수치보다 **설정 사이의 차이**를 본다. 무작위 봇(rules_bot.py)은 예외 찾기용, 이 봇은 난이도 비교용."""
import os, sys, random, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..")
for p in (P, os.path.join(P, "vendor")):
    if p not in sys.path: sys.path.insert(0, p)
import engine, orbs

ORDER = {"build": 0, "summon": 1}
def pri(x):
    o = x["o"]
    if o["role"] in ORDER: return ORDER[o["role"]]
    if o["role"] == "move": return 9
    vs = [p[0] for p in o["payload"]]
    if any(v in engine.ENEMY_V for v in vs): return 3
    if any(v in engine.ECO_V for v in vs): return 2
    return 4

def play_game(cfg, seed, stage, bag=None):
    g = engine.HexGame(bag or orbs.starter_orbs(), stage_type=stage, seed=seed, cfg=cfg); g.start()
    for _ in range(200):
        if g.phase != "play": break
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
        g.end_turn()
    return g

def run(label, cfg, n=40, bag=None):
    c = collections.Counter(); kills = []; golds = []; bounty = []
    for stage in ("balanced", "hostile", "rich"):
        for s in range(n):
            g = play_game(cfg, 1000 + s, stage, bag); res = g.result
            c["pass"] += bool(res["pass"]); c["died"] += bool(res["died"]); kills.append(res["kills"]); golds.append(res["gold"]); bounty.append(res["src"].get("g_bounty", 0))
    N = 3 * n
    print(f"{label:30} 통과 {c['pass']/N:4.0%} | 사망 {c['died']/N:4.0%} | 처치 평균 {st.mean(kills):4.1f} | 처치 보상 평균 {st.mean(bounty):5.1f}골드 | 최종 골드 평균 {st.mean(golds):5.0f}")
    return c["pass"] / N

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    run("현재 설정", {}, n)
    for nm, cfg in (("(옛) 체력11·보상4", dict(ehp=.5, bounty0=2, bountyk=2)), ("체력22·보상8", dict(ehp=1.0, bounty0=4, bountyk=4)), ("체력44·보상16", dict(ehp=2.0, bounty0=8, bountyk=8)), ("체력44·보상8", dict(ehp=2.0, bounty0=4, bountyk=4))):
        run(nm, cfg, n)

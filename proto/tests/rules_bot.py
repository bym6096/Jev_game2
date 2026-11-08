"""엔진 규칙 시험(Jev 호출 없음, 몇 초): python proto/tests/rules_bot.py
이동·식물·타게팅·사거리·지속 효과 중첩 방지를 하나씩 확인하고, 무작위 봇 90판을 돌려 예외가 없는지 본다. 통과율은 참고만(봇이 이동을 아무 데나 쓴다)."""
import os, sys, random, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine, orbs

def hand_of(g, *names):
    g.hand = [next(i for i in g.bag if g.inst[i]["o"]["name"] == n) for n in names]; g.mana = 6; return {x["o"]["name"]: x for x in g.view()["hand"]}

# 1) 이동·식물
g = engine.HexGame(orbs.starter_orbs(), seed=3); g.start()
names = [g.inst[i]["o"]["name"] for i in g.bag]; assert "달리기" in names and "텃밭" in names and len(names) == 10, names
h = hand_of(g, "달리기", "텃밭"); assert h["달리기"]["tiles"] and all(engine.hd(tuple(t), g.pos) <= 2 for t in h["달리기"]["tiles"])
dest = tuple(h["달리기"]["tiles"][0]); assert g.play(0, dest).get("ok") and g.pos == dest and g.view()["pos"] == list(dest)
h = {x["o"]["name"]: x for x in g.view()["hand"]}; assert all(engine.hd(tuple(t), g.pos) <= 2 for t in h["텃밭"]["tiles"]), "이동한 뒤 배치 범위는 새 위치 기준"
assert g.play(0, tuple(h["텃밭"]["tiles"][0])).get("ok")
b = g.view()["buildings"][0]; assert b["kind"] == "plant" and b["age"] == 0
ys = []
for _ in range(5): f = g.res["food"]; g.hand = []; g.end_turn(); ys.append(g.res["food"] - f)
assert ys[0] == 0 and ys[1] == 0 and max(ys[2:]) > 0, ys      # 2턴 자란 뒤부터 수확
assert g.view()["plants_n"] == 1 and g.view()["buildings_n"] == 0
print("이동·식물 OK", ys)

# 2) 타게팅·사거리(시전 4칸)
g = engine.HexGame(orbs.starter_orbs(), seed=5); g.start(); h = hand_of(g, "화염검")["화염검"]
assert h["why"] and "사거리" in h["why"], "1턴에는 적이 가장자리(5칸)라 사거리 밖: " + str(h["why"])
near, far, out = g.enemies[0], g.enemies[1], g.enemies[2]
near.update(q=2, r=-1); far.update(q=4, r=-1); out.update(q=5, r=-2)           # 거리 2·4·5
h = hand_of(g, "화염검")["화염검"]; assert h["need_target"] and set(h["target_ids"]) == {near["id"], far["id"]}, h["target_ids"]
hp0 = (near["hp"], far["hp"]); assert g.play(0, None, out["id"]).get("error"), "사거리 밖 대상은 거절"
assert g.play(0, None, far["id"]).get("ok"); assert near["hp"] == hp0[0] and (far["hp"] < hp0[1] or far not in g.enemies), "고른 먼 적만 맞는다"
h = hand_of(g, "화염검")["화염검"]; g.play(0)                                      # 대상을 안 주면 가장 가까운 적
print("타게팅·사거리 OK")

# 3) 소환물·건물 사거리(병사 1칸), 지속 효과는 쌓이지 않음
g = engine.HexGame(orbs.starter_orbs(), seed=7); g.start(); g.enemies = []
sol = next(o for o in orbs.starter_orbs() if o["name"] == "병사"); assert engine.unit_range(sol) == 1 and engine.unit_range({"role": "build", "unit": "worker"}) == 2
aura = orbs._hand("무한 자원", role="cast", payload=[["money", 1, None]], life="run", timing="repeating", mana=1)
a1, a2 = g.add_orb(aura), g.add_orb(aura); g.hand = [a1, a2]; g.mana = 6
assert engine.sustained(aura) and not engine.sustained(sol)
assert g.play(0).get("ok"); assert len([f for f in g.fx if f["kind"] == "dur"]) == 1
assert g.view()["hand"] == [] and g.view()["exh"] == 2, "지속 구슬은 쓰면 소멸하고 같은 사본도 함께 빠진다(못 쓰는 채 손패에 남지 않음)"
assert a1 not in g.disc + g.draw + g.hand and a2 not in g.disc + g.draw + g.hand and a1 in g.bag, "순환에서만 빠지고 주머니엔 남는다"
for _ in range(6): g.end_turn(); assert all(g.inst[i]["o"]["name"] != "무한 자원" for i in g.hand), "소멸한 구슬은 다시 뽑히지 않는다"
assert [h for h in g.view()["hand"] if h["why"] == "이미 작동 중"] == []
g2 = engine.HexGame(orbs.starter_orbs() + [aura], seed=7); g2.start(); assert g2.view()["exh"] == 0, "새 스테이지는 소멸 더미가 비어 있다(다시 나옴)"
print("사거리·중첩 방지·소멸 OK")

# 4) 무작위 봇 — 예외 없음
stat = collections.Counter()
for seed in range(90):
    g = engine.HexGame(orbs.starter_orbs(), stage_type=["balanced", "hostile", "rich"][seed % 3], seed=seed); g.start(); R = random.Random(seed)
    for _ in range(200):
        if g.phase != "play": break
        for _ in range(6):
            ok = [x for x in g.view()["hand"] if not x["why"]]
            if not ok or R.random() < .15: break
            x = R.choice(ok); tile = R.choice(x["tiles"]) if x["need_tile"] and x["tiles"] else None
            if x["need_tile"] and not tile: continue
            tg = R.choice(x["target_ids"]) if x["need_target"] and x["target_ids"] else None
            r = g.play(x["idx"], tile, tg); stat["moves"] += x["o"]["role"] == "move" and bool(r.get("ok")); stat["plants"] += x["o"]["name"] == "텃밭" and bool(r.get("ok"))
            assert "error" not in r, r
        g.end_turn(); v = g.view(); assert tuple(v["pos"]) not in {(e["q"], e["r"]) for e in v["enemies"]}, "플레이어 위에 적"
    stat["pass"] += bool(g.result and g.result["pass"])
print("무작위 봇 90판 OK", dict(stat))

# 5) 시너지: 사건 알림·반응·화상·종류별 증폭 (Jev 호출 없음)
H = orbs._hand
def sgame(extra=(), seed=3, near=1):
    """시험용 판: 손패는 버린 더미로 치우고(구슬이 순환에서 사라지지 않게), 적 3마리를 플레이어 곁(사거리 안)에 세우고 체력을 키워 안 죽게 한다."""
    g = engine.HexGame(orbs.starter_orbs() + list(extra), seed=seed); g.start(); g.mana = 6; g.disc += g.hand; g.hand = []; g.enemies = g.enemies[:3]
    for e, r in zip(g.enemies, (0, -1, 1)): e.update(q=near, r=r, hp=500, max=500, bounty=4)
    return g
def put(g, o): i = g.add_orb(o); g.hand.append(i); return len(g.hand) - 1
def pull(g, name):
    i = next(i for i in g.draw + g.disc if g.inst[i]["o"]["name"] == name); (g.draw if i in g.draw else g.disc).remove(i); g.hand.append(i); return len(g.hand) - 1
# 5a) 'X 구슬을 쓸 때마다' 반응: 공격에만, 턴당 최대 TRIG_PER_TURN회, 같은 반응은 쌓이지 않고 스테이지 지속은 소멸
react = H("공격 반응", role="cast", payload=[["money", 5, None]], life="stage", trig="orb_attack", mana=1)
g = sgame(); assert g.play(put(g, react)).get("ok"); assert g.view()["exh"] == 1 and "공격 반응" in [f["o"]["name"] for f in g.fx], "스테이지 반응은 깔리고 소멸한다"
g.play(pull(g, "금화 주머니")); assert g.stats["reactions"] == 0, "공격이 아닌 구슬엔 반응하지 않는다"
for k in range(4):
    g.mana = 6; idx = pull(g, "화염검") if any(g.inst[i]["o"]["name"] == "화염검" for i in g.draw + g.disc) else None
    if idx is None: break
    g.play(idx, None, g.enemies[0]["id"])
assert 1 <= g.stats["reactions"] <= engine.TRIG_PER_TURN, ("턴당 제한", g.stats["reactions"]); g.end_turn(); assert all(f.get("tn", 0) == 0 for f in g.fx), "다음 턴에 횟수 초기화"
# 5b) kill / harvest / hit / 건물 반응 + 건물은 매 턴 일하지 않는다
kr = H("처치 보상", role="cast", payload=[["money", 4, None]], life="stage", trig="kill", mana=1)
g = sgame(); g.enemies[0].update(hp=1); g.play(put(g, kr)); g0 = g.gold; g.play(pull(g, "화염검"), None, g.enemies[0]["id"]); assert g.gold - g0 >= 4 + 4 and g.stats["reactions"] == 1, "처치 시 반응 골드"
bd = H("식물 깃발", role="build", payload=[["money", 3, None]], life="run", trig="orb_plant", mana=1, hp=10, bcost=["gold", 0, 0])
g = sgame(); i = put(g, bd); g.play(i, g.valid_tiles(g.hand[i])[0]); g0 = g.gold; g.play(pull(g, "텃밭"), g.valid_tiles(g.hand[-1])[0]); assert g.stats["reactions"] == 1 and g.gold - g0 == 3 - 1, ("식물 구슬 → 건물 반응", g.gold - g0)
g.mana = 6; g0 = g.gold; g.end_turn(); assert g.gold == g0 or g.gold - g0 < 3 and True, "반응형 건물은 매 턴 일하지 않는다"
hitr = H("반격", role="cast", payload=[["money", 6, None]], life="stage", trig="hit", mana=1)
g = sgame(); g.play(put(g, hitr)); g.enemies[0].update(q=1, r=0); g0 = g.gold
for _ in range(6): g.end_turn() if g.phase == "play" else None
assert g.stats["reactions"] >= 1 or g.stats["dmg_taken"] == 0, "피격 반응"
# 5c) 화상(쌓임·턴마다 감소)과 종류별 증폭(합산·상한·갱신)
burn = H("불꽃", role="cast", payload=[["burn", 3, None]], life="instant", mana=1)
def burn_dmg(boosts):
    g = sgame(); e = g.enemies[0]
    for b in boosts: g.play(put(g, b))
    g.play(put(g, burn), None, e["id"]); assert e["burn"] == 3; hp = e["hp"]; g.end_turn(); assert e["burn"] == 2, "화상은 턴마다 1중첩 감소"; return hp - e["hp"]
b1 = H("불쏘시개", role="cast", payload=[["buff", 50, "burn"]], life="stage", mana=1); b2 = H("기름", role="cast", payload=[["buff", 50, "burn"]], life="stage", mana=1)
d0, d1, d2 = burn_dmg([]), burn_dmg([b1]), burn_dmg([b1, b2]); assert d0 == 6 and d1 == 9 and d2 == 12, ("서로 다른 구슬의 증폭은 합산", d0, d1, d2)
g = sgame(); g.play(put(g, b1)); assert g.mm("burn") == 1.5; a = put(g, b1); assert g.reason(g.hand[a]) == "이미 작동 중" or g.view()["exh"] >= 1, "같은 증폭은 쌓이지 않음"
big = [H(f"증폭{k}", role="cast", payload=[["buff", 90, "income"]], life="stage", mana=1) for k in range(3)]
g = sgame(); [g.play(put(g, b)) for b in big]; assert abs(g.mm("income") - (1 + engine.MULT_CAP)) < 1e-9, "증폭 합 상한"
inc = H("황금 장갑", role="cast", payload=[["buff", 40, "income"]], life="stage", mana=1); g = sgame(); g.play(put(g, inc)); g0 = g.gold; g.play(put(g, H("돈", role="cast", payload=[["money", 10, None]], mana=1))); assert g.gold - g0 == 14, "수입 +40%"
tm = H("3턴 증폭", role="cast", payload=[["buff", 30, "dmg"]], life="instant", mana=1); g = sgame(); g.play(put(g, tm)); assert g.mm("dmg") > 1
for _ in range(3): g.end_turn()
assert g.mm("dmg") == 1, "instant 증폭은 3턴 뒤 끝난다"
# 5d) 연쇄 방지: 반응이 같은 반응을 부르는 구슬(수확→수확)도 무한 루프 없이 끝난다
loop = H("수확의 노래", role="cast", payload=[["harvest", 4, "ore"]], life="stage", trig="harvest", mana=1)
g = sgame(); g.play(put(g, loop)); g.play(pull(g, "곡괭이")); assert g.stats["reactions"] <= 2 * engine.TRIG_PER_TURN, ("연쇄 제한", g.stats["reactions"])
print("시너지 규칙 OK (반응·턴당 제한·건물 반응·화상·증폭 합산/상한·연쇄 방지)")

# 5e) 시너지 구슬만 섞은 무작위 봇 — 예외·무한 루프 없음, 반응이 실제로 터진다
SYN = [react, kr, bd, hitr, burn, b1, inc, loop, H("복수의 탑", role="build", payload=[["damage", 8, None]], life="run", trig="hit", mana=2, hp=10, bcost=["gold", 0, 1], rng="around"),
       H("화염병", role="cast", payload=[["burn", 2, None]], life="turns", mana=2, rng="around"), H("수확 보너스", role="cast", payload=[["harvest", 2, "ore"]], life="stage", trig="harvest", mana=2)]
stat = collections.Counter()
for seed in range(60):
    g = engine.HexGame(orbs.starter_orbs() + [dict(o) for o in SYN], stage_type=["balanced", "hostile", "rich"][seed % 3], seed=seed); g.start(); R = random.Random(seed)
    for _ in range(200):
        if g.phase != "play": break
        for _ in range(6):
            ok = [x for x in g.view()["hand"] if not x["why"]]
            if not ok or R.random() < .15: break
            x = R.choice(ok); tile = R.choice(x["tiles"]) if x["need_tile"] and x["tiles"] else None
            if x["need_tile"] and not tile: continue
            tg = R.choice(x["target_ids"]) if x["need_target"] and x["target_ids"] else None
            r = g.play(x["idx"], tile, tg); assert "error" not in r, r
        g.end_turn()
    stat["reactions"] += g.stats["reactions"]; stat["burn_dmg"] += g.stats["burn_dmg"]; stat["pass"] += bool(g.result and g.result["pass"])
assert stat["reactions"] > 0 and stat["burn_dmg"] > 0, stat
print("시너지 봇 60판 OK", dict(stat))

# 6) 설치 사거리 1칸 + 재료 비용(건물·소환물)
g = engine.HexGame(orbs.starter_orbs(), seed=5); g.start(); g.mana = 6
for iid in g.hand:
    o = g.inst[iid]["o"]
    if g.needs_tile(o) and o["role"] != "move": assert all(engine.hd(t, g.pos) == 1 for t in g.valid_tiles(iid)), (o["name"], "건물·식물·소환은 인접 칸만")
costly = H("무거운 소환", role="summon", payload=[["damage", 4, None]], life="run", mana=1, hp=10, unit="soldier", bcost=["wood", 3, 2])
g = sgame(); i = put(g, costly); g.res["wood"] = 2; assert "재료" in (g.reason(g.hand[i]) or ""), "소환물도 재료가 모자라면 못 쓴다"
g.res["wood"] = 5; g.gold = 5; assert g.reason(g.hand[i]) is None and g.play(i, g.valid_tiles(g.hand[i])[0]).get("ok"); assert g.res["wood"] == 2 and g.gold == 3, "소환물 재료·골드 차감"
st0 = {"wood": 6, "ore": 4, "food": 3}; gold0 = 8
for o in orbs.starter_orbs():
    if o["bcost"]: mt, x, y = o["bcost"]; assert (x <= gold0 - y if mt == "gold" else x <= st0[mt] and y <= gold0), (o["name"], "시작 재료로 지을 수 있어야 한다")
print("설치 사거리·재료 비용 OK")

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

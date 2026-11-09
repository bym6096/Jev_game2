"""사전단어 변환 12종 시험 — Jev 호출 없음.   python3 -I proto/tests/mods_check.py
①풀: 변환 말 144 + 힌트 말 54, 서로 안 겹침, 옛 맛내기 말은 없음 ②변환마다 표대로 구슬이 바뀜(수치·범위·지속·마나·속성) ③엔진 지원: 메아리 사본·지연(시전·지속·건물·소환물)
④쓴 이름만 읽고 구슬 이름은 전체 이름 ⑤변환 말이 붙은 판을 무작위 봇이 끝까지 돌려도 예외 없음."""
import os, sys, copy, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..")
for p in (P, os.path.join(P, "vendor")):
    if p not in sys.path: sys.path.insert(0, p)
import engine, orbs, value, forge
H = orbs._hand
def mod(d, k): return orbs.apply_mod(copy.deepcopy(d), k, "시험")

# 1) 풀
hw = {w for _, _, w, _ in orbs.HINT_WORDS}; mw = {w for _, _, w, _ in orbs.MOD_WORDS}
assert len(orbs.MOD_WORDS) == 144 and len(orbs.HINT_WORDS) == 54 and not (hw & mw), hw & mw
assert set(orbs.MOD_RULES) == {"reverse", "bigger", "smaller", "faster", "slower", "stronger", "weaker", "risky", "random", "once", "lasting", "echo"}
assert collections.Counter(k for k, *_ in orbs.MOD_WORDS) == collections.Counter({k: 12 for k in orbs.MOD_RULES})
assert not hasattr(orbs, "FRAGS"), "옛 맛내기 말 풀은 폐기됨"
for k, pos, w, sp in orbs.MOD_WORDS + [(k, pos, w, sp) for k, pos, w, sp in orbs.HINT_WORDS]:
    b = {"tier": "평범한", "cap": 7, "frag": {"pos": pos, "t": w, "sp": sp, "hint": None, "mod": None}}; assert orbs.max_typed(b) >= 3, w
R = random.Random(2); c = collections.Counter(); seen_mods = set()
for _ in range(6000):
    f = orbs.new_blank("낡은", R)["frag"]; assert f is not None
    c["hint" if f["hint"] else "mod"] += 1; assert bool(f["hint"]) != bool(f["mod"]), f; seen_mods.add(f["mod"])
assert abs(c["hint"] / 6000 - orbs.HINT_SHARE) < .03 and len(seen_mods - {None}) == 12, (c, seen_mods)
print("풀 OK", dict(c))

# 2) 변환별 결과
cast = H("검", role="cast", payload=[["damage", 20, None]], rng="line", life="instant", mana=3, pe=1.5)
r = mod(cast, "reverse"); assert r["payload"][0][0] == "heal" and r["payload"][0][1] == 18 and r["mana"] == value.mana_for(r), (r["payload"], r["mana"])     # 반전 뒤 가격은 다시 매긴다(2026-11-09)
r = mod(H("약화", payload=[["debuff", 1, None]], pe=1.0), "reverse"); assert r["payload"][0][0] == "buff" and r["payload"][0][2] in engine.BOOST_KINDS and 10 <= r["payload"][0][1] <= 40
r = mod(H("돈", payload=[["money", 4, None], ["harvest", 5, "ore"]]), "reverse"); assert [p[0] for p in r["payload"]] == ["steal", "grow"] and r["payload"][1][2] == "ore"
r = mod(H("방어", payload=[["guard", 8, None]]), "reverse"); assert r["payload"][0][0] == "debuff"
r = mod(H("흡수", payload=[["energy", 2, None]]), "reverse"); assert r["payload"][0][0] == "energy", "표에 없는 동사는 그대로"
b = mod(cast, "bigger"); assert b["rng"] == "around" and b["payload"][0][1] == 18 and b["mana"] == 4
assert mod(H("광역", payload=[["damage", 10, None]], rng="wide", mana=2), "bigger")["rng"] == "wide"
assert mod(H("탑", role="build", payload=[["money", 3, None]], hp=10, bcost=["gold", 1, 1]), "bigger")["hp"] == 13
s = mod(cast, "smaller"); assert s["rng"] == "single" and s["payload"][0][1] == 17 and s["mana"] == 2
assert mod(H("작", payload=[["damage", 10, None]], rng="single", mana=1), "smaller")["mana"] == 1, "마나 최소 1"
f = mod(H("지연", payload=[["damage", 10, None]], timing="delayed", delay=3, mana=3), "faster"); assert f["timing"] == "now" and f["mana"] == 2
assert mod(H("그냥", payload=[["damage", 10, None]], mana=3), "faster")["mana"] == 2
sl = mod(cast, "slower"); assert sl["timing"] == "delayed" and sl["delay"] == 2 and sl["payload"][0][1] == 28 and sl["mana"] == 3 and "2턴 뒤" in sl["text"]
assert mod(H("반응", payload=[["money", 3, None]], trig="orb_attack", life="stage"), "slower")["timing"] == "now", "반응형 시전은 그대로"
sb = mod(H("탑", role="build", payload=[["money", 3, None]], hp=10, bcost=["gold", 1, 1], life="run"), "slower"); assert sb["timing"] == "delayed" and sb["delay"] == 2 and "쉬고" in sb["text"]
assert mod(cast, "stronger")["payload"][0][1] == 28 and mod(cast, "stronger")["mana"] == 4
assert mod(cast, "weaker")["payload"][0][1] == 14 and mod(cast, "weaker")["mana"] == 2
k = mod(cast, "risky"); assert k["payload"][0][1] == 30 and k["mod"] == "risky"
k = mod(cast, "random"); assert k["mod"] == "random" and k["mana"] == 2
k = mod(cast, "once"); assert k["fate"] == "used_up" and k["payload"][0][1] == 30 and "1회용" in k["text"]
k = mod(cast, "lasting"); assert k["life"] == "turns" and k["mana"] == 4 and k["payload"][0][1] == round(20 * (1.6 / 3) * .8), k["payload"]
k2 = mod(k, "lasting"); assert k2["life"] == "stage" and k2["rng"] == "line"
k3 = mod(H("긴", payload=[["damage", 6, None]], life="stage", rng="single"), "lasting"); assert k3["life"] == "run" and k3["rng"] == "around", "긴 지속의 단일 공격은 무리로"
assert mod(H("영원", payload=[["money", 1, None]], life="run", mana=2), "lasting")["life"] == "run" and mod(H("영원", payload=[["money", 1, None]], life="run", mana=2), "lasting")["mana"] == 2, "더 오래갈 수 없으면 그대로"
assert mod(H("탑", role="build", payload=[["money", 3, None]], hp=10, bcost=["gold", 1, 1], life="run"), "lasting")["hp"] == 15
e = mod(cast, "echo"); assert e["echo"] and e["mana"] == 4 and "메아리" in e["text"] and "'시험': 메아리" in e["text"]
assert orbs.apply_mod(orbs.scribble("낙서"), "stronger")["mana"] == 1 and "fragmod" not in orbs.scribble("낙서")
print("변환 12종 OK")

# 3) 엔진 지원
def game(extra, seed=3):
    g = engine.HexGame(orbs.starter_orbs() + extra, seed=seed); g.start(); g.mana = 8; g.disc += g.hand; g.hand = []; g.enemies = g.enemies[:3]
    for en, rr in zip(g.enemies, (0, -1, 1)): en.update(q=1, r=rr, hp=900, max=900)
    return g
def put(g, o): i = g.add_orb(o); g.hand.append(i); return len(g.hand) - 1
# 메아리: 사본이 손패에 생기고(마나 −1), 쓰면 사라지고, 쓰지 않아도 턴이 끝나면 사라진다. 원본은 주머니·순환에 그대로.
echo = mod(H("메아리 돈", payload=[["money", 5, None]], mana=3), "echo")
g = game([]); i = put(g, echo); g0 = g.gold; assert g.play(i).get("ok"); copies = [x for x in g.hand if g.inst[x]["o"].get("copy")]
assert len(copies) == 1 and g.inst[copies[0]]["o"]["mana"] == 3 and g.gold - g0 == 5, (len(copies), g.inst[copies[0]]["o"]["mana"] if copies else None)       # 원본 마나 4(=3+1) → 사본 3
m0 = g.mana; g.play(g.hand.index(copies[0])); assert g.gold - g0 == 5 + round(5 * engine.CFG["fam_decay"]) and copies[0] not in g.hand + g.disc + g.draw + g.bag and not [x for x in g.hand if g.inst[x]["o"].get("copy")], "사본은 쓰면 사라진다(사본의 사본은 없음)"
g = game([]); i = put(g, echo); g.play(i); g.end_turn(); assert not any(g.inst[x]["o"].get("copy") for x in g.hand + g.disc + g.draw), "안 쓴 사본은 턴이 끝나면 사라진다"
assert any(g.inst[x]["o"]["name"] == "메아리 돈" for x in g.disc + g.draw + g.hand), "원본은 순환에 남는다"
# 지연: 시전은 2턴 뒤 발동, 지속 시전은 2턴 뒤부터 지속, 소환물·건물은 처음 2턴 쉼
dl = mod(H("느린 돈", payload=[["money", 5, None]], mana=1), "slower")
g = game([]); i = put(g, dl); g0 = g.gold; g.play(i); assert g.gold == g0 and any(f["kind"] == "delay" for f in g.fx); [g.end_turn() for _ in range(2)]; assert g.gold == g0, "2턴 동안은 발동 전"; g.end_turn(); assert g.gold - g0 >= 7, "2턴 쉰 뒤(세 번째 턴 끝) 발동(수치 ×1.4)"
ds = mod(H("느린 지속", payload=[["money", 2, None]], life="stage", mana=1), "slower")
g = game([]); i = put(g, ds); g0 = g.gold; g.play(i); assert engine.sustained(ds) and g.view()["exh"] == 1, "지연된 지속 시전도 스테이지 동안 소멸"
[g.end_turn() for _ in range(2)]; assert g.gold == g0; g.end_turn(); mid = g.gold; assert mid - g0 >= 3 and any(f["kind"] == "dur" for f in g.fx), "기다린 뒤 지속 효과로"; g.end_turn(); assert g.gold > mid
dsum = mod(H("느린 병사", role="summon", payload=[["money", 3, None]], mana=1, hp=10, unit="soldier", life="run"), "slower")
g = game([]); i = put(g, dsum); g.play(i, g.valid_tiles(g.hand[i])[0]); g0 = g.gold; g.end_turn(); g.end_turn(); assert g.gold == g0, "소환물은 처음 2턴 작동 안 함"; g.end_turn(); assert g.gold > g0
# 한 방·위험·무작위·지속은 기존 엔진 규칙과 연결
g = game([]); on = put(g, mod(H("일회", payload=[["money", 5, None]], mana=1), "once")); iid = g.hand[on]; g.play(on); assert iid not in g.bag + g.disc + g.draw, "한 방은 쓰면 주머니에서 사라진다"
print("엔진 지원 OK")

# 4) 읽는 이름과 이름표
seen = []
def fake(name, lang="ko"): seen.append(name); return H(name, payload=[["damage", 20, None]], mana=3, pe=1.5)
o = orbs.orb_with_fragment("거꾸로 검", "검", mod="reverse", word="거꾸로", build=fake); assert seen[-1] == "검" and o["name"] == "거꾸로 검" and o["payload"][0][0] == "heal" and "'거꾸로': 반전" in o["text"]
blank = {"tier": "낡은", "cap": 5, "frag": {"pos": "suf", "t": "메가", "sp": True, "hint": None, "mod": "bigger"}}
o = orbs.orb_from_blank(blank, "검", build=fake); assert seen[-1] == "검" and o["name"] == "검 메가" and o["rng"] == "line" or o["rng"] == "around", o["rng"]
assert orbs.frag_info(blank)["kind"] == "mod" and orbs.frag_info(blank)["label"] == "확대" and orbs.frag_info({"frag": None}) is None
assert orbs.frag_info({"frag": {"pos": "pre", "t": "불타는", "sp": True, "hint": "burn", "mod": None}})["kind"] == "hint"
assert orbs.frag_info({"frag": {"pos": "pre", "t": "녹슨", "sp": True}}) is None, "옛 상태(맛내기 말)는 효과 없음으로 안전하게"
o = orbs.orb_from_blank({"tier": "평범한", "cap": 7, "frag": {"pos": "pre", "t": "녹슨", "sp": True}}, "검", build=fake); assert seen[-1] == "녹슨 검" and "fragmod" not in o, "옛 상태: 전체 이름을 읽고 변환 없음"
print("읽는 이름 OK")

# 5) 변환·힌트 구슬만 든 무작위 봇 — 예외 없음
R = random.Random(9); pool = []
base = [H("검", role="cast", payload=[["damage", 20, None]], mana=3, pe=1.5), H("돈", payload=[["money", 4, None]], mana=2), H("방패", payload=[["guard", 8, None]], life="turns", mana=2),
        H("광산", role="build", payload=[["harvest", 6, "ore"]], life="run", mana=3, hp=15, bcost=["ore", 1, 1]), H("병사", role="summon", payload=[["damage", 5, None]], life="run", mana=2, hp=12, unit="soldier"),
        H("불꽃", payload=[["burn", 3, None]], mana=2), H("강화", payload=[["buff", 20, "income"]], life="stage", mana=2)]
for k in orbs.MOD_RULES:
    for bo in base: pool.append(orbs.apply_mod(copy.deepcopy(bo), k, "시험"))
stat = collections.Counter()
for seed in range(40):
    g = engine.HexGame(orbs.starter_orbs() + [copy.deepcopy(o) for o in R.sample(pool, 30)], stage_type=["balanced", "hostile", "rich"][seed % 3], seed=seed); g.start(); RR = random.Random(seed)
    for _ in range(200):
        if g.phase != "play": break
        for _ in range(8):
            ok = [x for x in g.view()["hand"] if not x["why"]]
            if not ok or RR.random() < .1: break
            x = RR.choice(ok); tile = RR.choice(x["tiles"]) if x["need_tile"] and x["tiles"] else None
            if x["need_tile"] and not tile: continue
            tg = RR.choice(x["target_ids"]) if x["need_target"] and x["target_ids"] else None
            rs = g.play(x["idx"], tile, tg); assert "error" not in rs, rs
        g.end_turn()
    stat["pass"] += bool(g.result and g.result["pass"]); stat["echo"] += g.stats["plays"]
print("변환 봇 40판 OK", dict(stat))
print("변환 시험 통과")

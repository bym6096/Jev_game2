"""특성 힌트(빈 구슬 부스터) 시험 — Jev 호출 없음.   python3 -I proto/tests/hint_check.py
지키는 것: ①힌트 말이 이름 규칙(한글만, 8자 한도 안에서 쓸 자리가 남음)을 통과 ②힌트는 무작위로 붙고 없는 구슬도 있다 ③특성 판정(동사/역할, 애매하면 불일치) ④일치하면 효과 ×1.2 일괄·마나/비용 불변,
불일치·힌트 없음은 그대로 ⑤힌트가 붙으면 Jev는 쓴 이름만 읽고 구슬 이름은 새긴 전체 이름 ⑥옛 상태(힌트 키 없는 빈 구슬)도 깨지지 않음."""
import os, sys, random, copy, collections
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..")
for p in (P, os.path.join(P, "vendor")):
    if p not in sys.path: sys.path.insert(0, p)
import orbs, forge
H = orbs._hand

# 1) 힌트 말: 계열마다 6개, 한글만, 쓸 자리 남음, 합쳐도 이름 규칙 통과
assert len(orbs.HINT_WORDS) == 54 and {k for k, *_ in orbs.HINT_WORDS} == set(orbs.TRAITS), "9계열 × 6개"
assert all(sum(1 for k, *_ in orbs.HINT_WORDS if k == tr) == 6 for tr in orbs.TRAITS)
assert len({w for _, _, w, _ in orbs.HINT_WORDS}) == 54, "중복 없음"
for k, pos, w, sp in orbs.HINT_WORDS:
    assert 2 <= len(w) <= 4 and all("가" <= c <= "힣" for c in w), w
    b = {"tier": "평범한", "cap": 7, "frag": {"pos": pos, "t": w, "sp": sp, "hint": k}}; assert orbs.max_typed(b) >= 4, w
    c, err = forge.check_name(orbs.fuse(b, "감자" * 2)[: 8 + 2], "ko"); assert not err or "글자" in err or "길이" in err or "8" in err, (w, err)      # 붙인 이름이 규칙 오류(문자 종류)를 내지 않음
print("힌트 말 OK")

# 2) 분포: 사전단어 중 HINT_SHARE가 힌트, 힌트 없는 구슬도 많다
R = random.Random(1); c = collections.Counter()
for _ in range(4000):
    b = orbs.new_blank("평범한", R); f = b["frag"]; c["none" if not f else "hint" if f["hint"] else "flavor"] += 1
assert c["none"] > 1500 and abs(c["hint"] / (c["hint"] + c["flavor"]) - orbs.HINT_SHARE) < .05, c
assert all(orbs.new_blank("낡은", R)["frag"] is not None for _ in range(50)), "낡은 빈 구슬은 항상 사전단어"
assert orbs.hint_info({"frag": None}) is None and orbs.hint_info({"frag": {"pos": "pre", "t": "녹슨", "sp": True}}) is None, "옛 상태/힌트 없음도 안전"
print("분포 OK", dict(c))

# 3) 판정
fire = H("불꽃", payload=[["burn", 3, None]]); assert orbs.trait_ok(fire, "burn") and not orbs.trait_ok(fire, "strike")
assert orbs.trait_ok(H("검", payload=[["damage", 10, None]]), "strike") and orbs.trait_ok(H("군단", role="summon", payload=[["damage", 4, None]]), "summon")
assert orbs.trait_ok(H("탑", role="build", payload=[["money", 3, None]]), "build") and orbs.trait_ok(H("탑", role="build", payload=[["money", 3, None]]), "income"), "동사와 역할은 각각 특성"
assert not orbs.trait_ok(H("적대", role="summon", payload=[["damage", 4, None]], hostile=True), "summon"), "적대 소환은 소환 특성이 아님"
assert not orbs.trait_ok(dict(H("애매", payload=[["burn", 3, None]]), amb=True), "burn"), "애매한 이름은 불일치"
assert not orbs.trait_ok(orbs.scribble("낙서"), "burn")
print("판정 OK")

# 4) 부스터: 일치하면 ×1.2 일괄(마나·비용 그대로), 불일치는 그대로
d = H("불꽃", payload=[["burn", 5, None], ["damage", 10, None]], mana=3, bcost=None); m0 = copy.deepcopy(d)
orbs.apply_hint(d, "burn"); assert [p[1] for p in d["payload"]] == [6, 12] and d["mana"] == 3 and d["hint"]["ok"] and "일치" in d["text"], d
d2 = copy.deepcopy(m0); orbs.apply_hint(d2, "grow"); assert d2["payload"] == m0["payload"] and not d2["hint"]["ok"] and "불일치" in d2["text"]
big = H("큰 불", payload=[["damage", 29, None]]); orbs.apply_hint(big, "strike"); assert big["payload"][0][1] == 35
mv = H("달리기", role="move", payload=[["move", 0, None]]); orbs.apply_hint(mv, "strike"); assert mv["payload"][0][1] == 0
print("부스터 OK")

# 5) 읽는 이름: 힌트가 붙으면 쓴 이름만, 아니면 전체. 구슬 이름은 항상 새긴 전체 이름
seen = []
def fake(name, lang="ko"): seen.append(name); return H(name, payload=[["burn", 4, None]], mana=2)
hb = {"tier": "평범한", "cap": 7, "frag": {"pos": "pre", "t": "불타는", "sp": True, "hint": "burn"}}
o = orbs.orb_from_blank(hb, "감자", build=fake); assert seen[-1] == "감자" and o["name"] == "불타는 감자" and o["hint"]["ok"] and o["payload"][0][1] == 5
fb = {"tier": "평범한", "cap": 7, "frag": {"pos": "suf", "t": "그림자", "sp": True, "hint": None}}
o = orbs.orb_from_blank(fb, "감자", build=fake); assert seen[-1] == "감자 그림자" and o["name"] == "감자 그림자" and "hint" not in o and o["payload"][0][1] == 4
o = orbs.orb_from_blank({"tier": "평범한", "cap": 7, "frag": None}, "감자", build=fake); assert seen[-1] == "감자" and "hint" not in o
sb = {"tier": "깨끗한", "cap": 9, "frag": {"pos": "pre", "t": "서리", "sp": True, "hint": "control"}}
o = orbs.orb_from_blank(sb, "감자", build=lambda n, l="ko": orbs.scribble(n)); assert o["name"] == "서리 감자" and "hint" not in o, "낙서는 힌트 판정 안 함"
print("읽는 이름 OK")
print("힌트 시험 통과")

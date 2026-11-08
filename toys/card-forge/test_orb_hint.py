"""card-forge 의 빈 구슬 힌트 시험 — Jev 호출 없음.   python3 toys/card-forge/test_orb_hint.py
①서버의 힌트 요청 검증(parse_hint) ②forge_orb 가 힌트가 붙으면 쓴 이름만 읽고 구슬 이름은 전체 이름으로 돌려줌 ③카드 JSON 에 hint·place·소환물 비용이 실림
④조립된 index.html 에 힌트 표(__HINTS__)가 들어 있고 proto 의 HINT_WORDS 와 같다."""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import forge_orb
orbs = forge_orb.orbs

# 1) 요청 검증
assert forge_orb.parse_hint({}, "감자", "ko") == (None, None, None) and forge_orb.parse_hint({"hint": ""}, "감자", "ko") == (None, None, None)
assert forge_orb.parse_hint({"hint": "burn", "typed": "감자"}, "불타는 감자", "ko") == ("감자", "burn", None)
assert forge_orb.parse_hint({"hint": "zzz", "typed": "감자"}, "불타는 감자", "ko")[2], "모르는 특성은 거절"
assert forge_orb.parse_hint({"hint": ["burn"], "typed": "감자"}, "불타는 감자", "ko")[2], "형식이 틀리면 거절"
assert forge_orb.parse_hint({"hint": "burn", "typed": "사과"}, "불타는 감자", "ko")[2], "쓴 이름이 전체 이름 안에 없으면 거절"
assert forge_orb.parse_hint({"hint": "burn"}, "불타는 감자", "ko")[2] and forge_orb.parse_hint({"hint": "burn", "typed": "x1"}, "불타는 x1", "ko")[2], "쓴 이름이 없거나 이름 규칙 위반이면 거절"
# 변환 말 요청
assert forge_orb.parse_frag({"mod": "reverse", "typed": "검", "word": "거꾸로"}, "거꾸로 검", "ko") == ("검", None, "reverse", "거꾸로", None)
assert forge_orb.parse_frag({"mod": "zzz", "typed": "검"}, "거꾸로 검", "ko")[4], "모르는 변환은 거절"
assert forge_orb.parse_frag({"mod": "reverse", "hint": "burn", "typed": "검"}, "거꾸로 검", "ko")[4], "힌트와 변환은 함께 못 씀"
assert forge_orb.parse_frag({"mod": "reverse", "typed": "사과"}, "거꾸로 검", "ko")[4], "쓴 이름이 전체 이름 안에 없으면 거절"
assert forge_orb.parse_frag({"mod": "reverse", "typed": "검", "word": "엉뚱"}, "거꾸로 검", "ko")[3] is None, "전체 이름에 없는 표시용 말은 버림"
print("요청 검증 OK")

# 2) 읽는 이름과 카드 JSON (Jev 대신 가짜 생성기)
seen = []
def fake(name, lang="ko"): seen.append(name); return orbs._hand(name, role="summon", payload=[["damage", 5, None]], mana=2, hp=12, bcost=["wood", 2, 1], unit="soldier", life="run")
real = orbs.orb_from_jev; orbs.orb_from_jev = fake
try:
    c = forge_orb.forge_orb("용병 궁수대", "ko", "궁수대", "summon")
    assert seen[-1] == "궁수대" and c["name"] == "용병 궁수대" and c["hint"]["ok"] and c["hint"]["trait"] == "summon", (seen, c.get("hint"))
    assert c["orb"]["payload"][0][1] == 6 and c["orb"]["place"] == 1 and "나무 2" in c["orb"]["cost"], c["orb"]        # ×1.2, 인접 1칸, 소환물 비용
    c = forge_orb.forge_orb("불타는 궁수대", "ko", "궁수대", "burn"); assert not c["hint"]["ok"] and c["orb"]["payload"][0][1] == 5, "불일치는 그대로"
    c = forge_orb.forge_orb("궁수대", "ko"); assert seen[-1] == "궁수대" and c["hint"] is None and c["mod"] is None, "사전단어 없으면 전체 이름을 읽음"
    c = forge_orb.forge_orb("메가 궁수대", "ko", "궁수대", None, "echo", "메가"); assert seen[-1] == "궁수대" and c["mod"] == {"key": "echo", "name": "메아리", "word": "메가"} and c["orb"]["echo"] and "메아리" in c["orb"]["text"], c["mod"]
    c = forge_orb.forge_orb("거꾸로 궁수대", "ko", "궁수대", None, "reverse", "거꾸로"); assert c["orb"]["payload"][0][0] == "heal" and c["hint"] is None, "변환: 피해→회복"
finally: orbs.orb_from_jev = real
print("forge_orb 힌트 OK")

# 3) 조립 결과
html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
assert "__HINTS__" not in html and "const HINTS = {" in html
tbl = json.loads(re.search(r"const HINTS = (\{.*?\});", html, re.S).group(1))
assert [(w["k"], w["pos"], w["t"], w["sp"]) for w in tbl["mods"]] == list(orbs.MOD_WORDS) and len(tbl["mods"]) == 144, "변환 말 표가 다름"
assert [(w["k"], w["pos"], w["t"], w["sp"]) for w in tbl["words"]] == list(orbs.HINT_WORDS) and tbl["share"] == orbs.HINT_SHARE and tbl["mult"] == orbs.HINT_MULT, "index.html 의 힌트 표가 엔진과 다름 — python assemble.py 를 다시 돌리세요"
print("조립 OK")
print("card-forge 힌트 시험 통과")

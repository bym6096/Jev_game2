"""구슬 엔진 어댑터: 게임 프로토타입(proto/)과 **같은 구슬 생성 엔진**(orbengine/, sync_orbengine.py가 proto/에서 복사)으로 이름을 읽고,
결과를 이 장난감 화면이 이해하는 카드 JSON으로 바꾼다. 화면은 `orb` 필드가 있으면 구슬 상세(역할·효과 문구·사거리 …)를 보여 준다.
옛 카드 엔진(forge.py: 속성 98·효과 64·공격/방어)은 그대로 두고 `engine: "old"` 로 부를 수 있다."""
import os, sys, colorsys
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = os.path.join(HERE, "orbengine")
if ENG not in sys.path: sys.path.insert(0, ENG)
import orbs, engine                       # orbengine/ (proto의 복사본). orbs.py가 이 폴더의 forge.py(call_jev)를 쓴다

ROLE_KO = {"cast": "시전", "build": "건물", "summon": "소환", "move": "이동", "plant": "식물"}
VERB_KO = {"damage": "피해", "drain": "흡수", "guard": "방어", "heal": "회복", "money": "골드", "steal": "탈취", "harvest": "채집", "grow": "재배", "process": "가공", "buff": "증폭", "burn": "화상", "debuff": "약화",
           "control": "행동 불가", "draw": "더 뽑기", "recycle": "되돌림", "trash": "폐기", "peek": "엿보기", "tempo": "마나", "energy": "마나", "create": "생성", "amplify": "증폭", "remove": "제거", "transform": "변환", "move": "이동"}
# 구슬 색: proto/app.js 의 orbColor 와 같은 규칙(효과 종류 → 기본색, 이름으로 색조·채도·밝기를 조금 변주)
VERB_COLOR = {"damage": "#d8503f", "drain": "#b8325a", "guard": "#4b86dc", "heal": "#4cbf86", "money": "#e0b03a", "steal": "#c99a2e", "process": "#d19a3e", "grow": "#7cbf4f", "buff": "#e5863a", "burn": "#ef6a2b", "debuff": "#8f6bd8",
              "control": "#6c5fd0", "draw": "#37b6c8", "recycle": "#37b6c8", "trash": "#6e8796", "peek": "#58a8d8", "tempo": "#3aa0e8", "energy": "#3aa0e8", "create": "#d36ec0", "amplify": "#e060a0",
              "remove": "#7a8a92", "transform": "#c070d0", "move": "#6db7ea"}
MAT_COLOR = {"wood": "#5fa84f", "ore": "#8a97a8", "food": "#9ab84a", "gold": "#e0b03a"}
FAMILY = {"cast": 5, "build": 4, "summon": 6, "move": 3, "plant": 1}     # 화면의 안쪽 무늬 번호(0~6): 구슬 종류마다 하나

def _hash(s):
    h = 2166136261
    for ch in s: h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h
def orb_color(o):
    if o.get("scribble"): return "#777777"
    p0 = (o.get("payload") or [[None, 0, None]])[0]; verb, mat = p0[0], p0[2]
    base = (MAT_COLOR.get(mat) if verb in ("harvest", "grow") else VERB_COLOR.get(verb)) or VERB_COLOR.get(verb) or "#8a99a8"
    r, g, b = (int(base[i:i + 2], 16) / 255 for i in (1, 3, 5)); h, l, s = colorsys.rgb_to_hls(r, g, b); n = _hash(o["name"])
    h = ((h * 360 + (n % 25) - 12) % 360) / 360; s = max(.35, s - ((n >> 5) % 8) / 100); l = min(.72, max(.2, l + (((n >> 9) % 9) - 4) / 100))
    r, g, b = colorsys.hls_to_rgb(h, l, s); return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))

def kind_of(o): return "plant" if engine.is_plant(o) else o["role"]

def to_card(o, name, lang):
    """구슬 엔진이 만든 구슬(dict) → 화면용 카드 JSON."""
    if o.get("scribble"): return {"name": name, "lang": lang, "status": "scribble", "reason": "구슬이 이름이 아니라 명령을 읽었다", "engine": "orb"}
    kd = kind_of(o); verbs = [p for p in o["payload"] if p[0] != "move"] or o["payload"]
    effects = [{"name": VERB_KO.get(v, v), "desc": orbs.vtext(v, m, mt, o), "value": min(99, int(m))} for v, m, mt in verbs]
    cost = ""
    if o["role"] == "build" and o.get("bcost"): mt, x, y = o["bcost"]; cost = f"{orbs.RES.get(mt, mt)} {x} + 골드 {y}"
    rng = engine.unit_range(o) if o["role"] in ("build", "summon") and not o.get("hostile") else (engine.CAST_RANGE if o["role"] == "cast" else None)
    return {"name": name, "lang": lang, "status": "ok", "engine": "orb", "element": ROLE_KO[kd], "kind": "구슬", "color": orb_color(o), "element_family": FAMILY.get(kd, 0),
            "mana": o["mana"], "mana_power": round(o["pe"], 1), "mana_stats": 0, "mana_effect": 0, "attack": 0, "defense": 0, "effect": effects[0]["name"] if effects else "", "effect_desc": o["text"], "effect_value": effects[0]["value"] if effects else 1,
            "themes": [], "unique": False, "combo": False, "effects": effects,
            "orb": {"role": o["role"], "kind": kd, "text": o["text"], "life": o["life"], "timing": o["timing"], "trig": o["trig"], "fate": o["fate"], "rng": o["rng"], "mod": o["mod"], "hp": o["hp"], "cost": cost, "range": rng,
                    "unit": o.get("unit"), "mv": o.get("mv"), "pe": round(o["pe"], 2), "hostile": bool(o.get("hostile")), "lvl": o.get("lvl"), "delay": o.get("delay"), "payload": [[v, m, mt] for v, m, mt in o["payload"]]}}

def forge_orb(name, lang):
    """이름 → 구슬 카드. 프로토타입의 orbs.orb_from_jev 와 같은 Jev 요청·같은 구슬 규칙."""
    return to_card(orbs.orb_from_jev(name, lang or "ko"), name, lang or "ko")

"""Orb construction for the web prototype (self-contained: uses only proto/vendor and proto/data, so it runs on Vercel with Root Directory = proto).
Starter orbs are precomputed from measured Jev data (data/starter_orbs.json); new orbs come from a live Jev call."""
import os, re, sys, json, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); VEN = os.path.join(HERE, "vendor")
for p in (VEN, HERE):
    if p not in sys.path: sys.path.insert(0, p)
import orbmake as S, axes_v3, axes_v2, axes_v4, forge, engine
GM, CM = .25, "value"
STARTER = ["금화 주머니", "화염검", "화염검", "방패", "곡괭이", "병사", "벌목장", "광산"]
RES = {"wood": "나무", "ore": "광석", "food": "식량", "gold": "골드", None: "자원"}
LIFE = {"instant": "", "turns": "3턴 동안 ", "stage": "이번 스테이지 동안 ", "run": "이번 런 동안 ", "forever": "영구 "}
COND = {"hit": "피격 시", "death": "사망 시", "orb": "다른 구슬을 쓸 때", "approach": "적이 다가오면"}
MOD = {"scaling": "쓸수록 +10% 성장", "risky": "위험: 사용자도 피해", "random": "효과 50~150% 무작위", "network": "인접 건물이 많을수록 강해짐"}
UNIT = {"soldier": "병사", "worker": "일꾼", "beast": "짐승", "spirit": "정령", "construct": "기계"}
# 누구를 맞히는가: 즉발 시전은 플레이어가 직접 고르고, 건물·소환물·지속·지연·조건부 효과는 자동으로 가장 가까운 적(건물·소환물은 사거리 3칸)
TG_MANUAL = {"single": "고른 적 1", "line": "고른 적과 그 옆의 적 1", "around": "고른 적 주변 무리(1칸)", "wide": "모든 적"}
TG_AUTO = {"single": "가장 가까운 적 1", "line": "가까운 적 2", "around": "가장 가까운 적 주변 무리(1칸)", "wide": "모든 적"}
def vtext(v, m, mt, o):
    tg = TG_MANUAL[o["rng"]] if engine.manual_target(o) else TG_AUTO[o["rng"]]
    return {"damage": f"{tg}에 피해 {m}", "drain": f"{tg}에 피해 {m}, 체력 {m//2} 흡수", "guard": f"방어막 +{m}", "heal": f"체력 {m} 회복", "money": f"골드 {m}",
            "steal": f"적에게서 골드 {m} 탈취", "harvest": (f"식량 {m} 수확(경작지)" if mt == "food" else f"{RES.get(mt)} {m} 채집(근처 자원 타일)"), "grow": f"{RES.get(mt or 'food')} {m} 재배", "process": f"원료 {m}개를 골드 ×1.5로 가공",
            "buff": f"아군 피해 +{max(1,m//2)}", "debuff": f"{tg} 공격 약화", "control": f"{tg} 행동 불가", "remove": "효과 1개 제거(미구현)", "transform": "변환(미구현)",
            "draw": "구슬 더 뽑기", "recycle": "버린 구슬 1개 되돌림", "trash": "버린 구슬 1개 영구 폐기", "peek": "주머니 위 3개 확인", "tempo": "마나 +1", "energy": f"마나 +{max(1,int(o['pe']//1.5))}",
            "create": ("1회용 아이템 1개 생성" if not mt else f"{RES.get(mt)} 2 생성"), "amplify": "다음 구슬 효과 ×2"}.get(v, v)
def describe(o):
    body = "; ".join(vtext(v, m, mt, o) for v, m, mt in o["payload"] if v != "move")
    life = LIFE.get(o["life"], "")
    if o["role"] == "move": t = f"이동 — 주변 {o.get('mv', 2)}칸 안의 빈 칸으로 걸어간다" + (f", 그리고 {body}" if body else "")
    elif o["role"] == "build" and o["payload"] and (o["payload"][0][0] == "grow" or (o["payload"][0][0] == "harvest" and o["payload"][0][2] == "food")): t = f"식물(체력 {o['hp']}) 심기 — 2턴 자란 뒤 매 턴 {body}"
    elif o["role"] == "build": t = f"건물(체력 {o['hp']}) 설치 — 매 턴 {body}"
    elif o["role"] == "summon": t = f"{UNIT.get(o['unit'],'병사')} 소환 — 매 턴 {body}" if not o["hostile"] else f"적대 {UNIT.get(o['unit'],'짐승')} 웨이브 Lv{o['lvl']} 소환 (처치 보상 일부)"
    else:
        t = (life + ("" if o["life"] == "instant" else "매 턴 ") + body) if o["life"] != "instant" else body
        if o["timing"] == "delayed": t = f"{o['delay']}턴 뒤: {t}"
        if o["trig"] != "none": t = f"{COND[o['trig']]} 발동 — {t}"
    if o["role"] in ("build", "summon") and not o["hostile"] and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.unit_range(o)}칸)"
    elif o["role"] == "cast" and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.CAST_RANGE}칸)"
    if engine.sustained(o): t += " [소멸: 쓰면 이 스테이지 동안 다시 나오지 않음]"
    if o["mod"]: t += f" ＋ {MOD[o['mod']]}"
    if o["fate"] == "used_up": t += " [1회용]"
    if o["fate"] == "passive": t += " [주머니에 있으면 자동]"
    return t
# 값어치 재평가(디렉터 지적: "무한 자원 생성 구슬은 강한데 마나가 너무 싸다"). 측정 모델(est_total_value)은 그대로 두고 프로토 쪽에서만 가격을 손본다.
# 지속형 골드 수입(건물·지속 시전의 money/steal/골드 채집)은 값어치가 곧바로 정산액이 되는데, 로그 비용 곡선에 눌려 너무 싸다. 그래서 이런 구슬만
# 값어치를 1.5배로 치고 곡선을 가파르게(계수 .8→1.0) 해서 마나를 올리고, 건물이면 골드 비용도 턴당 수입의 2배 이상으로 올린다. 가격은 올리기만 하고 내리지 않는다.
# (다른 구슬은 그대로: 광산·벌목장 같은 자원 건물이나 즉발 효과의 값은 건드리지 않음)
def gold_income(o): return sum(m for v, m, mt in o.payload if v in ("money", "steal") or (mt == "gold" and v in ("harvest", "grow", "create")))
def repriced_mana(o):
    if not (gold_income(o) and (o.role in ("build", "summon") or o.life != "instant")): return o.mana
    v = S.est_total_value(o) * 1.5
    return max(o.mana, max(1, min(8, round(.9 + 1.0 * math.log2(1 + v / 4)))))
def to_dict(o):
    d = dict(name=o.name, role=o.role, payload=[list(p) for p in o.payload], rng=o.rng, life=o.life, timing=o.timing, trig=o.trig, mat=o.mat, fate=o.fate, mod=o.mod, pe=round(o.pe, 2),
             mana=o.mana, hp=o.hp, bcost=list(o.bcost) if o.bcost else None, unit=o.unit, hostile=o.hostile, lvl=o.lvl, delay=o.delay, bag_only=o.bag_only, B=round(o.B, 1), amb=o.amb)
    d["mana"] = repriced_mana(o)
    if d["bcost"] and o.role == "build" and gold_income(o): d["bcost"][2] = max(d["bcost"][2], 2 * gold_income(o))
    d["text"] = describe(d); return d
def _hand(name, **kw):
    d = dict(name=name, role="cast", payload=[], rng="single", life="instant", timing="now", trig="none", mat=None, fate="returns", mod=None, pe=1.0, mana=1, hp=1, bcost=None, unit="soldier", hostile=False, lvl=1, delay=1, bag_only=False, B=10, amb=False)
    d.update(kw); d["text"] = describe(d); return d
# 손으로 만든 시작 구슬(측정 데이터 없이 규칙만 시험): 이동 구슬 하나, 식물 구슬 하나. 나머지 8개는 sync_vendor.py가 Jev 측정값으로 만든다.
HAND_STARTERS = [_hand("달리기", role="move", payload=[["move", 0, None]], mana=1, mv=2),
                 _hand("텃밭", role="build", payload=[["grow", 5, "food"]], life="run", timing="repeating", mat="food", mana=2, hp=10, bcost=["food", 1, 1], unit="worker")]
def starter_orbs(): return json.load(open(os.path.join(HERE, "data", "starter_orbs.json"), encoding="utf-8")) + [dict(o) for o in HAND_STARTERS]
def scribble(name):
    d = dict(name=name, role="cast", payload=[["tempo", 1, None]], rng="single", life="instant", timing="now", trig="none", mat=None, fate="returns", mod=None, pe=0, mana=1, hp=1, bcost=None, unit="soldier", hostile=False, lvl=1, delay=1, bag_only=True, B=1, amb=True)
    d["text"] = "수상한 낙서 — 아무 효과도 없다(손패만 차지)"; d["scribble"] = True; return d
LANG_NAMES = {"ko": "Korean", "en": "English", "ja": "Japanese", "zh-Hans": "Simplified Chinese", "zh-Hant": "Traditional Chinese", "es": "Spanish", "fr": "French", "de": "German", "pt-BR": "Brazilian Portuguese", "vi": "Vietnamese", "ru": "Russian", "th": "Thai", "ar": "Arabic"}
def jev_request(full, lang="ko"):
    bq = axes_v3.build_request(full, lang if lang in ("ko", "en") else "en")         # 측정된 질문지는 한국어·영어만 있다. 다른 언어는 "이 이름은 <언어>로 쓴 것" 한 줄만 덧붙인다(card-forge와 같은 방식)
    if lang not in ("ko", "en") and lang in LANG_NAMES: bq["state"] += f"\nThe orb name above is written in {LANG_NAMES[lang]}."
    bq["questions"]["verb"]["criteria"] = axes_v4.VERBS
    for k in ("unit", "allegiance"):
        i, o = axes_v2.CHOICES[k]; bq["questions"][k] = {"type": "choice", "instructions": i, "criteria": o}
    return bq
def orb_from_jev(full, lang="ko"):
    d = forge.call_jev(jev_request(full, lang)); a = d["answers"]
    if a["guard"]["probabilities"].get("instructs_the_evaluator", 0) > .5: return scribble(full)
    return to_dict(S.make_orb(full, cost_model=CM, gold_mult=GM, extra={full: [a]}))
FRAGS = [tuple(x) for x in json.load(open(os.path.join(HERE, "data", "fragments.json"), encoding="utf-8"))] if os.path.exists(os.path.join(HERE, "data", "fragments.json")) else []
TIERS = {"낡은": (5, 1.0), "평범한": (7, .5), "깨끗한": (9, .25), "금박": (12, .1)}
def new_blank(tier, R):
    cap, p = TIERS[tier]; fr = R.choice(FRAGS) if R.random() < p else None
    return {"tier": tier, "cap": cap, "frag": ({"pos": fr[0], "t": fr[1], "sp": fr[2]} if fr else None)}
def fuse(blank, typed):
    f = blank["frag"]
    if not f: return typed
    return f"{f['t']}{' ' if f['sp'] else ''}{typed}" if f["pos"] == "pre" else f"{typed}{' ' if f['sp'] else ''}{f['t']}"
def max_typed(blank): return 8 - (len(blank["frag"]["t"].replace(" ", "")) if blank["frag"] else 0)
def check_typed(blank, typed):
    c, err = forge.check_name(typed, "ko")
    if err: return None, err
    if len(c.replace(" ", "")) > max_typed(blank): return None, f"새겨진 말을 포함해 8글자까지입니다(쓸 수 있는 글자 {max_typed(blank)}자)"
    return c, None

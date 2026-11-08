"""Orb construction for the web prototype (self-contained: uses only proto/vendor and proto/data, so it runs on Vercel with Root Directory = proto).
Starter orbs are precomputed from measured Jev data (data/starter_orbs.json); new orbs come from a live Jev call."""
import os, re, sys, json, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); VEN = os.path.join(HERE, "vendor")
for p in (VEN, HERE):
    if p not in sys.path: sys.path.insert(0, p)
import orbmake as S, axes_v3, axes_v2, axes_v4, forge, engine, value
GM, CM = .25, "value"
STARTER = ["금화 주머니", "화염검", "화염검", "방패", "곡괭이", "병사", "벌목장", "광산"]
RES = {"wood": "나무", "ore": "광석", "food": "식량", "gold": "골드", None: "자원"}
LIFE = {"instant": "", "turns": "3턴 동안 ", "stage": "이번 스테이지 동안 ", "run": "이번 런 동안 ", "forever": "영구 "}
COND = engine.COND_KO          # 반응 조건 문구(엔진과 공유)
MOD = {"scaling": "쓸수록 +10% 성장", "risky": "위험: 사용자도 피해", "random": "효과 50~150% 무작위", "network": "인접 건물이 많을수록 강해짐"}
UNIT = {"soldier": "병사", "worker": "일꾼", "beast": "짐승", "spirit": "정령", "construct": "기계"}
# 누구를 맞히는가: 즉발 시전은 플레이어가 직접 고르고, 건물·소환물·지속·지연·조건부 효과는 자동으로 가장 가까운 적(건물·소환물은 사거리 3칸)
TG_MANUAL = {"single": "고른 적 1", "line": "고른 적과 그 옆의 적 1", "around": "고른 적 주변 무리(1칸)", "wide": "모든 적"}
TG_AUTO = {"single": "가장 가까운 적 1", "line": "가까운 적 2", "around": "가장 가까운 적 주변 무리(1칸)", "wide": "모든 적"}
EVENT_COND = ("orb", "orb_attack", "orb_eco", "orb_plant", "orb_build", "orb_summon", "orb_defense", "kill", "harvest")      # 사건이 일어날 때마다 터지는 반응(나머지 hit·death·approach는 상황 반응)
def cond_every(c): s = COND[c]; return s + "마다" if s.endswith("때") else s
def every(o):   # 건물·소환물이 일하는 때: 평소엔 매 턴, 반응형이면 사건마다
    c = o["trig"]; return "매 턴 " if c == "none" else (cond_every(c) + " " if c in EVENT_COND else ("아군이 부서질 때마다 " if c == "death" else ("플레이어가 맞을 때마다 " if c == "hit" else COND[c] + " ")))
def vtext(v, m, mt, o):
    tg = TG_MANUAL[o["rng"]] if engine.manual_target(o) else TG_AUTO[o["rng"]]
    return {"damage": f"{tg}에 피해 {m}", "drain": f"{tg}에 피해 {m}, 체력 {m//2} 흡수", "guard": f"방어막 +{m}", "heal": f"체력 {m} 회복", "money": f"골드 {m}",
            "steal": f"적에게서 골드 {m} 탈취", "harvest": (f"식량 {m} 수확(경작지)" if mt == "food" else f"{RES.get(mt)} {m} 채집(근처 자원 타일)"), "grow": f"{RES.get(mt or 'food')} {m} 재배", "process": f"원료 {m}개를 골드 ×1.5로 가공",
            "buff": f"{engine.BOOST_KO.get(mt or 'dmg', '피해')} +{m}% ({ {'instant': '3턴', 'turns': '4턴'}.get(o['life'], '이번 스테이지') }, 다른 구슬과 합산)", "burn": f"{tg}에 화상 {m}중첩 (턴마다 중첩×{engine.BURN_DMG} 피해, 1중첩씩 감소)", "debuff": f"{tg} 공격 약화", "control": f"{tg} 행동 불가", "remove": "효과 1개 제거(미구현)", "transform": "변환(미구현)",
            "draw": "구슬 더 뽑기", "recycle": "버린 구슬 1개 되돌림", "trash": "버린 구슬 1개 영구 폐기", "peek": "주머니 위 3개 확인", "tempo": "마나 +1", "energy": f"마나 +{max(1,int(o['pe']//1.5))}",
            "create": ("1회용 아이템 1개 생성" if not mt else f"{RES.get(mt)} 2 생성"), "amplify": "다음 구슬 효과 ×2"}.get(v, v)
def describe(o):
    body = "; ".join(vtext(v, m, mt, o) for v, m, mt in o["payload"] if v != "move")
    life = LIFE.get(o["life"], "")
    if o["role"] == "move": t = f"이동 — 주변 {o.get('mv', 2)}칸 안의 빈 칸으로 걸어간다" + (f", 그리고 {body}" if body else "")
    elif o["role"] == "build" and o["payload"] and (o["payload"][0][0] == "grow" or (o["payload"][0][0] == "harvest" and o["payload"][0][2] == "food")): t = f"식물(체력 {o['hp']}) 심기 — 2턴 자란 뒤 매 턴 {body}"
    elif o["role"] == "build": t = f"건물(체력 {o['hp']}) 설치 — {every(o)}{body}"
    elif o["role"] == "summon": t = f"{UNIT.get(o['unit'],'병사')} 소환 — {every(o)}{body}" if not o["hostile"] else f"적대 {UNIT.get(o['unit'],'짐승')} 웨이브 Lv{o['lvl']} 소환 (처치 보상 일부)"
    else:
        t = (life + ("" if o["life"] == "instant" else "매 턴 ") + body) if o["life"] != "instant" else body
        if o["payload"] and all(p[0] == "buff" for p in o["payload"]): t = body        # 증폭 문구에 기간이 이미 들어 있음
        if o["timing"] == "delayed": t = f"{o['delay']}턴 뒤: {t}"
        c = o["trig"]
        if c in EVENT_COND: t = f"{life}{cond_every(c)} {body}" + ("" if o["life"] not in ("instant", "turns") else f" ({engine.trig_uses(o)}회까지)") + f" [턴당 최대 {engine.TRIG_PER_TURN}회]"
        elif c != "none": t = f"{COND[c]} 발동 — {t}"
    if o["role"] in ("build", "summon") and not o["hostile"] and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.unit_range(o)}칸)"
    elif o["role"] == "cast" and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.CAST_RANGE}칸)"
    if engine.sustained(o): t += " [소멸: 쓰면 이 스테이지 동안 다시 나오지 않음]"
    if o["mod"]: t += f" ＋ {MOD[o['mod']]}"
    if o["fate"] == "used_up": t += " [1회용]"
    if o["fate"] == "passive": t += " [주머니에 있으면 자동]"
    return t
# 가격: 이전의 손질(측정 모델 est_total_value × 골드 수입 1.5배 등)을 value.py의 표준 가치 모델로 대체했다. Jev는 가격을 판단하지 않는다(value.py 머리말).
def gold_income(o): return sum(m for v, m, mt in o.payload if v in ("money", "steal") or (mt == "gold" and v in ("harvest", "grow", "create")))
def to_dict(o):
    d = dict(name=o.name, role=o.role, payload=[list(p) for p in o.payload], rng=o.rng, life=o.life, timing=o.timing, trig=o.trig, mat=o.mat, fate=o.fate, mod=o.mod, pe=round(o.pe, 2),
             mana=o.mana, hp=o.hp, bcost=list(o.bcost) if o.bcost else None, unit=o.unit, hostile=o.hostile, lvl=o.lvl, delay=o.delay, bag_only=o.bag_only, B=round(o.B, 1), amb=o.amb)
    shape(d, getattr(o, "boost", None))
    if d["bcost"] and o.role == "build" and gold_income(o): d["bcost"][2] = max(d["bcost"][2], 2 * gold_income(o))
    d["mana"] = value.mana_for(d)            # 건물 비용을 먼저 정한 뒤 나머지를 마나로 매긴다
    value.enforce_cost(d)                    # 마나로 못 갚는 슬롯형(회수 배율 4 초과)은 재료·골드를 더 받는다
    d["text"] = describe(d); return d
def shape(d, boost=None):
    """Jev가 정한 동사 수치(측정 모델의 m)를 시너지 동사의 실제 단위로 바꾼다: buff → (퍼센트, 키우는 것), burn → 화상 중첩 수. 한 번만 부른다(구슬 생성 시)."""
    vs = [p[0] for p in d["payload"]]
    for p in d["payload"]:
        if p[0] == "buff":
            kind = boost if boost in engine.BOOST_KINDS else ("burn" if "burn" in vs else "growth" if any(v in ("harvest", "grow") for v in vs) else "income" if any(v in ("money", "steal", "process") for v in vs) else "dmg")
            p[1] = max(10, min(40, round(10 + 8 * d["pe"]))); p[2] = kind
        elif p[0] == "burn": p[1] = max(1, round(p[1] / 4))
    if d["role"] == "cast" and d["life"] in ("stage", "run", "forever") and d["rng"] == "single" and vs and vs[0] == "burn": d["rng"] = "around"      # 긴 지속은 한 마리가 아니라 무리(vendor 규칙과 같음)
    react_scale(d); return d
def react_scale(d):
    """드문 사건에 반응하는 구슬은 사건 한 번에 더 세게: 매 턴 일하는 구슬(기간 동안 약 REMAIN번)과 총량이 비슷하도록 사건 수로 나눠 키운다(최대 3배).
    횟수가 정해진 즉발·3턴 반응(2회·4회)과, 플레이어 부활(death 시전)은 제외."""
    c = d["trig"]
    if c == "none" or (d["role"] == "cast" and (d["life"] in ("instant", "turns") or c == "death")): return d
    ev = 3.0 if c == "approach" else value.E0.events.get(c)
    if not ev: return d
    f = max(1.0, min(3.0, value.E0.remain / ev))
    for p in d["payload"]:
        if p[0] not in ("buff", "move"): p[1] = max(1, round(p[1] * f))
    return d
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
# ---- 시너지용 질문 확장(측정 파일은 그대로 두고 요청을 만들 때 덧씌운다): 화상 동사, 반응 조건(어떤 구슬/사건에 반응하나), 증폭 대상
VERBS = dict(axes_v4.VERBS)
VERBS["burn"] = "burning, igniting, scorching, poisoning, or inflicting a lingering condition that keeps hurting enemies over several turns"
VERBS["debuff"] = VERBS["debuff"].replace("poisoning, ", "")
VERBS["trash"] = VERBS["trash"].replace("burning up, ", "")
VERBS["buff"] = "making allies stronger, faster, braver, or more capable, or boosting a kind of effect, like a blessing, a catalyst, a booster, or a lucky charm"
TRIGGERS = {"none": "no, it simply happens when used", "hit": "when someone is hit or takes damage", "death": "when someone dies or is destroyed", "approach": "when an enemy comes near or steps on it",
            "orb": "when any other orb is used", "orb_attack": "when an attacking orb is used, like a weapon, a spell, or a strike", "orb_eco": "when a gathering, farming, trading, or money-making orb is used",
            "orb_plant": "when a plant or farming orb is used", "orb_build": "when a building orb is used", "orb_summon": "when a summoning orb is used", "orb_defense": "when a defending or healing orb is used",
            "kill": "when an enemy is defeated", "harvest": "when resources are gathered"}
BOOST = ("If an orb with this name makes some kind of effect stronger, which kind would it most naturally strengthen?",
         {"dmg": "damage dealt to enemies: weapons, strength, fury", "burn": "burning and poison: fire, embers, oil, kindling", "income": "gold and trade profits: wealth, markets, greed",
          "growth": "gathering and growing resources: harvests, farms, rain, fertility", "defense": "shields and healing: armor, blessings, medicine", "unit": "buildings and summoned creatures: leadership, banners, workshops"})
def jev_request(full, lang="ko"):
    bq = axes_v3.build_request(full, lang if lang in ("ko", "en") else "en")         # 측정된 질문지는 한국어·영어만 있다. 다른 언어는 "이 이름은 <언어>로 쓴 것" 한 줄만 덧붙인다(card-forge와 같은 방식)
    if lang not in ("ko", "en") and lang in LANG_NAMES: bq["state"] += f"\nThe orb name above is written in {LANG_NAMES[lang]}."
    bq["questions"]["verb"]["criteria"] = VERBS
    bq["questions"]["trigger"]["criteria"] = TRIGGERS
    bq["questions"]["boost"] = {"type": "choice", "instructions": BOOST[0], "criteria": BOOST[1]}
    for k in ("unit", "allegiance"):
        i, o = axes_v2.CHOICES[k]; bq["questions"][k] = {"type": "choice", "instructions": i, "criteria": o}
    return bq
def orb_from_jev(full, lang="ko"):
    d = forge.call_jev(jev_request(full, lang)); a = d["answers"]
    if a["guard"]["probabilities"].get("instructs_the_evaluator", 0) > .5: return scribble(full)
    orb = S.make_orb(full, cost_model=CM, gold_mult=GM, extra={full: [a]}); pb = a["boost"]["probabilities"]; orb.boost = max(pb, key=pb.get)       # 증폭 대상(buff 동사일 때만 쓰임)
    return to_dict(orb)
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

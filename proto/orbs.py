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
def cond_every(c):
    if c == "hit": return "피격될 때마다"
    s = COND[c]; return s + "마다" if s.endswith("때") else s
def every(o):   # 건물·소환물이 일하는 때: 평소엔 매 턴, 반응형이면 사건마다
    c = o["trig"]
    if c == "none" and o["timing"] == "delayed": return f"처음 {o['delay']}턴은 쉬고 그다음부터 매 턴 "
    return "매 턴 " if c == "none" else (cond_every(c) + " " if c in EVENT_COND else ("아군이 부서질 때마다 " if c == "death" else ("플레이어가 맞을 때마다 " if c == "hit" else COND[c] + " ")))
def vtext(v, m, mt, o):
    tg = TG_MANUAL[o["rng"]] if engine.manual_target(o) else TG_AUTO[o["rng"]]
    return {"damage": f"{tg}에 피해 {m}", "drain": f"{tg}에 피해 {m}, 체력 {m//2} 흡수", "guard": f"방어막 +{m}", "heal": f"체력 {m} 회복", "money": f"골드 {m}",
            "steal": f"적에게서 골드 {m} 탈취", "harvest": (f"식량 {m} 수확(경작지)" if mt == "food" else f"{RES.get(mt)} {m} 채집({'옆 칸' if o['role'] in ('build', 'summon') else '3칸 안'} 자원 타일)"), "grow": f"{RES.get(mt or 'food')} {m} 재배", "process": f"원료 {m}개를 골드 ×1.5로 가공",
            "buff": f"{engine.BOOST_KO.get(mt or 'dmg', '피해')} +{m}% ({ {'instant': '3턴', 'turns': '4턴'}.get(o['life'], '이번 스테이지') }, 다른 구슬과 합산)", "burn": f"{tg}에 화상 {m}중첩 (턴마다 중첩×{engine.BURN_DMG} 피해, 1중첩씩 감소)", "debuff": f"{tg} 공격 약화", "control": f"{tg} 행동 불가", "remove": "효과 1개 제거(미구현)", "transform": "변환(미구현)",
            "draw": f"구슬 {engine.draw_n(o)}개 더 뽑기", "recycle": "버린 구슬 1개 되돌림", "trash": "버린 구슬 1개 영구 폐기", "peek": "주머니 위 3개 확인", "tempo": "마나 +1, 구슬 1개 더 뽑기", "energy": f"마나 +{engine.energy_gain(o)}",
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
        # 피격도 사건처럼 쓴다: 맞을 때마다 한 번(매 턴이 아님)
        if c in EVENT_COND or c == "hit": t = f"{life}{cond_every(c)} {body}" + ("" if o["life"] not in ("instant", "turns") else f" ({engine.trig_uses(o)}회까지)") + f" [턴당 최대 {engine.TRIG_PER_TURN}회]"
        elif c != "none": t = f"{COND[c]} 발동 — {t}"
    if o["role"] in ("build", "summon") and not o["hostile"] and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.unit_range(o)}칸)"
    elif o["role"] == "cast" and any(p[0] in engine.ENEMY_V for p in o["payload"]): t += f" (사거리 {engine.CAST_RANGE}칸)"
    if engine.sustained(o) and o["fate"] != "passive": t += " [소멸: 쓰면 이 스테이지 동안 다시 나오지 않음]"      # 자동 구슬은 쓰지 않으니 소멸도 없다
    if o["mod"]: t += f" ＋ {MOD[o['mod']]}"
    if o["fate"] == "used_up": t += " [1회용]"
    if o["fate"] == "passive": t += " [주머니에 있으면 자동]"
    if o.get("echo"): t += " [메아리: 쓰면 사본이 이번 턴 손패에 생김]"
    fm = o.get("fragmod")
    if fm: t += f" [사전단어 '{fm['word']}': {fm['name']}]" if fm.get("word") else f" [사전단어: {fm['name']}]"
    h = o.get("hint")
    if h: t += f" [힌트 '{h['label']}' 일치: 효과 ×{h['mult']:g}]" if h["ok"] else f" [힌트 '{h['label']}' 불일치]"
    return t
# 가격: 이전의 손질(측정 모델 est_total_value × 골드 수입 1.5배 등)을 value.py의 표준 가치 모델로 대체했다. Jev는 가격을 판단하지 않는다(value.py 머리말).
def gold_income(o): return sum(m for v, m, mt in o.payload if v in ("money", "steal") or (mt == "gold" and v in ("harvest", "grow", "create")))
def to_dict(o):
    d = dict(name=o.name, role=o.role, payload=[list(p) for p in o.payload], rng=o.rng, life=o.life, timing=o.timing, trig=o.trig, mat=o.mat, fate=o.fate, mod=o.mod, pe=round(o.pe, 2),
             mana=o.mana, hp=o.hp, bcost=list(o.bcost) if o.bcost else None, unit=o.unit, hostile=o.hostile, lvl=o.lvl, delay=o.delay, bag_only=o.bag_only, B=round(o.B, 1), amb=o.amb)
    if d["fate"] == "passive" and d["role"] != "cast": d["fate"] = "returns"      # 자동은 시전만: 건물·소환물·이동은 놓을 칸이 있어야 하니 손패로 온다(엔진은 자동 시전만 처리)
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
    hp_scale(d); react_scale(d); return d
DMG_V = ("damage", "drain")
def placed_scale(d):
    """건물·소환물·스테이지 이상 지속 시전의 피해 수치에 곱할 배율(적 체력이 측정 모델의 가정보다 클수록 커진다). 즉발·3턴 구슬은 수치가 이미 한 방·몇 방 기준이라 1."""
    return engine.CFG["ehp"] / engine.HP_REF if ((d["role"] in ("build", "summon") and not d.get("hostile")) or (d["role"] == "cast" and d["life"] in ("stage", "run", "forever"))) else 1.0
def hp_scale(d):
    s = placed_scale(d)
    if s != 1.0:
        for p in d["payload"]:
            if p[0] in DMG_V: p[1] = max(1, round(p[1] * s))
    return d
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
# 손패·마나 동사(2026-11-09): 측정 질문문의 draw는 '자석·그물처럼 끌어당기기'라 손패와 무관한 이름에만 켜졌다 → 게임 안의 뜻(이번 턴 구슬을 더 뽑음 / 마나를 더 씀)으로 바꿈.
# 실측(이름 12 + 대조 4): 책가방 draw .18→.95, 준비성·계획표·영감 → draw .7, 커피 energy .39→.88, 명상 .56→.96, 대조(화염검·금화 주머니·방패·광산)는 그대로.
VERBS["draw"] = "drawing more orbs into your hand right now, for more options this turn: preparation, inspiration, planning, quick hands, a backpack, a bag of tricks"
VERBS["tempo"] = "speed, haste, rushing, or doing two things at once, like getting an extra action this turn"
VERBS["energy"] = "charging up, fueling, caffeine, focus, or meditation that gives you more mana to spend this turn"
VERBS["buff"] = "making allies stronger, faster, braver, or more capable, or boosting a kind of effect, like a blessing, a catalyst, a booster, or a lucky charm"
TRIGGERS = {"none": "no, it simply happens when used", "hit": "when the PLAYER is struck by an enemy or takes damage (being attacked; NOT when the player attacks or hits something)", "death": "when someone dies or is destroyed", "approach": "when an enemy comes near or steps on it",
            "orb": "when any other orb is used", "orb_attack": "whenever the player attacks, strikes, or swings, i.e. when ANOTHER orb that attacks is used, as a combo or follow-up bonus (not for an attack that simply hurts)", "orb_eco": "when ANOTHER gathering, farming, trading, or money-making orb is used, as a follow-up bonus",
            "orb_plant": "when ANOTHER plant or farming orb is used", "orb_build": "when ANOTHER building orb is used", "orb_summon": "when ANOTHER summoning orb is used", "orb_defense": "when ANOTHER defending or healing orb is used",
            "kill": "when an enemy is defeated", "harvest": "when resources are gathered"}
BOOST = ("If an orb with this name makes some kind of effect stronger, which kind would it most naturally strengthen?",
         {"dmg": "damage dealt to enemies: weapons, strength, fury", "burn": "burning and poison: fire, embers, oil, kindling", "income": "gold and trade profits: wealth, markets, greed",
          "growth": "gathering and growing resources: harvests, farms, rain, fertility", "defense": "shields and healing: armor, blessings, medicine", "unit": "buildings and summoned creatures: leadership, banners, workshops", "bounty": "rewards for defeating enemies: bounties, trophies, hunting, plunder, wanted posters"})
def jev_request(full, lang="ko"):
    bq = axes_v3.build_request(full, lang if lang in ("ko", "en") else "en")         # 측정된 질문지는 한국어·영어만 있다. 다른 언어는 "이 이름은 <언어>로 쓴 것" 한 줄만 덧붙인다(card-forge와 같은 방식)
    if lang not in ("ko", "en") and lang in LANG_NAMES: bq["state"] += f"\nThe orb name above is written in {LANG_NAMES[lang]}."
    bq["questions"]["verb"]["criteria"] = VERBS
    bq["questions"]["trigger"]["criteria"] = TRIGGERS
    bq["questions"]["boost"] = {"type": "choice", "instructions": BOOST[0], "criteria": BOOST[1]}
    for k in ("unit", "allegiance"):
        i, o = axes_v2.CHOICES[k]; bq["questions"][k] = {"type": "choice", "instructions": i, "criteria": o}
    bq["questions"]["allegiance"] = {"type": "choice", "criteria": ALLEGIANCE[1], "instructions": ALLEGIANCE[0]}      # 측정 질문은 '보통 누구 편인가'라 늑대·용 같은 짐승이 적 웨이브가 됐다
    return bq
ALLEGIANCE = ("If the player summoned or called the creature named on this orb, would it fight on the player's side or would it attack the player? "
              "Animals, beasts, dragons, and monsters that the player summons or tames fight for the player.",
              {"ally": "it fights for the player: a summoned or tamed creature, pet, helper, hero, worker, or familiar",
               "hostile": "it attacks the player: the name itself says enemies, invaders, a horde, pests, or a curse that brings monsters against the player"})
def orb_from_jev(full, lang="ko"):
    d = forge.call_jev(jev_request(full, lang)); a = d["answers"]
    if a["guard"]["probabilities"].get("instructs_the_evaluator", 0) > .5: return scribble(full)
    orb = S.make_orb(full, cost_model=CM, gold_mult=GM, extra={full: [a]}); pb = a["boost"]["probabilities"]; orb.boost = max(pb, key=pb.get)       # 증폭 대상(buff 동사일 때만 쓰임)
    return to_dict(orb)
TIERS = {"낡은": (5, 1.0), "평범한": (7, .5), "깨끗한": (9, .25), "금박": (12, .1)}
# ---- 사전단어(빈 구슬에 미리 새겨진 말) — 2026-11-08 디렉터 확정: 풀은 **변환 말 144개 + 힌트 말 54개** 두 종류뿐이다(옛 '맛내기 말' 210개는 폐기, 겹치는 말은 한쪽으로).
# 두 종류 모두 **Jev는 플레이어가 쓴 이름만 읽는다**(말이 효과를 대신 켜 주면 안 되므로). 변환 말은 표(data/fragment_mods.json, 문서 docs/FRAGMENT_MODS.md)대로 결정적으로 구슬을 바꾸고(가격 표시 마나 포함),
# 힌트 말은 이름이 그 계열이면 효과 ×1.2(가격 그대로)를 준다. 사전단어가 안 붙은 빈 구슬도 많다(등급별 확률 TIERS).
HINT_MULT = 1.2
HINT_SHARE = .5          # 사전단어가 붙은 빈 구슬 중 힌트 말인 비율(나머지는 변환 말)
TRAITS = {   # 키: (이름표, 그 특성으로 치는 효과 동사, 그 특성으로 치는 구슬 역할)
    "burn": ("화상", {"burn"}, set()), "strike": ("타격", {"damage", "drain"}, set()), "income": ("수입", {"money", "steal", "process"}, set()), "grow": ("채집·재배", {"harvest", "grow"}, set()),
    "build": ("건물", set(), {"build"}), "summon": ("소환", set(), {"summon"}), "guard": ("방어·회복", {"guard", "heal"}, set()), "control": ("제어·약화", {"control", "debuff"}, set()), "boost": ("증폭", {"buff", "amplify"}, set())}
_HW = {   # 계열별 힌트 말: (앞에 붙는 말 3, 뒤에 붙는 말 3). 앞말은 "말 ___", 뒷말은 "___ 말"(띄어 씀). 변환 표와 겹치거나 변환처럼 읽히는 말("황금"·"저주받은"·"일격"·"증폭"·"강화")은 뺐다.
    "burn": ("불타는 화염의 잿불의", "불꽃 화염 용암"), "strike": ("맹렬한 강타 번개", "강습 폭발 화살"), "income": ("부유한 상인의 금빛", "상회 은행 보물"), "grow": ("풍년의 숲속의 푸른", "농장 열매 씨앗"),
    "build": ("석조 튼튼한 벽돌", "성채 공방 망루"), "summon": ("용병 군단의 수비대", "부대 병사 기사단"), "guard": ("철벽의 방패 치유의", "방벽 갑옷 성역"), "control": ("서리 얼어붙은 마비", "족쇄 안개 함정"),
    "boost": ("고취된 축복의 각성한", "축복 응원 격려")}
HINT_WORDS = [(k, pos, w, True) for k, (pre, suf) in _HW.items() for pos, ws in (("pre", pre), ("suf", suf)) for w in ws.split()]
_MF = os.path.join(HERE, "data", "fragment_mods.json"); _M = json.load(open(_MF, encoding="utf-8")) if os.path.exists(_MF) else {"rules": {}, "words": []}
MOD_RULES = {k: (v["name"], v["text"]) for k, v in _M["rules"].items()}                       # 변환 키 → (이름, 설명)
MOD_WORDS = [(w["mod"], w["pos"], w["t"], bool(w["sp"])) for w in _M["words"]]                  # (변환 키, 앞/뒤, 말, 띄어 쓰나)
def trait_ok(d, trait):
    """이름이 그 특성이었나: Jev가 읽은 결과(만들어진 구슬)의 효과 동사나 역할이 특성에 속하고, 애매한 이름(amb)이 아닐 것."""
    if d.get("scribble") or d.get("amb") or trait not in TRAITS: return False
    _, verbs, roles = TRAITS[trait]; vs = {p[0] for p in d["payload"]}
    return bool(vs & verbs) or (d["role"] in roles and not d.get("hostile"))
def apply_hint(d, trait):
    """힌트 결과를 구슬에 새긴다. 일치하면 효과 수치 일괄 ×HINT_MULT(마나·비용은 그대로). d를 고쳐 쓰고 돌려준다."""
    ok = trait_ok(d, trait)
    if ok:
        for p in d["payload"]:
            if p[0] != "move": p[1] = max(p[1] + 1, round(p[1] * HINT_MULT))      # 작은 수치(골드 1 등)도 최소 +1은 커지게
    d["hint"] = {"trait": trait, "label": TRAITS[trait][0], "ok": ok, "mult": HINT_MULT if ok else 1.0}
    d["text"] = describe(d); return d

# ---- 변환 말(12종). 표대로 결정적으로 구슬을 바꾼다. 수치·마나 증감은 표(docs/FRAGMENT_MODS.md 1절)의 값이고 모두 임시.
RNG_STEPS = ["single", "line", "around", "wide"]
TN = {"instant": 1.0, "turns": 1.6 / 3, "stage": 2.4 / 12, "run": 3.2 / 40, "forever": 4.0 / 100}      # 지속별 한 번의 크기(측정 모델의 T/N): 지속을 바꿀 때 수치를 이 비로 다시 맞춘다
LIFE_UP = {"instant": "turns", "turns": "stage", "stage": "run"}
REVERSE = {"damage": "heal", "heal": "damage", "debuff": "buff", "buff": "debuff", "guard": "debuff", "money": "steal", "steal": "money", "harvest": "grow", "grow": "harvest", "draw": "trash", "trash": "draw"}
def _scale(d, f):
    for p in d["payload"]:
        if p[0] != "move": p[1] = max(1, round(p[1] * f))
def _mana(d, k): d["mana"] = max(1, min(8, d["mana"] + k))
def _aura(d):       # 긴 지속은 한 마리가 아니라 무리(측정 모델 규칙)
    vs = [p[0] for p in d["payload"]]
    if d["role"] == "cast" and d["life"] in ("stage", "run", "forever") and d["rng"] == "single" and vs and vs[0] in engine.ENEMY_V: d["rng"] = "around"
def _boost_kind(vs): return "burn" if "burn" in vs else "growth" if any(v in ("harvest", "grow") for v in vs) else "income" if any(v in ("money", "steal", "process") for v in vs) else "dmg"
def apply_mod(d, mod, word=None):
    """변환 말을 구슬에 적용한다(d를 고쳐 쓰고 돌려줌). 낙서·알 수 없는 변환은 그대로. 적용할 게 없는 구슬(예: 이미 가장 좁은 범위의 축소)은 효과가 없을 수 있다."""
    if d.get("scribble") or mod not in MOD_RULES: return d
    r = d["role"]; placed = r in ("build", "summon") and not d.get("hostile"); usable = r == "cast" or placed
    if mod == "reverse":
        sc = placed_scale(d)           # 건물·소환·지속의 피해 수치는 체력비로 키워져 있으니, 피해↔회복을 뒤집을 때 그만큼 보정한다
        for p in d["payload"]:
            nv = REVERSE.get(p[0])
            if not nv: continue
            old = p[0]
            if old in DMG_V and nv not in DMG_V: p[1] = max(1, round(p[1] / sc))
            elif old not in DMG_V and nv in DMG_V: p[1] = max(1, round(p[1] * sc))
            p[0] = nv
            if nv == "buff": p[1] = max(10, min(40, round(10 + 8 * d["pe"]))); p[2] = _boost_kind([q[0] for q in d["payload"]])
            elif old == "buff": p[1] = max(1, round(d["pe"] * 3)); p[2] = None
        _scale(d, .9); _aura(d)
        d["mana"] = value.mana_for(d); value.enforce_cost(d)        # 효과의 종류가 바뀌었으니 가격을 다시 매긴다(회복 1마나 → 피해 건물 1마나 같은 공짜를 막음)
    elif mod == "bigger":
        d["rng"] = RNG_STEPS[min(3, RNG_STEPS.index(d["rng"]) + 1)] if d["rng"] in RNG_STEPS else d["rng"]
        if placed: d["hp"] = max(1, round(d["hp"] * 1.3))
        _scale(d, .9); _mana(d, 1)
    elif mod == "smaller":
        d["rng"] = RNG_STEPS[max(0, RNG_STEPS.index(d["rng"]) - 1)] if d["rng"] in RNG_STEPS else d["rng"]
        _scale(d, .85); _mana(d, -1)
    elif mod == "faster":
        if d["timing"] == "delayed": d["timing"] = "now"
        _mana(d, -1)
    elif mod == "slower":
        if usable and not (r == "cast" and d["trig"] != "none"):      # 반응형 시전은 기다릴 일이 없다
            d["delay"] = (d["delay"] if d["timing"] == "delayed" else 0) + 2; d["timing"] = "delayed"; _scale(d, 1.4)
    elif mod == "stronger": _scale(d, 1.4); _mana(d, 1)
    elif mod == "weaker": _scale(d, .7); _mana(d, -1)
    elif mod == "risky": _scale(d, 1.5); d["mod"] = "risky"
    elif mod == "random": d["mod"] = "random"; _mana(d, -1)
    elif mod == "once":
        _scale(d, 1.5)
        if d["fate"] != "passive": d["fate"] = "used_up"
    elif mod == "lasting":
        if placed: d["hp"] = max(1, round(d["hp"] * 1.5))
        elif r == "cast" and d["life"] in LIFE_UP:
            old_s = placed_scale(d); new = LIFE_UP[d["life"]]; _scale(d, TN[new] / TN[d["life"]] * .8); d["life"] = new; _mana(d, 1); _aura(d)
            if placed_scale(d) != old_s:       # 즉발·3턴 → 스테이지: 피해는 체력비 배율을 새로 받는다
                for p in d["payload"]:
                    if p[0] in DMG_V: p[1] = max(1, round(p[1] * placed_scale(d) / old_s))
    elif mod == "echo": d["echo"] = True; _mana(d, 1)
    d["fragmod"] = {"key": mod, "name": MOD_RULES[mod][0], "word": word}
    d["text"] = describe(d); return d

def frag_info(blank):
    """화면용: 이 빈 구슬의 사전단어가 무엇을 하는가(없으면 None). kind = hint | mod."""
    f = blank.get("frag")
    if not f: return None
    if f.get("hint") in TRAITS: tr = f["hint"]; return {"kind": "hint", "key": tr, "label": TRAITS[tr][0], "mult": HINT_MULT, "text": f"이름이 '{TRAITS[tr][0]}' 계열이면 효과 ×{HINT_MULT:g}"}
    if f.get("mod") in MOD_RULES: nm, tx = MOD_RULES[f["mod"]]; return {"kind": "mod", "key": f["mod"], "label": nm, "text": tx, "word": f["t"]}
    return None
hint_info = frag_info       # 옛 이름
def new_blank(tier, R):
    cap, p = TIERS[tier]; fr = None
    if R.random() < p:
        if (R.random() < HINT_SHARE) or not MOD_WORDS: k, pos, w, sp = R.choice(HINT_WORDS); fr = {"pos": pos, "t": w, "sp": sp, "hint": k, "mod": None}
        else: k, pos, w, sp = R.choice(MOD_WORDS); fr = {"pos": pos, "t": w, "sp": sp, "hint": None, "mod": k}
    return {"tier": tier, "cap": cap, "frag": fr}
def fuse(blank, typed):
    f = blank["frag"]
    if not f: return typed
    return f"{f['t']}{' ' if f['sp'] else ''}{typed}" if f["pos"] == "pre" else f"{typed}{' ' if f['sp'] else ''}{f['t']}"
def orb_with_fragment(full, typed, hint=None, mod=None, word=None, lang="ko", build=None):
    """사전단어가 붙은 이름 → 구슬. Jev는 쓴 이름(typed)만 읽고, 구슬 이름은 새긴 전체 이름(full). 힌트면 특성이 맞을 때 ×HINT_MULT, 변환이면 표대로 구슬을 바꾼다. 둘 다 없으면 전체 이름을 읽는다.
    프로토타입(빈 구슬 흐름)과 card-forge(서버가 클라이언트의 요청을 받을 때)가 같이 쓴다."""
    build = build or orb_from_jev; hint = hint if hint in TRAITS else None; mod = mod if mod in MOD_RULES else None
    d = build(typed if (hint or mod) else full, lang); d["name"] = full
    if d.get("scribble"): return d
    if hint: apply_hint(d, hint)
    if mod: apply_mod(d, mod, word)
    return d
def orb_with_hint(full, typed, hint, lang="ko", build=None): return orb_with_fragment(full, typed, hint=hint, lang=lang, build=build)
def orb_from_blank(blank, typed, lang="ko", build=None):
    """빈 구슬 + 플레이어가 쓴 이름 → 구슬."""
    f = blank.get("frag") or {}; return orb_with_fragment(fuse(blank, typed), typed, f.get("hint"), f.get("mod"), f.get("t"), lang, build)
def max_typed(blank): return 8 - (len(blank["frag"]["t"].replace(" ", "")) if blank["frag"] else 0)
def check_typed(blank, typed):
    c, err = forge.check_name(typed, "ko")
    if err: return None, err
    if len(c.replace(" ", "")) > max_typed(blank): return None, f"새겨진 말을 포함해 8글자까지입니다(쓸 수 있는 글자 {max_typed(blank)}자)"
    return c, None

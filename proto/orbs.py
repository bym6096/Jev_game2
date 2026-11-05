"""Orb construction for the web prototype: starter orbs from measured Jev data, new orbs from a live Jev call. Shares make_orb with the simulator."""
import os, re, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "sim")); sys.path.insert(0, os.path.join(ROOT, "measurements", "orb_axes")); sys.path.insert(0, os.path.join(ROOT, "toys", "card-forge"))
import orbsim as S, axes_v3, axes_v2, axes_v4, forge
GM, CM = .25, "value"
STARTER = ["금화 주머니", "화염검", "화염검", "방패", "곡괭이", "병사", "벌목장", "광산"]
RES = {"wood": "나무", "ore": "광석", "food": "식량", "gold": "골드", None: "자원"}
LIFE = {"instant": "", "turns": "3턴 동안 ", "stage": "이번 스테이지 동안 ", "run": "이번 런 동안 ", "forever": "영구 "}
COND = {"hit": "피격 시", "death": "사망 시", "orb": "다른 구슬을 쓸 때", "approach": "적이 다가오면"}
MOD = {"scaling": "쓸수록 +10% 성장", "risky": "위험: 사용자도 피해", "random": "효과 50~150% 무작위", "network": "인접 건물이 많을수록 강해짐"}
UNIT = {"soldier": "병사", "worker": "일꾼", "beast": "짐승", "spirit": "정령", "construct": "기계"}
def vtext(v, m, mt, o):
    tg = {"single": "적 1", "line": "적 2", "around": "적 무리(1칸)", "wide": "모든 적"}[o["rng"]]
    return {"damage": f"{tg}에 피해 {m}", "drain": f"{tg}에 피해 {m}, 체력 {m//2} 흡수", "guard": f"방어막 +{m}", "heal": f"체력 {m} 회복", "money": f"골드 {m}",
            "steal": f"적에게서 골드 {m} 탈취", "harvest": f"{RES.get(mt)} {m} 채집(근처 자원 타일)", "grow": f"{RES.get(mt or 'food')} {m} 재배", "process": f"원료 {m}개를 골드 ×1.5로 가공",
            "buff": f"아군 피해 +{max(1,m//2)}", "debuff": f"{tg} 공격 약화", "control": f"{tg} 행동 불가", "remove": "효과 1개 제거(미구현)", "transform": "변환(미구현)",
            "draw": "구슬 더 뽑기", "recycle": "버린 구슬 1개 되돌림", "trash": "버린 구슬 1개 영구 폐기", "peek": "주머니 위 3개 확인", "tempo": "마나 +1", "energy": f"마나 +{max(1,int(o['pe']//1.5))}",
            "create": ("1회용 아이템 1개 생성" if not mt else f"{RES.get(mt)} 2 생성"), "amplify": "다음 구슬 효과 ×2"}.get(v, v)
def describe(o):
    body = "; ".join(vtext(v, m, mt, o) for v, m, mt in o["payload"])
    life = LIFE.get(o["life"], "")
    if o["role"] == "build":
        b = o["bcost"]; t = f"건물(체력 {o['hp']}) 설치 — 매 턴 {body}"
    elif o["role"] == "summon":
        t = f"{UNIT.get(o['unit'],'병사')} 소환 — 매 턴 {body}" if not o["hostile"] else f"적대 {UNIT.get(o['unit'],'짐승')} 웨이브 Lv{o['lvl']} 소환 (처치 보상 일부)"
    else:
        t = (life + ("" if o["life"] == "instant" else "매 턴 ") + body) if o["life"] != "instant" else body
        if o["timing"] == "delayed": t = f"{o['delay']}턴 뒤: {t}"
        if o["trig"] != "none": t = f"{COND[o['trig']]} 발동 — {t}"
    if o["mod"]: t += f" ＋ {MOD[o['mod']]}"
    if o["fate"] == "used_up": t += " [1회용]"
    if o["fate"] == "passive": t += " [주머니에 있으면 자동]"
    return t
def to_dict(o):
    d = dict(name=o.name, role=o.role, payload=[list(p) for p in o.payload], rng=o.rng, life=o.life, timing=o.timing, trig=o.trig, mat=o.mat, fate=o.fate, mod=o.mod, pe=round(o.pe, 2),
             mana=o.mana, hp=o.hp, bcost=list(o.bcost) if o.bcost else None, unit=o.unit, hostile=o.hostile, lvl=o.lvl, delay=o.delay, bag_only=o.bag_only, B=round(o.B, 1), amb=o.amb)
    d["text"] = describe(d); return d
def starter_orbs(): return [to_dict(S.make_orb(n, cost_model=CM, gold_mult=GM)) for n in STARTER]
def scribble(name):
    d = dict(name=name, role="cast", payload=[["tempo", 1, None]], rng="single", life="instant", timing="now", trig="none", mat=None, fate="returns", mod=None, pe=0, mana=1, hp=1, bcost=None, unit="soldier", hostile=False, lvl=1, delay=1, bag_only=True, B=1, amb=True)
    d["text"] = "수상한 낙서 — 아무 효과도 없다(손패만 차지)"; d["scribble"] = True; return d
def jev_request(full):
    bq = axes_v3.build_request(full); bq["questions"]["verb"]["criteria"] = axes_v4.VERBS
    for k in ("unit", "allegiance"):
        i, o = axes_v2.CHOICES[k]; bq["questions"][k] = {"type": "choice", "instructions": i, "criteria": o}
    return bq
def orb_from_jev(full):
    d = forge.call_jev(jev_request(full)); a = d["answers"]
    if a["guard"]["probabilities"].get("instructs_the_evaluator", 0) > .5: return scribble(full)
    o = S.make_orb(full, cost_model=CM, gold_mult=GM, extra={full: [a]}); r = to_dict(o); r["answers_brief"] = {"verb": max(a["verb"]["probabilities"], key=a["verb"]["probabilities"].get)}; return r
# --- pre-written fragments (same lists and join rule as the toy)
def _lst(t, var):
    m = re.search(r"const " + var + r' = \((.*?)\)\.split\("\|"\)', t, re.S); return "".join(re.findall(r'"([^"]*)"', m.group(1))).split("|")
_T = open(os.path.join(ROOT, "toys", "card-forge", "template.html"), encoding="utf-8").read()
PRE, SP, ATT = _lst(_T, "PRE"), _lst(_T, "SUF_SP"), _lst(_T, "SUF_ATT")
FRAGS = [("pre", x, True) for x in PRE] + [("suf", x, True) for x in SP] + [("suf", x, False) for x in ATT]
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

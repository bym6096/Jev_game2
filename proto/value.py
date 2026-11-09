"""표준 가치 모델 — 구슬 하나의 값어치를 **골드 환산**으로 정량화하고, 그 값에서 마나 가격을 정한다. Jev가 가격을 판단하지 않는다: Jev는 이름에서 동사·지속·범위·이름의 힘을 읽을 뿐이고,
가격은 이 파일의 규칙이 계산한다(같은 구슬은 항상 같은 가격).

구조
  1. econ(): 환산율을 **엔진 상수(engine.CFG·WAVES·STAGE_TYPES)에서 계산**한다. 적 체력·현상금·정산액·자원 판매율을 바꾸면 환산율이 따라 바뀐다. 손으로 정한 값은 아래 KNOBS뿐이고 각각 이유를 적었다.
  2. breakdown(d): 값어치 = Σ(효과 한 번의 값 × 적용 횟수 × 신뢰도) — 지속은 남은 턴 수, 건물·소환물은 생존율, 적을 겨냥하면 사거리 신뢰도, 반응(trig)은 사건이 스테이지에 일어날 기대 횟수와 횟수 제한, 증폭(buff)은 증폭 대상의 스테이지 흐름 × 퍼센트 × 기간.
  3. mana_for(d): 값어치 ÷ VPM(마나 1당 표준 가치) → 마나. 마나로 못 갚는 몫은 shortfall()로 보고만 한다(재료·골드·칸 제한으로 갚아야 하는 구슬).
  4. 이상치 보고서·회귀 시험: proto/value_report.py, proto/tests/value_check.py.
숫자는 모두 임시(프로토타입). 단 '표준선'은 한 곳(VPM)에서 나온다."""
import math, types
import engine

# ---- 손으로 정한 노브(그 외는 전부 엔진 상수에서 계산) -------------------------------------------------------------------------------------------------------------------------
KNOBS = dict(
    MARGIN=1.2,        # 표준선: 정산액을 막 넘기는 것보다 20% 여유 있게 벌 수 있어야 '표준' 주머니
    SAFETY=.25,        # 체력 1을 잃는 값: 쓰러지면 그 스테이지 골드를 몰수당하므로, 정산액의 25%를 체력 전체에 매긴다
    KILL_TURNS=3,      # 적 하나를 일찍 죽이면 그 적이 평균 몇 턴 덜 때리는가
    PROC_SHARE=.25,    # 모은 자원 중 가공 건물로 가는 몫(나머지는 스테이지 끝에 SALE_RATE로 팔림)
    REMAIN=11,         # 지속·건물을 놓는 시점의 평균 남은 턴(15턴 중 평균 4턴째에 씀)
    SURV_B=.85, SURV_S=.7,    # 건물·소환물이 스테이지 끝까지 살아 있을 비율
    REL_CAST_NOW=.85, REL_CAST_AUTO=.6,     # 적이 사거리 안에 있을 확률: 즉발은 플레이어가 때를 고르므로 높다 / 자동 지속은 낮다
    REL_UNIT={1: .3, 2: .5},      # 건물·소환물 사거리별 교전 시간 비율
    NT={"single": 1, "line": 1.7, "around": 2.2, "wide": 3.0},     # 한 번에 맞히는 기대 적 수(동시에 나타나는 무리 크기로 제한)
    REL_DEFENSE=.5,    # 방어·회복이 실제로 쓰이는 비율(플레이어가 맞는 일은 드물다)
    NICHE=.5,          # 짝(화상 부여자·채집 구슬·방어 구슬·건물)이 있어야 의미 있는 증폭은 흐름을 이만큼만 친다
    RUN_LIFE=2.0,      # 런·영구 지속 시전은 스테이지를 넘어 계속 일한다(런 구조, 2026-11-09): 이번 스테이지 값 × 이만큼. 뒤 스테이지일수록 정산액이 1.4배씩 커져 같은 골드의 무게가 줄므로 남은 스테이지 수가 아니라 할인 합(≈2)
    FATE_USED_UP=.75,  # 1회용(쓰면 주머니에서 영구히 빠짐)은 값을 깎는다
    EVENT_SHARE={"attack": .30, "eco": .30, "plant": .06, "build": .12, "summon": .08, "defense": .10},     # 구슬 사용 중 각 태그 비율(시작 주머니 구성 기준)
)

def econ(cfg=None, lvl=None):
    """환산율. 모든 값은 '골드'가 단위."""
    c = dict(engine.CFG); c.update(cfg or {}); K = KNOBS; lvl = lvl or c["lvl"]
    E = types.SimpleNamespace(cfg=c, K=K)
    E.ehp = (14 + 8 * lvl) * c["ehp"]; E.eatk = (3 + 2 * lvl) * c["eatk"]; E.bounty = c["bounty0"] + c["bountyk"] * lvl
    E.n_en = sum(engine.WAVES.values()) * (sum(t["enemy"] for t in engine.STAGE_TYPES.values()) / len(engine.STAGE_TYPES))      # 스테이지당 평균 적 수
    E.hp_g = c["due"] * K["SAFETY"] / c["hp"]                                   # 체력 1의 값
    E.kill = E.bounty + E.eatk * K["KILL_TURNS"] * E.hp_g                        # 적 하나를 처치하는 값(현상금 + 덜 맞는 체력)
    E.res_g = engine.SALE_RATE * (1 - K["PROC_SHARE"]) + c["process_ratio"] * K["PROC_SHARE"]    # 자원 1의 값(팔거나 가공)
    E.vpm = c["due"] / (c["mana"] * c["turns"]) * K["MARGIN"]                    # 표준선: 마나 1당 값어치. 한 판의 마나 총량(마나×턴)으로 정산액+여유를 번다
    E.remain = K["REMAIN"]
    E.turns = c["turns"]
    E.kill_cap = E.n_en * E.kill * .8                                            # 한 구슬이 스테이지에 낼 수 있는 처치 가치의 상한(적 수 한계)
    E.supply_b = 1.5 * c["tile_amt"]; E.supply_c = 2.5 * c["tile_amt"]           # 건물(1칸)·시전(3칸) 주변에서 거둘 수 있는 자원 총량
    # 사건이 남은 기간에 일어날 기대 횟수(반응 구슬의 신뢰도). 구슬 사용은 마나로, 처치는 적 수로, 수확·피격은 대략으로.
    plays = c["mana"] * E.remain / 2.0                                           # 평균 마나 2짜리를 계속 쓴다고 보고 남은 기간의 구슬 사용 수
    ev = {"orb": plays}
    for t, sh in K["EVENT_SHARE"].items(): ev["orb_" + t] = plays * sh
    ev.update(kill=E.n_en * E.remain / E.turns * .8, harvest=2 * E.remain, hit=E.remain / 2.5, death=1.5, approach=E.remain * .5)
    E.events = ev
    E.flow = {"dmg": E.kill_cap, "burn": E.kill_cap * .25, "income": c["due"] * .8, "growth": 30 * E.res_g, "defense": E.hp_g * 40, "unit": c["due"] * .4, "bounty": E.n_en * E.bounty * .8}      # 증폭 대상의 스테이지 흐름(골드)
    E.death_save = c["due"] * .1                                                  # 죽음에서 돌아오는 보험: 쓰러질 확률 10% × 몰수되는 골드
    return E
E0 = econ()

BAG_V = ("draw", "recycle", "trash", "peek", "tempo", "energy", "amplify")
def _g(d, k, default=None): return d[k] if isinstance(d, dict) else getattr(d, k, default)

def plays_to_kill(m, hp):
    """적 하나(체력 hp)를 피해 m짜리로 죽이는 데 드는 **사용 횟수**(죽이는 데 마나가 얼마나 드는가의 기준). 한 방에 죽이면 1. 못 죽이면 '올림'(그 구슬만 쓸 때)과 '체력/피해 + 0.5'(마지막 타격의 낭비를 반쯤 인정, 다른 구슬이 마무리할 때) 중 작은 쪽
    — 한 방 경계(m = hp)에서 값이 끊기지 않고 이어진다. 효과 한 번의 처치 가치 = 처치 값 ÷ 이 횟수(한 번에 죽이고 남는 피해는 낭비라 값이 더 안 늘어난다)."""
    r = hp / max(m, 1e-9); return max(1.0, min(math.ceil(r), r + .5))
def unit_value(v, m, mt, d, E, repeat=False):
    """효과 한 번(한 번의 적용)의 값. (값, 적을 겨냥하는가). repeat=True: 같은 적에게 되풀이해 거는 지속·건물 효과 — 약화·제어는 쌓이지 않고 갱신되므로 적용 한 번이 '한 턴 분'이다."""
    nt = E.K["NT"][_g(d, "rng", "single")]; pe = _g(d, "pe", 1.0)
    if v in ("damage", "drain"):
        x = nt * E.kill / plays_to_kill(m, E.ehp) + (E.hp_g * .6 * (m // 2) if v == "drain" else 0); return x, True
    if v == "burn": return nt * E.kill / plays_to_kill(engine.BURN_DMG * m * (m + 1) / 2, E.ehp), True
    if v == "debuff": return nt * ((1 if repeat else 3) * min(3, E.eatk) * E.hp_g + E.kill * (.03 if repeat else .1)), True
    if v == "control":
        n = 1 if (repeat or _g(d, "life", "instant") in ("stage", "run", "forever")) else 1 + int(_g(d, "B", 10) // 30); return nt * n * (E.eatk * E.hp_g + E.kill * (.03 if repeat else .1)), True
    if v == "guard": return m * E.hp_g * .8, False
    if v == "heal": return m * E.hp_g * .6, False
    if v == "money": return m * 1.0, False
    if v == "steal": return m * .7, False                                           # 적이 있을 때만 들어온다
    if v in ("harvest", "grow"): return (m * 1.0 if mt == "gold" else m * E.res_g * (1.2 if _g(d, "role") == "build" else 1.0)), False
    if v == "process": return m * max(0, E.cfg["process_ratio"] - E.res_g) * .7, False
    if v == "create": return (2.0 if mt == "gold" else 2 * E.res_g if mt else E.hp_g * 15 * .5), False
    if v == "buff": return 0.0, False                                                # 증폭은 별도(흐름 기반)
    if v == "draw": return (1 + int(pe // 2.5)) * E.vpm * .6, False
    if v == "recycle": return E.vpm * .55, False
    if v == "trash": return E.vpm * .25, False
    if v == "peek": return E.vpm * .15, False
    if v == "tempo": return E.vpm * .8, False
    if v == "energy": return max(1, int(pe // 1.5)) * E.vpm * .8, False
    if v == "amplify": return E.vpm * 1.5, False                                    # 다음 구슬 ×2 ≈ 평균 구슬 한 번(마나 2)의 값 × 짝이 있을 확률
    if v == "move": return E.vpm * .5, False
    return 0.0, False                                                                # remove·transform(미구현)

def buff_value(m, mt, d, E):
    """종류별 증폭: 퍼센트 × 대상 흐름 × 지속 기간 비율(× 짝이 필요한 종류는 NICHE)."""
    life = _g(d, "life", "instant"); frac = {"instant": 3, "turns": 4}.get(life, E.remain) / E.turns
    niche = E.K["NICHE"] if mt in ("burn", "growth", "defense", "unit") else 1.0
    return min(m, engine.MULT_CAP * 100) / 100 * E.flow.get(mt or "dmg", E.flow["dmg"]) * min(1.0, frac) * niche

def breakdown(d, E=None):
    """구슬(dict)의 값어치 분해. 돌려주는 dict: total(골드 환산), parts, n(적용 횟수), rel(신뢰도), fires(반응이면 기대 발동), cost(건물 짓는 비용 값), notes"""
    E = E or E0; K = E.K; role = _g(d, "role"); life = _g(d, "life"); trig = _g(d, "trig", "none"); timing = _g(d, "timing", "now"); fate = _g(d, "fate", "returns")
    pay = [tuple(p) for p in _g(d, "payload")]; notes = []
    if role == "summon" and _g(d, "hostile"):          # 적대 웨이브: 적 2마리를 일부러 불러 현상금 일부를 번다(위험은 값에서 뺌)
        fb = max(1, round(E.bounty * E.cfg["farm_bounty"])); return dict(total=max(.5, 2 * fb - E.eatk * E.hp_g), parts=[("적대 웨이브", 2 * fb)], n=1, rel=1, fires=None, cost=0, notes=["적대 소환"])
    if fate == "passive": return dict(total=0.0, parts=[], n=0, rel=0, fires=None, cost=0, notes=["주머니에 있으면 자동(가격 무관)"])
    # 적용 횟수 n
    if role == "move": n = 1; surv = 1.0
    elif role == "build": n = E.remain - (E.cfg["grow_turns"] if engine.is_plant(d) else 0); surv = K["SURV_B"]
    elif role == "summon": n = E.remain; surv = K["SURV_S"]
    elif life == "instant": n = 1; surv = 1.0
    elif life == "turns": n = 4; surv = 1.0
    else: n = (1 + E.remain) * (K["RUN_LIFE"] if life in ("run", "forever") else 1); surv = 1.0
    if role == "cast" and life != "instant" and pay and all(p[0] in BAG_V for p in pay): n = 4          # 주머니 조작 지속은 충전 3번(+즉시 1번)
    if timing == "delayed" and role == "cast": n, notes = 1, notes + ["지연 ×.9"]
    fires = None
    if trig != "none":
        ev = E.events.get(trig, E.remain)
        if role in ("build", "summon"): cap = engine.TRIG_PER_TURN * n
        else: cap = min(engine.trig_uses(d), engine.TRIG_PER_TURN * E.remain)      # 횟수 제한과 턴당 제한 중 작은 쪽
        if trig == "approach": fires = min(cap, E.remain * .5, 3 if role in ("build", "summon") else cap)
        elif trig == "death" and role == "cast": fires = 0.1 * min(cap, 3)      # 플레이어가 쓰러질 때 부활(확률 10%)
        else: fires = min(cap, ev * (surv if role in ("build", "summon") else 1.0))
        n = fires
        notes.append(f"반응 {trig}: 기대 {fires:.1f}회")
    parts = []; total = 0.0; atk_sum = 0.0
    for v, m, mt in pay:
        if v == "buff": val = buff_value(m, mt, d, E); parts.append((f"buff:{mt}", val)); total += val; continue
        x, attack = unit_value(v, m, mt, d, E, repeat=(n > 1 and role != "move"))
        if role in ("build", "summon") and not _g(d, "hostile"): rel = K["REL_UNIT"].get(engine.unit_range(d) if isinstance(d, dict) else 2, .5) if attack else 1.0
        elif role == "cast": rel = (K["REL_CAST_NOW"] if (life == "instant" and timing != "delayed" and trig == "none") else K["REL_CAST_AUTO"]) if attack else 1.0
        else: rel = 1.0
        if v in ("guard", "heal"): rel = K["REL_DEFENSE"]          # 방어막·회복은 실제로 맞았을 때만 쓸모가 있다
        val = x * n * rel * surv
        if v in ("damage", "drain", "burn", "debuff", "control"): val = min(val, E.kill_cap); atk_sum += val
        if v in ("guard", "heal"): val = min(val, E.flow["defense"])
        if v in ("harvest", "grow") and mt in ("wood", "ore", "food"): val = min(val, (E.supply_b if role == "build" else E.supply_c) * E.res_g)
        parts.append((v, val)); total += val
    if atk_sum > E.kill_cap: total -= atk_sum - E.kill_cap; notes.append("공격 동사 합산 상한")      # 공격 동사가 여럿이어도 한 스테이지에 낼 수 있는 처치 가치는 하나
    mod = _g(d, "mod")
    if mod == "scaling": total *= 1.2
    elif mod == "network": total *= 1.3
    elif mod == "risky": total -= sum(max(1, p[1] // 4) for p in pay) * n * E.hp_g
    if timing == "delayed" and role == "cast": total *= .9
    if trig == "death" and role == "cast": total += E.death_save * 1.0; parts.append(("죽음 보험", E.death_save))
    if fate == "used_up": total *= K["FATE_USED_UP"]; notes.append("1회용 ×.75")
    cost = 0.0
    bc = _g(d, "bcost")
    if role in ("build", "summon") and bc and not _g(d, "hostile"): mt_, x_, y_ = bc; cost = (x_ + y_) if mt_ == "gold" else x_ * E.res_g + y_
    return dict(total=max(0.0, total), parts=parts, n=n, rel=None, fires=fires, cost=cost, notes=notes)

def net_value(d, E=None):
    """마나로 갚아야 하는 값어치 = 값어치 − 건물을 지을 때 내는 재료·골드(그쪽으로 이미 갚음)"""
    b = breakdown(d, E); return max(0.0, b["total"] - b["cost"])

MAX_MANA = 8
PAYBACK_STD, PAYBACK_MAX = 3.0, 4.0        # 슬롯형 구슬이 가격(마나+재료·골드)의 몇 배를 버는가: 표준 3배. 4배를 넘으면 모자란 만큼 재료·골드를 더 받는다(enforce_cost)
def is_slot(d):
    """슬롯형: 한 번 놓으면 오래 일하고 칸(건물·소환물) 또는 '스테이지에 한 번'(지속 시전, 소멸)으로 규제되는 구슬. 마나만으로 값어치를 다 매길 수 없다(마나 최대 6)."""
    r = _g(d, "role"); return (r in ("build", "summon") and not _g(d, "hostile")) or engine.sustained(d)
def mana_curve(P):
    """놀이형: P = 값어치/VPM(마나 환산). 4까지는 1:1, 넘으면 로그로 눌린다(마나 최대 8)."""
    return P if P <= 4 else 4 + 1.5 * math.log2(P / 4)
def mana_for(d, E=None):
    E = E or E0; V = net_value(d, E)
    if is_slot(d): m = .9 + .8 * math.log2(1 + V / (2 * E.vpm))          # 슬롯형: 배치 비용. 나머지는 칸 제한·재료·골드가 규제(회수 배율로 점검)
    else: m = mana_curve(V / E.vpm)
    return max(1, min(MAX_MANA, round(m)))
def payback(d, E=None):
    """슬롯형: 값어치 ÷ 가격(마나×VPM + 건물비용). 놀이형: 값어치 ÷ (마나×VPM) — 같은 식. 1이면 본전, 표준은 슬롯형 3 / 놀이형 1."""
    E = E or E0; b = breakdown(d, E); return b["total"] / (max(1, _g(d, "mana", 1)) * E.vpm + b["cost"])
def ratio(d, E=None):
    """표준선 대비 배율. 놀이형은 payback 그대로(표준 1.0), 슬롯형은 표준(PAYBACK_STD)으로 나눈다. 1.0 근처가 표준, 크면 싸고 작으면 비싸다."""
    return payback(d, E) / (PAYBACK_STD if is_slot(d) else 1.0)
def verdict(d, E=None, lo=.6, hi=1.6):
    r = ratio(d, E); return "싸다(약한 가격)" if r > hi else ("최소 가격" if _g(d, "mana", 1) <= 1 else "비싸다") if r < lo else "표준"      # 마나 1 미만으로는 못 내리므로 1마나인 구슬은 비싸다고 하지 않음
def shortfall(d, E=None):
    """마나로 못 갚은 값어치(골드 환산, 놀이형만). 0이면 마나 가격이 값어치를 다 반영. 크면 재료·골드·칸 제한 같은 다른 대가가 필요한 구슬."""
    E = E or E0
    if is_slot(d): return 0.0
    P = net_value(d, E) / E.vpm; paid = min(MAX_MANA, max(1, round(mana_curve(P)))); return max(0.0, (P - paid) * E.vpm)

def enforce_cost(d, E=None):
    """슬롯형 건물·소환물이 가격(마나×VPM + 재료·골드)의 PAYBACK_MAX배를 넘게 벌면, 모자란 몫을 **재료(70%)와 골드(30%)**로 더 받는다. 마나는 건드리지 않고 비용은 올리기만 한다.
    마나로는 값어치를 다 못 치르는 구슬(마나 최대 6)을 재료로 갚게 하는 규칙. 돌려주는 값: 올렸으면 True."""
    E = E or E0
    if _g(d, "role") not in ("build", "summon") or _g(d, "hostile"): return False
    b = breakdown(d, E); need = b["total"] / PAYBACK_MAX; price = max(1, _g(d, "mana", 1)) * E.vpm + b["cost"]
    if price >= need - 1e-9: return False
    R = need - price; bc = list(_g(d, "bcost") or [(_g(d, "mat") if _g(d, "mat") in engine.RAW else "wood"), 0, 0])
    if bc[0] == "gold": bc[1] += math.ceil(R)
    else: bc[1] += math.ceil(R * .7 / E.res_g); bc[2] += math.ceil(R * .3)
    d["bcost"] = bc; return True

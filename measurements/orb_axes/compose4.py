"""Composer fixes only (no axis change): (a) integer scale x5 so long/wide effects don't all collapse to 1, (b) state verbs say the duration once and long hard-CC becomes slow,
(c) delayed => one-shot after the delay, (d) build wording for delayed/trigger/plants, (e) passive orbs drop duration, (f) ambiguous names fall back to a plain cast with one verb."""
import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import compose3 as C
from compose3 import V3, V2, mp, best, T, N, CD, CR, RM, RES, UNIT, SIDE, STATE_V, SELF_V, LIFE_TXT, COND, MOD, select_verbs, lifetime, A
def compose4(name, grade="깨끗한"):
    r, r2 = V3[name], V2.get(name)
    pw = st.mean(a["power"]["score"] for a in r); vs = select_verbs(r); p1 = vs[0][1]
    amb = p1 < .4; pe = pw * (1.0 if p1 >= .5 else .85 if p1 >= .4 else .6)
    if amb: vs = vs[:1]
    role, timing, trig, rng, mat = (best(r, k) for k in ("role", "timing", "trigger", "range", "material"))
    if amb: role, trig = "cast", "none"
    if mp(r, "trigger", trig) < .5: trig = "none"
    L = lifetime(r, role, pe, grade); fate = best(r, "bagfate2") if mp(r, "bagfate2", best(r, "bagfate2")) >= .5 else "returns"
    if timing == "delayed" and role == "cast" and L in ("turns", "stage"): L = "instant"         # (c)
    if fate == "passive": L = "run" if L == "instant" else L                                         # (e)
    B = 5 * (1 + 2 * pe); rl = RES.get(mat)
    def mag(share):
        if role in ("build", "summon"): v = B * .3 * RM[rng]
        elif L == "instant": v = B * RM[rng]
        else: v = B * T[L] / N[L] * RM[rng]
        return max(1, round(v * share))
    def eff(v, share):
        m = mag(share); half = max(1, m // 2); side = SIDE.get(v, ""); tgt = ""
        if v not in SELF_V: tgt = {"single": f"{side} 1", "line": f"직선 3칸의 {side}", "around": f"주변 1칸의 {side}", "wide": f"맵 전체의 {side}"}[rng]
        instant_res = role == "cast" and v in ("harvest", "grow", "money", "create")
        if instant_res: m = max(1, m // 2)
        long = L in ("stage", "run", "forever") and role == "cast"
        d = {"damage": f"{tgt}에 피해 {m}", "guard": f"{tgt}에 방어막 {m}", "heal": f"{tgt} 체력 {m} 회복", "money": f"골드 {m} 획득",
             "harvest": f"{rl or '자원'} {m} 채집", "grow": f"{tgt}의 식물 {m} 성장" + (f" → {rl} 생산" if rl else ""),
             "buff": f"{tgt} 공격 +{half}", "debuff": f"{tgt} 공격 -{half}",
             "control": (f"{tgt} 이동 -{max(1, m // 5)} (둔화)" if long else f"{tgt} 행동 불가 {1 + int(B // 30)}턴"),
             "remove": f"{tgt}의 효과 1개 제거", "transform": f"{tgt} 1개를 다른 것으로 변환", "draw": f"구슬 {1 + int(pe // 2.5)}개 더 뽑기",
             "recycle": "버린 구슬 1개를 주머니로 되돌림", "trash": "주머니의 구슬 1개 영구 폐기", "peek": f"주머니 위 {2 + int(pe // 2)}개 확인",
             "tempo": "이번 턴 행동 +1", "energy": f"마나 +{max(1, int(pe // 1.5))}", "create": (f"{rl} 아이템 1개 생성" if rl else "1회용 아이템 1개 생성"),
             "steal": f"{tgt}에게서 골드 {m} 탈취", "amplify": "다음 구슬 효과 ×2"}[v]
        return d, v in STATE_V
    parts = [eff(v, s) for (v, _), s in zip(vs, (1, .7, .5))]; body = "; ".join(p[0] for p in parts)
    allstate = all(p[1] for p in parts)
    if role in ("cast", "move"):
        if fate == "passive": body = f"주머니에 있는 동안 {'' if allstate else '매 턴 '}{body}"
        elif L != "instant": body = f"{LIFE_TXT[L]} {'' if allstate else '매 턴 '}{body}"
        if timing == "delayed": body = f"{1 + int(pe // 2)}턴 뒤: {body}"
        elif timing == "repeating" and L == "instant": body = f"매 턴: {body}"
        if trig != "none": body = f"{COND[trig]} 발동 — {body}"
    cm = max(1, round(.5 * pe * CD[L] * CR[rng])) + len(vs) - 1; cost = f"마나 {cm}"
    if role == "build":
        x = max(1, round(B * .5 / 5)); y = max(1, round(B * .4 / 5)); cost += f" + {rl or '나무'} {x} + 골드 {y}"
        kind = "식물" if any(v == "grow" for v, _ in vs) else "건물"
        when = f"설치 {1 + int(pe // 2)}턴 뒤부터 " if timing == "delayed" else ""
        cond = f"{COND[trig]} 1회 발동 — " if trig != "none" else "매 턴 "
        text = f"{kind}(체력 {round(B)}) 설치, {LIFE_TXT[L] or '이번 런 동안'} 유지 — {when}{cond}{body}"
    elif role == "summon":
        u = UNIT.get((r2 and best(r2, "unit")) or "soldier", "병사"); hostile = bool(r2) and best(r2, "allegiance") == "hostile"
        if hostile:
            lv = 1 + int(pe // 1.5); text = f"적대 {u} 웨이브 Lv{lv} 소환 (처치 시 골드 {lv * 2})"
        else: text = f"{u}(체력 {round(B)}) 소환, 스테이지 동안 — 매 턴 {body}"
    elif role == "move": text = f"{2 + int(pe)}칸 이동 후 {body}"
    else: text = body
    mods = sorted(((st.mean(a[m]["noul"] for a in r), m) for m in A.MODS), reverse=True)
    if mods[0][0] >= .6 and not amb: text += f" ＋ {MOD[mods[0][1]]}"
    if fate == "used_up": text += " ［1회용］"
    return {"name": name, "text": text.replace("  ", " ").strip(), "cost": cost, "amb": amb}
if __name__ == "__main__":
    cmp = ["영구빙결", "절대영도", "무적", "시한폭탄", "맹독치유", "폭우", "가뭄", "씨앗", "함정", "뽁뽁이", "혜자", "윤회", "방패", "성벽", "우로보로스", "데미지반사", "야영지", "텃밭"]
    out = ["# 조합 시험 v3b — 문구 틀만 고친 뒤", "", "고친 것: ①수치 단위 ×5(긴·넓은 효과가 전부 1로 뭉치지 않게) ②상태 효과는 지속을 한 번만 쓰고 길면 행동 불가 대신 둔화 ③'지연'은 N턴 뒤 한 번 ④건물 문구(지연·트리거·식물) ⑤자동 구슬은 지속 생략 ⑥애매한 이름은 시전 + 동사 1개로 후퇴", "",
           "| 이름 | 고치기 전 | 고친 뒤 |", "|---|---|---|"]
    for n in cmp:
        a = C.compose(n); b = compose4(n); out.append(f"| {n} | {a['text']} ({a['cost']}) | {b['text']} ({b['cost']}) |")
    allb = [compose4(n) for n in C.V3]; L = [len(c["text"]) for c in allb]
    out += ["", f"전체 339개 문구 길이: 평균 {st.mean(L):.0f}, 중앙 {st.median(L):.0f}, 최대 {max(L)}"]
    open("COMPOSE_v3b.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))
    json.dump(allb, open("compose_v3b_all.json", "w", encoding="utf-8"), ensure_ascii=False)

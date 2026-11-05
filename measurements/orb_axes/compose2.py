"""Composition v2: same measured data, but (1) the 2nd/3rd verb needs an absolute floor 0.2 (ambiguous names have flat distributions and used to get MORE verbs),
(2) target side is DERIVED from the verb (not asked), (3) build implies 'stays', (4) range 'self' is lifted to 'one' for verbs that need a target."""
import sys, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import compose as C
from compose import rows, mp, best, A, effect, MOD
SIDE_OF = {**{v: "적" for v in ("damage", "debuff", "control", "steal")}, **{v: "아군" for v in ("guard", "heal", "buff", "remove")},
           **{v: "땅" for v in ("harvest", "grow", "transform")}}
SELF_ONLY = {"money", "draw", "recycle", "trash", "peek", "tempo", "energy", "create", "amplify"}
def phrase(v, rng, ff):
    if v in SELF_ONLY: return ""
    s = "전원(아군 포함)" if ff else SIDE_OF[v]
    return {"self": "자신", "one": f"{s} 1", "line": f"직선 3칸의 {s}", "around": f"주변 1칸의 {s}", "wide": f"맵 전체의 {s}"}[rng if rng != "self" or v in ("guard", "heal", "buff", "remove") else "one"]
def compose2(key):
    r = rows[key]; pw = st.mean(a["power"]["score"] for a in r)
    vs = C.select_verbs(r, rel=.4, floor=.2); p1 = vs[0][1]
    f = 1.0 if p1 >= .5 else .85 if p1 >= .4 else .6; pe = pw * f
    n = max(1, round(1 + pe * 2)); mana = max(1, round(pe * 1.2)) + (len(vs) - 1)
    role, timing, rng, persist = (best(r, k) for k in ("role", "timing", "range", "persist"))
    ff = best(r, "side") == "all" and mp(r, "side", "all") >= .5
    if role == "build": persist = "stays"
    parts = []
    for (v, _), w in zip(vs, (1, .7, .5)):
        ph = phrase(v, rng, ff and v in ("damage", "debuff", "control"))
        parts.append(effect(v, max(1, round(n * w)), ph, pe).replace("에서 ", "에서 ") if ph else effect(v, max(1, round(n * w)), "", pe))
    eff = "; ".join(parts)
    t = {"build": f"건물(체력 {n}) 설치 — 매 턴 {eff}", "instant": eff, "lasting": f"{1 + int(pe // 2) + 1}턴 동안 매 턴 {eff}",
         "summon": f"소환(체력 {n}) — 매 턴 {eff}", "move": f"{2 + int(pe)}칸 이동 후 {eff}"}[role]
    if timing == "delayed": t = f"{1 + int(pe // 2)}턴 뒤: {t}"
    if timing == "trigger": t = f"함정(적이 닿으면 발동): {t}"
    mv, mm = max((st.mean(a[m]["noul"] for a in r), m) for m in A.MODS)
    if mv >= .6: t += f" ＋ {MOD[mm]}"
    t += {"used_up": " ［1회용］", "returns": " ［복귀］", "stays": " ［맵에 남음］", "passive": " ［주머니에 있으면 자동］"}[persist]
    return t, mana, pw, pe, p1, len(vs)
if __name__ == "__main__":
    allrows = {k.split("|", 1)[1]: k for k in rows}
    cmp = ["병사", "억까", "특이점", "궁니르", "뜨거운얼음", "박스테이프", "뽁뽁이", "혜자", "흡혈", "자동부활", "영구빙결", "절대영도", "맵전체타격", "시한폭탄", "레고블록", "도박", "방패", "맹독치유"]
    out = ["# 조합 시험 v2 (규칙 보정 뒤) — 같은 측정값, 새 호출 없음", "", "보정: ①2·3번째 동사는 확률 0.2 이상일 때만 ②대상(적/아군/땅)은 동사에서 정함 ③건물은 맵에 남음 ④자신 범위인데 적을 대상으로 하는 동사는 대상 1로.", "",
           "| 이름 | 보정 전 | 보정 후 |", "|---|---|---|"]
    for n in cmp:
        a = C.compose(allrows[n])[0]; b = compose2(allrows[n])[0]
        out.append(f"| {n} | {a} | {b} |")
    # verb count effect on ambiguous names
    pool = [k for k in rows if not k.startswith("기존56|")]
    for lab, fl in (("0.1", .1), ("0.2", .2)):
        amb = [len(C.select_verbs(rows[k], floor=fl)) for k in pool if max(mp(rows[k], "verb", o) for o in C.V) < .4]
        clr = [len(C.select_verbs(rows[k], floor=fl)) for k in pool if max(mp(rows[k], "verb", o) for o in C.V) >= .5]
        out.append(f"\n바닥 {lab}: 애매한 이름 평균 동사 {st.mean(amb):.2f}개, 분명한 이름 {st.mean(clr):.2f}개")
    open("COMPOSE_v2.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

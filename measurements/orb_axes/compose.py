"""Compose readable orb effects from the measured axes (no new Jev calls). Numbers/templates are PLACEHOLDERS to judge the axes, not balance."""
import sys, json, collections, statistics as st, math
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v1 as A
rows = collections.defaultdict(list)
for l in open("out_v1.jsonl", encoding="utf-8"):
    r = json.loads(l); rows[r["id"]].append(r["answers"])
mp = lambda r, k, o: st.mean(a[k]["probabilities"][o] for a in r)
best = lambda r, k: max(A.CHOICES[k][1], key=lambda o: mp(r, k, o))
V = list(A.VERBS)

def select_verbs(r, rel=.4, floor=.1, cap=3):
    p = {o: mp(r, "verb", o) for o in V}; rk = sorted(p, key=lambda o: -p[o])
    return [(o, p[o]) for i, o in enumerate(rk[:cap]) if i == 0 or p[o] >= max(rel * p[rk[0]], floor)]

RANGE = {"self": "자신", "one": "대상 1", "line": "직선 3칸", "around": "주변 1칸", "wide": "맵 전체"}
SIDE = {"ally": "아군", "enemy": "적", "land": "땅·자원", "all": "범위 내 전원(아군 포함)"}
def effect(v, n, tgt, pe):
    t = max(1, 1 + int(pe // 2)); d = max(1, 1 + int(pe // 2.5))
    return {"damage": f"{tgt}에 피해 {n}", "guard": f"{tgt}에 방어막 {n}", "heal": f"{tgt} 체력 {n} 회복",
            "money": f"골드 {n} 획득", "harvest": f"{tgt}의 자원 {n} 채집", "grow": f"{tgt}의 작물·식물 {n} 성장",
            "buff": f"{tgt} 공격·이동 +{max(1,n//2)}", "debuff": f"{tgt} 약화 -{max(1,n//2)}", "control": f"{tgt} 행동 불가 {t}턴",
            "remove": f"{tgt}의 효과 1개 제거", "transform": f"{tgt} 1개를 다른 것으로 변환", "draw": f"구슬 {d}개 더 뽑기",
            "recycle": "버린 구슬 1개를 주머니로 되돌림", "trash": "주머니의 구슬 1개를 영구 폐기", "peek": f"주머니 위 {d+1}개 확인",
            "tempo": "이번 턴 행동 +1", "energy": f"마나 +{d}", "create": "1회용 아이템 1개 생성",
            "steal": f"{tgt}에게서 골드 {n} 탈취", "amplify": "다음 구슬 효과 ×2"}[v]

MOD = {"scaling": "사용할 때마다 +1 성장", "risky": "위험: 사용자도 피해", "random": "효과 50~150% 무작위",
       "network": "인접한 구슬·건물마다 +1", "conditional": "조건부(조건 미정)"}

def compose(key, penalty=True):
    r = rows[key]; pw = st.mean(a["power"]["score"] for a in r)
    vs = select_verbs(r); p1 = vs[0][1]
    f = 1.0 if p1 >= .5 else .85 if p1 >= .4 else .6                      # ambiguous names lose power (director's choice a)
    pe = pw * (f if penalty else 1)
    n = max(1, round(1 + pe * 2)); mana = max(1, round(pe * 1.2)) + (len(vs) - 1)
    role, timing, rng, side, persist = (best(r, k) for k in ("role", "timing", "range", "side", "persist"))
    conflicts = []
    if rng == "self" and side != "ally": conflicts.append(f"범위=자신인데 대상={side}")
    if role == "build" and persist != "stays": conflicts.append(f"건물인데 지속={persist}")
    if persist == "stays" and role in ("instant", "move"): conflicts.append(f"{role}인데 맵에 남음")
    tgt = RANGE[rng] if rng == "self" else f"{RANGE[rng]}의 {SIDE[side]}"
    eff = "; ".join(effect(v, max(1, round(n * w)), tgt, pe) for v, w in zip([x[0] for x in vs], (1, .7, .5)))
    t = {"build": f"건물(체력 {n}) 설치 — 매 턴 {eff}", "instant": eff, "lasting": f"{1 + int(pe // 2) + 1}턴 동안 매 턴 {eff}",
         "summon": f"소환(체력 {n}) — 매 턴 {eff}", "move": f"{2 + int(pe)}칸 이동 후 {eff}"}[role]
    if timing == "delayed": t = f"{1 + int(pe // 2)}턴 뒤: {t}"
    if timing == "trigger": t = f"함정(적이 닿으면 발동): {t}"
    mods = [(st.mean(a[m]["noul"] for a in r), m) for m in A.MODS]; mv, mm = max(mods)
    if mv >= .6: t += f" ＋ {MOD[mm]}"
    t += {"used_up": " ［1회용］", "returns": " ［사용 후 주머니 복귀］", "stays": " ［맵에 남음］", "passive": " ［주머니에 있으면 자동］"}[persist]
    return t, mana, pw, pe, p1, conflicts

if __name__ == "__main__":
    PICK = ["영구빙결","무적","자원강탈","골드두배","맵전체타격","즉사","흡혈","자동부활","엑스칼리버","우로보로스","지우개","레고블록","돋보기","압정",
            "시한폭탄","자본주의","맹독치유","조용한폭발","데자뷔","망각","무한대발산","윤회","운명의데스티니","오버클럭","절대영도","핵폭탄급방귀",
            "억까","뽁뽁이","혜자","특이점","궁니르","뜨거운얼음","박스테이프","각설탕",
            "씨앗","텃밭","곡괭이","성벽","병사","양봉장","금화 주머니","상인","이자","화염검","방패","도박"]
    allrows = {k.split("|", 1)[1]: k for k in rows}
    out = ["# 조합 시험 — 측정된 축으로 구슬 효과 문구 만들기", "",
           "새 Jev 호출 없음(`out_v1.jsonl` 재사용). **숫자와 문구 틀은 축이 읽히는지 보려는 임시 값**이며 밸런스가 아님. 애매한 이름(동사 1순위 확률 <0.5)은 힘을 깎음(0.4~0.5 ×0.85, 0.4 미만 ×0.6).", "",
           "| 이름 | 만들어진 효과 | 마나 | 힘(원래→깎인) | 비고 |", "|---|---|---|---|---|"]
    for n in PICK:
        t, m, pw, pe, p1, c = compose(allrows[n])
        out.append(f"| {n} | {t} | {m} | {pw:.1f}→{pe:.1f} | {'애매 ' if p1<.4 else ''}{'⚠ ' + ', '.join(c) if c else ''} |")
    # contradiction statistics over all 256 names
    cc = collections.Counter(); tot = 0; names_c = collections.defaultdict(list)
    for k in rows:
        if k.startswith("기존56|") and False: continue
        tot += 1
        for c in compose(k)[5]:
            cc[c.split("인데")[0] if "인데" in c else "범위=자신인데 대상≠아군"] += 1; names_c[c].append(k.split("|", 1)[1])
    anyc = sum(1 for k in rows if compose(k)[5])
    out += ["", f"## 축끼리 모순되는 조합 (256개 이름 중)", f"모순이 하나라도 있는 이름: **{anyc}/{tot} = {anyc/tot:.0%}**", ""]
    for c, ns in sorted(names_c.items(), key=lambda x: -len(x[1]))[:8]: out.append(f"- {c}: {len(ns)}개 (예: {', '.join(ns[:5])})")
    open("COMPOSE_v1.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

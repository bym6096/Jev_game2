"""Compose readable orbs from the v3 axes. NUMBERS ARE PLACEHOLDERS; the point is the structure:
budget B = 1 + 2*power_eff is shared by duration/range/verbs (total-value conservation), cost grows with duration/range,
buildings pay materials+gold and produce per turn (value accumulates, so it is paid back by cost)."""
import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v3 as A
def load(f):
    d = collections.defaultdict(list)
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); d[r["id"].split("|", 1)[1]].append(r["answers"])
    return d
V3, V2 = load("out_v3.jsonl"), load("out_v2.jsonl")
LV = ["instant", "turns", "stage", "run", "forever"]
mp = lambda r, key, o: st.mean(a[key]["probabilities"][o] for a in r)
best = lambda r, key: max(r[0][key]["probabilities"], key=lambda o: mp(r, key, o))
VERBS = list(A.CHOICES["verb"][1])
UNIT = {"soldier": "병사", "worker": "일꾼", "beast": "짐승", "spirit": "정령", "construct": "기계"}
RES = {"wood": "나무", "ore": "광석", "food": "식량", "gold": "골드"}
SIDE = {**{v: "적" for v in ("damage", "debuff", "control", "steal")}, **{v: "아군" for v in ("guard", "heal", "buff", "remove")}, **{v: "땅" for v in ("harvest", "grow", "transform")}}
STATE_V = {"guard", "buff", "debuff", "control"}                       # shown as "during X: ..." instead of "every turn"
SELF_V = {"money", "draw", "recycle", "trash", "peek", "tempo", "energy", "create", "amplify"}
T = {"instant": 1.0, "turns": 1.6, "stage": 2.4, "run": 3.2, "forever": 4.0}; N = {"instant": 1, "turns": 3, "stage": 12, "run": 40, "forever": 100}
CD = {"instant": 1.0, "turns": 1.2, "stage": 1.6, "run": 2.2, "forever": 3.5}; CR = {"single": 1.0, "line": 1.1, "around": 1.3, "wide": 1.6}
RM = {"single": 1.0, "line": .8, "around": .6, "wide": .4}
LIFE_TXT = {"instant": "", "turns": "3턴 동안", "stage": "이번 스테이지 동안", "run": "이번 런 동안", "forever": "영구(프로필에 남음)"}
COND = {"hit": "피격 시", "death": "사망 시", "orb": "다른 구슬을 쓸 때", "approach": "적이 다가오면"}
MOD = {"scaling": "사용할 때마다 +1 성장", "risky": "위험: 사용자도 피해", "random": "효과 50~150% 무작위", "network": "인접한 구슬·건물마다 +1"}

def select_verbs(r, rel=.4, floor=.2, cap=3):
    p = {o: mp(r, "verb", o) for o in VERBS}; rk = sorted(p, key=lambda o: -p[o])
    return [(o, p[o]) for i, o in enumerate(rk[:cap]) if i == 0 or p[o] >= max(rel * p[rk[0]], floor)]

def lifetime(r, role, pe, grade):
    L = max(LV, key=lambda o: mp(r, "lifetime_A", o))
    if L in ("turns", "run") and mp(r, "lifetime_A", "stage") >= .15: L = "stage"
    if role == "build" and L in ("instant", "turns"): L = "run"
    if L == "turns" and pe >= 1.5: L = "stage"
    if L == "forever" and not (grade == "금박" and pe >= 3 and mp(r, "lifetime_A", "forever") >= .7): L = "run"
    return L

def compose(name, grade="깨끗한"):
    r, r2 = V3[name], V2.get(name)
    pw = st.mean(a["power"]["score"] for a in r); vs = select_verbs(r); p1 = vs[0][1]
    pe = pw * (1.0 if p1 >= .5 else .85 if p1 >= .4 else .6)
    role, timing, trig, rng, mat = (best(r, k) for k in ("role", "timing", "trigger", "range", "material"))
    if mp(r, "trigger", trig) < .5: trig = "none"
    L = lifetime(r, role, pe, grade); fate = best(r, "bagfate2") if mp(r, "bagfate2", best(r, "bagfate2")) >= .5 else "returns"
    B = 1 + 2 * pe; rl = RES.get(mat)
    def val(share, state_or_turn):
        if role in ("build", "summon"): v = B * .3 * RM[rng]
        else: v = (B * T[L] / N[L] if state_or_turn else B) * RM[rng]
        return max(1, round(v * share))
    def eff(v, share):
        per_turn = L != "instant" or role in ("build", "summon")
        m = val(share, per_turn); half = max(1, m // 2)
        side = SIDE.get(v, ""); tgt = ""
        if v not in SELF_V:
            tgt = {"single": f"{side} 1", "line": f"직선 3칸의 {side}", "around": f"주변 1칸의 {side}", "wide": f"맵 전체의 {side}"}[rng]
        instant_res = role == "cast" and v in ("harvest", "grow", "money", "create")
        if instant_res: m = max(1, m // 2)
        d = {"damage": f"{tgt}에 피해 {m}", "guard": f"{tgt}에 방어막 {m}", "heal": f"{tgt} 체력 {m} 회복", "money": f"골드 {m} 획득",
             "harvest": f"{rl or '자원'} {m} 채집", "grow": f"{tgt}의 식물 {m} 성장" + (f" → {rl} 생산" if rl else ""),
             "buff": f"{tgt} 공격 +{half}", "debuff": f"{tgt} 공격 -{half}", "control": f"{tgt} 행동 불가 {1 + int(B // 6)}턴",
             "remove": f"{tgt}의 효과 1개 제거", "transform": f"{tgt} 1개를 다른 것으로 변환", "draw": f"구슬 {1 + int(pe // 2.5)}개 더 뽑기",
             "recycle": "버린 구슬 1개를 주머니로 되돌림", "trash": "주머니의 구슬 1개 영구 폐기", "peek": f"주머니 위 {2 + int(pe // 2)}개 확인",
             "tempo": "이번 턴 행동 +1", "energy": f"마나 +{max(1, int(pe // 1.5))}", "create": (f"{rl} 아이템 1개 생성" if rl else "1회용 아이템 1개 생성"),
             "steal": f"{tgt}에게서 골드 {m} 탈취", "amplify": "다음 구슬 효과 ×2"}[v]
        return d, v in STATE_V, instant_res
    parts = [eff(v, s) for (v, _), s in zip(vs, (1, .7, .5))]
    body = "; ".join(p[0] for p in parts); notes = []
    if any(p[2] for p in parts): notes.append("즉시 획득은 효율 낮음(×0.5)")
    # lifetime / timing wrapper
    if role != "build" and role != "summon":
        if L != "instant":
            every = "" if all(p[1] for p in parts) else "매 턴 "
            body = f"{LIFE_TXT[L]} {every}{body}"
    if timing == "delayed": body = f"{1 + int(pe // 2)}턴 뒤: {body}"
    elif timing == "repeating" and L == "instant" and role not in ("build", "summon"): body = f"매 턴: {body}"
    if trig != "none": body = f"{COND[trig]} 발동 — {body}"
    cost_m = max(1, round(.5 * pe * CD[L] * CR[rng])) + len(vs) - 1; cost = f"마나 {cost_m}"
    if role == "build":
        x = max(1, round(B * .5)); y = max(1, round(B * .4)); cost += f" + {rl or '나무'} {x} + 골드 {y}"
        text = f"건물(체력 {max(1, round(B))}) 설치 [{LIFE_TXT[L] or '이번 런 동안'}]: 매 턴 {body}" if True else body
        text = f"건물(체력 {max(1, round(B))}) 설치, {LIFE_TXT[L] or '이번 런 동안'} 유지 — 매 턴 {body}"
    elif role == "summon":
        u = UNIT.get((r2 and best(r2, "unit")) or "soldier", "병사"); hostile = bool(r2) and best(r2, "allegiance") == "hostile"
        if hostile:
            lv = 1 + int(pe // 1.5); text = f"적대 {u} 웨이브 Lv{lv} 소환 (처치 시 골드 {max(1, lv * 2)})"; notes.append("적을 부르는 구슬: 위험 감수 보상형")
        else:
            text = f"{u}(체력 {max(1, round(B))}) 소환, {'이번 스테이지' if L in ('instant', 'turns') else LIFE_TXT[L]} 동안 — 매 턴 {body}"
    elif role == "move":
        text = f"{2 + int(pe)}칸 이동 후 {body}"
    else:
        text = body
    mods = sorted(((st.mean(a[m]["noul"] for a in r), m) for m in A.MODS), reverse=True)
    if mods[0][0] >= .6: text += f" ＋ {MOD[mods[0][1]]}"
    if fate == "used_up": text += " ［1회용］"
    elif fate == "passive": text += " ［주머니에 있으면 자동］"
    return {"name": name, "text": text.replace("  ", " ").strip(), "cost": cost, "role": role, "life": L, "verbs": [v for v, _ in vs], "p1": p1, "pw": pw, "pe": pe, "notes": notes, "fate": fate}

if __name__ == "__main__":
    allnames = list(V3)
    PICK = ["영구빙결", "무적", "자원강탈", "골드두배", "맵전체타격", "즉사", "흡혈", "자동부활", "엑스칼리버", "우로보로스", "지우개", "레고블록", "돋보기", "압정", "시한폭탄", "맹독치유", "조용한폭발", "망각", "윤회",
            "오버클럭", "절대영도", "핵폭탄급방귀", "억까", "뽁뽁이", "혜자", "특이점",
            "씨앗", "텃밭", "곡괭이", "성벽", "병사", "양봉장", "금화 주머니", "상인", "이자", "화염검", "방패", "도박", "폭우", "야영지", "포위전", "가뭄", "통나무", "제재소", "대장간", "오두막", "농부", "늑대", "슬라임", "해골", "천사", "골렘", "도적", "데미지반사", "함정"]
    PICK = [n for n in PICK if n in V3]
    out = ["# 조합 시험 v3 — 새 축으로 구슬 만들기 (숫자는 임시, 구조가 핵심)", "",
           "구조: 예산 B = 1 + 2×힘(애매하면 깎음). 지속이 길수록 **턴당** 효과가 약하고(총량은 조금만 증가), 범위가 넓을수록 **대상당** 효과가 약하며, 둘 다 마나 비용을 올린다. 건물은 재료+골드를 내고 매 턴 생산(누적 가치는 비용으로 회수). 영구는 금박 + 힘 3↑ + 영구 확률 0.7↑. 구슬 즉시 획득은 효율 ×0.5. 표시 등급: 깨끗한.", "",
           "| 이름 | 만들어진 구슬 | 비용 | 메모 |", "|---|---|---|---|"]
    for n in PICK:
        c = compose(n); out.append(f"| {n} | {c['text']} | {c['cost']} | {'애매(힘 깎음) ' if c['p1']<.4 else ''}{' '.join(c['notes'])} |")
    out += ["", "## 영구가 되는 5개 (금박 등급)", "", "| 이름 | 금박 | 깨끗한 |", "|---|---|---|"]
    for n in ["무한지속", "영구기관", "영원", "영구빙결", "불멸"]:
        a, b = compose(n, "금박"), compose(n, "깨끗한"); out.append(f"| {n} | {a['text']} ({a['cost']}) | {b['text']} ({b['cost']}) |")
    # readability stats over all names
    allc = [compose(n) for n in allnames]
    L = [len(c["text"]) for c in allc]
    out += ["", "## 읽기 쉬운가: 전체 339개 통계", f"- 문구 길이(글자): 평균 {st.mean(L):.0f}, 중앙 {st.median(L):.0f}, 100자 초과 {sum(x>100 for x in L)}개, 60자 이하 {sum(x<=60 for x in L)}개",
            f"- 동사 개수: {dict(sorted(collections.Counter(len(c['verbs']) for c in allc).items()))}",
            f"- 지속 기간: {dict(collections.Counter(c['life'] for c in allc).most_common())}",
            f"- 역할: {dict(collections.Counter(c['role'] for c in allc).most_common())}"]
    open("COMPOSE_v3.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))
    json.dump([{k: v for k, v in c.items()} for c in allc], open("compose_v3_all.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

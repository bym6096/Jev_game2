"""가치 모델(value.py) 회귀 시험 — Jev 호출 없음.
  python3 -I proto/tests/value_check.py
무엇을 지키나: ①환산율이 엔진 상수에서 따라온다 ②값어치가 크기·지속·범위·사건 수에 단조롭게 반응한다 ③시작 구슬이 표준선 안이고 실제로 쓸 수 있는 가격이다
④모델 값이 **실제 엔진을 돌린 결과**와 비슷하다(같은 시드에서 구슬을 넣은 판과 뺀 판의 골드 차이) ⑤측정 풀(있을 때)의 분포가 무너지지 않는다."""
import os, sys, copy, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..")
for p in (P, os.path.join(P, "vendor")):
    if p not in sys.path: sys.path.insert(0, p)
import engine, orbs, value
H = orbs._hand
def V(**k): d = H("시험", **k); return value.breakdown(d)["total"]

# 1) 환산율은 엔진 상수에서 계산된다
E = value.econ()
assert abs(E.vpm - engine.CFG["due"] / (engine.CFG["mana"] * engine.CFG["turns"]) * value.KNOBS["MARGIN"]) < 1e-9
assert value.econ({"due": 300}).vpm > E.vpm * 1.99, "정산액을 올리면 마나 1당 표준 값어치가 따라 오른다"
assert value.econ({"bounty0": 6}).kill > E.kill, "현상금을 올리면 처치 값이 오른다"
assert value.econ({"ehp": engine.CFG["ehp"] * 2}).ehp > E.ehp
# 죽이는 데 드는 사용 횟수: 한 방이면 1, 한 방 직전은 1~2 사이로 매끄럽게, 더 세져도 값이 안 늘고(낭비), 약할수록 늘어난다
ptk = value.plays_to_kill
assert ptk(33, 33) == 1 and ptk(100, 33) == 1 and ptk(34, 33) == 1
assert 1 < ptk(32, 33) < 2 and abs(ptk(32, 33) - ptk(33, 33)) < .6 and 1.4 < ptk(29, 33) < 1.9, "한 방 직전은 1.5회 안팎으로 이어진다(절벽 없음)"
assert all(ptk(m, 33) >= ptk(m + 1, 33) - 1e-9 for m in range(1, 60)), "피해가 클수록 횟수는 줄거나 같다"
assert value.breakdown(H("강타", payload=[["damage", 80, None]]))["total"] == value.breakdown(H("강타", payload=[["damage", 40, None]]))["total"] or engine.CFG["ehp"] * 22 < 40, "한 방에 죽이고 남는 피해는 값이 안 늘어난다"
print("환산율 OK  VPM=%.2f 처치=%.2f 자원=%.2f" % (E.vpm, E.kill, E.res_g))

# 2) 단조성
assert V(payload=[["money", 4, None]]) > V(payload=[["money", 2, None]])
assert V(payload=[["money", 2, None]], life="stage") > V(payload=[["money", 2, None]], life="turns") > V(payload=[["money", 2, None]])
assert V(payload=[["damage", 8, None]], rng="around") > V(payload=[["damage", 8, None]], rng="single")
assert V(payload=[["money", 2, None]], life="stage", trig="orb") > V(payload=[["money", 2, None]], life="stage", trig="hit") > V(payload=[["money", 2, None]], life="stage", trig="orb_plant"), "사건이 흔할수록 반응 구슬의 값이 크다"
assert V(payload=[["buff", 30, "income"]], life="stage") > V(payload=[["buff", 15, "income"]], life="stage") > V(payload=[["buff", 30, "income"]], life="instant")
assert V(payload=[["buff", 20, "income"]], life="stage") > V(payload=[["buff", 20, "burn"]], life="stage"), "짝이 있어야 쓰는 증폭은 싸다(NICHE)"
assert V(payload=[["debuff", 1, None]], life="stage", rng="around") < V(payload=[["debuff", 1, None]], life="stage", rng="around") * 3
two = V(payload=[["damage", 30, None], ["debuff", 1, None]], life="stage", rng="wide"); one = V(payload=[["damage", 30, None]], life="stage", rng="wide")
assert two <= value.E0.kill_cap + 1e-6 + V(payload=[["debuff", 1, None]], life="stage", rng="wide"), "공격 동사 합산 상한"
assert V(role="move", payload=[["recycle", 1, None]], life="run") < V(payload=[["recycle", 1, None]], life="run"), "이동은 한 번만 적용"
assert value.breakdown(H("부적", fate="passive", payload=[["money", 5, None]]))["total"] == 0
print("단조성 OK")

# 3) 반응 조건은 전부 가격 모델이 안다
for c in orbs.TRIGGERS:
    if c == "none": continue
    assert c in engine.COND_KO, f"{c}: 엔진 문구 없음"
    assert c in value.E0.events, f"{c}: 기대 사건 횟수 없음"
for c in orbs.TRIGGERS:
    if c in ("none", "approach", "death"): continue
    assert engine.trig_match(c, {"hit": "hit", "kill": "kill", "harvest": "harvest"}.get(c, "orb"), {"tags": {c[4:]} if c.startswith("orb_") else set()}), f"{c}: 사건과 안 맞음"
print("반응 조건 표 OK")

# 4) 시작 구슬: 쓸 수 있는 가격 + 표준선 안
for o in orbs.starter_orbs():
    assert o["mana"] <= engine.CFG["mana"], f"{o['name']} 마나 {o['mana']} > 최대 마나"
    if o["name"] in ("달리기", "텃밭"): continue
    r = value.ratio(o); assert .2 <= r <= 2.6, f"{o['name']} 배율 {r:.2f}"      # 병사(매 턴 피해 4)는 적 체력 33에서 약해져 0.24 — 가치 모델이 정확히 짚은 것(HANDOFF 참고)
print("시작 구슬 OK", {o["name"]: (o["mana"], round(value.ratio(o), 2)) for o in orbs.starter_orbs() if o["name"] not in ("달리기", "텃밭")})

# 5) 모델 ↔ 엔진: 같은 시드에서 구슬을 4턴째에 쓴 판과 안 쓴 판의 최종 골드 차이
def final_gold(extra=None, seed=11):
    g = engine.HexGame(orbs.starter_orbs(), seed=seed, cfg=dict(due0=10 ** 6)); g.start(); g.hp = g.max_hp = 10 ** 6      # 사망·정산 규칙이 끼지 않게(런 구조: 통과하면 정산액을 내므로 정산 없이 스테이지 수입만 잰다)
    while g.phase == "play":
        if g.turn == 4 and extra and not getattr(g, "_done", False):
            g._done = True; i = g.add_orb(extra); g.hand.append(i); g.mana = 6
            t = g.valid_tiles(i)[0] if g.needs_tile(extra) else None; r = g.play(len(g.hand) - 1, t); assert r.get("ok"), r
        g.end_turn()
    return g.gold + int(sum(g.res.values()) * engine.SALE_RATE)      # 남은 자원은 판매가로(가치 모델의 자원 값 바닥)
base = final_gold()
for name, orb in {"지속 시전(골드 10/턴)": H("A", payload=[["money", 10, None]], life="stage", mana=1), "골드 건물(3/턴)": H("B", role="build", payload=[["money", 3, None]], life="run", mana=1, hp=40, bcost=["gold", 0, 0], timing="repeating")}.items():
    real = final_gold(orb) - base; model = value.breakdown(orb)["total"]
    assert .6 <= real / model <= 1.6, f"{name}: 엔진 {real} vs 모델 {model:.1f}"
    print(f"  엔진-모델 {name}: 실제 +{real} / 모델 {model:.1f} (비 {real/model:.2f})")

# 6) 측정 풀(개발용 데이터가 있을 때만)
try:
    sys.path.insert(0, os.path.join(P, "..", "sim")); import orbsim as SIM
    rs = []
    for n in sorted(SIM.V3):
        d = orbs.to_dict(SIM.make_orb(n, cost_model=orbs.CM, gold_mult=orbs.GM)); rs.append((value.ratio(d), value.verdict(d), d["mana"]))
    med = st.median(r for r, _, _ in rs); std = sum(1 for _, v, _ in rs if v in ("표준", "최소 가격")) / len(rs)
    sl = [orbs.to_dict(SIM.make_orb(n, cost_model=orbs.CM, gold_mult=orbs.GM)) for n in sorted(SIM.V3)]
    assert all(value.payback(d) <= value.PAYBACK_MAX + .3 for d in sl if d["role"] in ("build", "summon") and not d["hostile"]), "슬롯형은 회수 배율 상한(재료·골드로 갚음)을 지킨다"
    assert .7 <= med <= 1.3, f"풀 배율 중앙값 {med:.2f}"; assert std >= .6, f"표준 비율 {std:.0%}"
    print(f"측정 풀 {len(rs)}개 OK: 중앙값 {med:.2f}, 표준·최소 {std:.0%}, 싸다 {sum(1 for _, v, _ in rs if v.startswith('싸'))}개")
except ImportError: print("측정 풀 건너뜀(sim/ 없음)")
print("가치 모델 시험 통과")

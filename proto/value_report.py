"""가격 이상치 보고서(개발용 — 측정 데이터가 있는 저장소에서만 돈다. Vercel에는 안 올라감).
측정된 이름 풀(sim/orbsim.py: 약 360개)을 전부 구슬로 만들어 value.py 로 가격을 매기고, **표준선에서 벗어난 구슬**과 **동사별 편차**를 표로 낸다.
  python proto/value_report.py            # proto/docs/VALUE_REPORT.md 를 새로 쓴다
  python proto/value_report.py --top 25   # 이상치 표 길이
읽는 법: 배율 = 값어치 ÷ 가격(놀이형은 마나×VPM, 슬롯형은 회수 3배를 1로 본 배율). 1.0 근처가 표준, 1.6 초과는 가격이 싸다(너무 센 구슬 후보), 0.6 미만은 비싸다."""
import os, sys, statistics as st, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
for p in (os.path.join(ROOT, "sim"), os.path.join(HERE, "vendor"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import orbsim as SIM          # 측정 데이터(개발용)
import orbs, value, engine
TOP = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 15
E = value.E0

def build_pool():
    out = []
    for n in sorted(SIM.V3):
        try: d = orbs.to_dict(SIM.make_orb(n, cost_model=orbs.CM, gold_mult=orbs.GM))
        except Exception as e: continue
        out.append(d)
    return out
def synthetic():
    """시너지 구슬 견본: 측정 풀에는 없는 동사·조건을 손으로 만들어 가격 감각을 본다."""
    H = orbs._hand
    L = []
    def add(name, **k): d = H(name, **k); orbs.react_scale(d); d["mana"] = value.mana_for(d); d["text"] = orbs.describe(d); L.append(d)
    add("공격 반응(스테이지)", role="cast", payload=[["money", 3, None]], life="stage", trig="orb_attack", pe=1.0)
    add("처치 보상(스테이지)", role="cast", payload=[["money", 3, None]], life="stage", trig="kill", pe=1.0)
    add("수확 보너스(스테이지)", role="cast", payload=[["harvest", 2, "ore"]], life="stage", trig="harvest", pe=1.0)
    add("공격 반응(즉발 2회)", role="cast", payload=[["damage", 14, None]], life="instant", trig="orb_attack", pe=1.5, rng="around")
    add("식물 깃발(건물)", role="build", payload=[["money", 3, None]], life="run", trig="orb_plant", pe=1.0, hp=10, bcost=["gold", 1, 1])
    add("복수의 탑(피격 반응 건물)", role="build", payload=[["damage", 8, None]], life="run", trig="hit", pe=1.0, hp=10, bcost=["wood", 2, 1], rng="around")
    add("불꽃(화상 3)", role="cast", payload=[["burn", 3, None]], life="instant", pe=1.0)
    add("화염병(화상, 3턴)", role="cast", payload=[["burn", 2, None]], life="turns", pe=1.0, rng="around")
    add("불쏘시개(화상 +18%)", role="cast", payload=[["buff", 18, "burn"]], life="stage", pe=1.0)
    add("황금 장갑(수입 +18%)", role="cast", payload=[["buff", 18, "income"]], life="stage", pe=1.0)
    add("함성(피해 +24%, 3턴)", role="cast", payload=[["buff", 24, "dmg"]], life="instant", pe=2.0)
    add("마법사의 탑(건물 +22%)", role="build", payload=[["buff", 22, "unit"]], life="run", pe=1.0, hp=20, bcost=["wood", 2, 1])
    add("부활의 부적(죽음 반응)", role="cast", payload=[["heal", 20, None]], life="instant", trig="death", pe=1.5)
    return L

def row(d):
    b = value.breakdown(d); return dict(name=d["name"], role=d["role"], life=d["life"], trig=d["trig"], verbs="+".join(p[0] for p in d["payload"]), mana=d["mana"], V=b["total"], payback=value.payback(d), ratio=value.ratio(d), slot=value.is_slot(d), short=value.shortfall(d), verdict=value.verdict(d))
def fmt(r): return f"| {r['name']} | {r['role']}{'·'+r['trig'] if r['trig']!='none' else ''} | {r['life']} | {r['verbs']} | {r['mana']} | {r['V']:.1f} | {r['ratio']:.2f} | {r['verdict']} |"
HEAD = "| 이름 | 역할 | 지속 | 동사 | 마나 | 값어치 | 배율 | 판정 |\n|---|---|---|---|---|---|---|---|"

def main():
    pool = [row(d) for d in build_pool()]; syn = [row(d) for d in synthetic()]
    L = ["# 가격 이상치 보고서", "", "`python proto/value_report.py` 가 만든 파일(직접 고치지 않음). 모델 설명은 `proto/value.py` 머리말.", "",
         "## 1. 환산율(엔진 상수에서 계산)", "", "| 항목 | 값 | 뜻 |", "|---|---|---|",
         f"| 적 체력 / 공격 / 현상금 | {E.ehp:.1f} / {E.eatk:.1f} / {E.bounty} | `CFG`의 ehp·eatk·bounty |", f"| 적 하나 처치 값 | {E.kill:.2f} | 현상금 + 덜 맞는 체력 |", f"| 체력 1 | {E.hp_g:.2f} | 정산액 × SAFETY ÷ 최대 체력 |",
         f"| 자원 1 | {E.res_g:.2f} | 판매율 {engine.SALE_RATE}와 가공율 {E.cfg['process_ratio']}의 혼합 |", f"| **마나 1당 표준 값어치(VPM)** | **{E.vpm:.2f}** | 정산액 ÷ (마나×턴) × 여유 {value.KNOBS['MARGIN']} |",
         f"| 처치 가치 상한 | {E.kill_cap:.1f} | 스테이지 평균 적 {E.n_en:.1f}마리 × 처치 값 × .8 |", ""]
    L += ["## 2. 기대 사건 횟수(반응 구슬의 신뢰도)", "", "| 사건 | 남은 기간 기대 횟수 |", "|---|---|"] + [f"| {k} | {v:.1f} |" for k, v in E.events.items()] + [""]
    L += ["## 3. 풀 전체 분포", "", f"측정된 이름 {len(pool)}개. 놀이형 {sum(1 for r in pool if not r['slot'])} · 슬롯형 {sum(1 for r in pool if r['slot'])}.", "",
          "| 판정 | 개수 | 비율 |", "|---|---|---|"]
    c = collections.Counter(r["verdict"] for r in pool)
    for k in ("싸다(약한 가격)", "표준", "비싸다"): L.append(f"| {k} | {c[k]} | {100*c[k]/len(pool):.0f}% |")
    rs = sorted(r["ratio"] for r in pool); L += ["", f"배율 중앙값 {st.median(rs):.2f}, 10% {rs[len(rs)//10]:.2f}, 90% {rs[-len(rs)//10]:.2f}, 최대 {rs[-1]:.2f}.", ""]
    L += ["## 4. 동사별 배율(첫 동사 기준 중앙값)", "", "| 동사 | 개수 | 중앙값 | 최대 |", "|---|---|---|---|"]
    by = collections.defaultdict(list)
    for r in pool: by[r["verbs"].split("+")[0]].append(r["ratio"])
    for v, xs in sorted(by.items(), key=lambda kv: -st.median(kv[1])): L.append(f"| {v} | {len(xs)} | {st.median(xs):.2f} | {max(xs):.2f} |")
    L += ["", "## 5. 가장 싼 구슬(너무 센 후보) 상위", "", HEAD] + [fmt(r) for r in sorted(pool, key=lambda r: -r["ratio"])[:TOP]]
    L += ["", "## 6. 가장 비싼 구슬 하위", "", HEAD] + [fmt(r) for r in sorted(pool, key=lambda r: r["ratio"])[:TOP]]
    sf = sorted((r for r in pool if r["short"] > 0), key=lambda r: -r["short"])[:TOP]
    L += ["", "## 7. 마나로 못 갚는 놀이형(마나 최대 8에 눌림)", "", "| 이름 | 동사 | 마나 | 값어치 | 못 갚은 몫(골드) |", "|---|---|---|---|---|"] + [f"| {r['name']} | {r['verbs']} | {r['mana']} | {r['V']:.1f} | {r['short']:.1f} |" for r in sf]
    L += ["", "## 8. 시너지 견본(손으로 만든 구슬)", "", HEAD] + [fmt(r) for r in syn] + [""]
    out = os.path.join(HERE, "docs", "VALUE_REPORT.md"); open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L)); print("쓴 파일:", os.path.relpath(out, ROOT)); print("\n".join(L[:0]))
    print(f"풀 {len(pool)}개 — 싸다 {c['싸다(약한 가격)']} · 표준 {c['표준']} · 비싸다 {c['비싸다']} · 배율 중앙값 {st.median(rs):.2f}")
if __name__ == "__main__": main()

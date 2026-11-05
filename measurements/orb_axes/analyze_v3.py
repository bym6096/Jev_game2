import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v3 as A, names3, names4
rows = collections.defaultdict(list)
for l in open("out_v3.jsonl", encoding="utf-8"):
    r = json.loads(l); b, n = r["id"].split("|", 1); rows[(b, n)].append(r["answers"])
byname = {k[1]: k for k in rows}
P = lambda k, key, o: st.mean(a[key]["probabilities"][o] for a in rows[k])
top = lambda k, key: max(A.CHOICES[key][1], key=lambda o: P(k, key, o))
tp = lambda k, key: P(k, key, top(k, key))
LV = ["instant", "turns", "stage", "run", "forever"]
def life(k, v):
    if v == "S":
        s = st.mean(a["lifetime_S"]["score"] for a in rows[k]); return LV[min(4, max(0, round(s)))]
    return top(k, {"v2": "lifetime_v2", "A": "lifetime_A", "B": "lifetime_B"}[v])
def life_reps(k, v):
    return [LV[min(4, max(0, round(a["lifetime_S"]["score"])))] if v == "S" else max(a[{"v2": "lifetime_v2", "A": "lifetime_A", "B": "lifetime_B"}[v]]["probabilities"], key=a[{"v2": "lifetime_v2", "A": "lifetime_A", "B": "lifetime_B"}[v]]["probabilities"].get) for a in rows[k]]
verbs = list(A.CHOICES["verb"][1]); p1v = lambda k: max(P(k, "verb", o) for o in verbs)
main = [k for k in rows if not k[0].startswith("보충")]
out = []; W = lambda *a: out.append(" ".join(str(x) for x in a))

W("## 1. 안정성 (3번 반복, 339개)")
W("| 축 | 1순위가 바뀐 이름 | (v2 같은 축) |"); W("|---|---|---|")
v2 = {"role": 9, "timing": 6, "trigger": 6, "range": 25, "material": 11, "bagfate": 12, "verb": 27}
for key in ("role", "timing", "trigger", "range", "material", "bagfate", "bagfate2", "verb"):
    f = sum(len({max(a[key]["probabilities"], key=a[key]["probabilities"].get) for a in rows[k]}) > 1 for k in rows)
    W(f"| {key} | {f}/{len(rows)} | {v2.get(key, '—')}/318 |")
for v in ("v2", "A", "B", "S"):
    W(f"| 지속 기간 {v} | {sum(len(set(life_reps(k, v))) > 1 for k in rows)}/{len(rows)} | {'37/318' if v == 'v2' else '—'} |")

W("\n## 2. 지속 기간 문구 4가지 비교")
exp = names4.EXPECT_LIFE; groups = {"스테이지 기대": [n for n, a in exp.items() if a[0] == "stage"], "몇 턴 기대": [n for n, a in exp.items() if a == ["turns"] or a == ["turns", "stage"]],
        "즉시 기대": [n for n, a in exp.items() if a == ["instant"]], "런/영구 기대(건물 등)": [n for n, a in exp.items() if a == ["run", "forever"]], "영구 기대": [n for n, a in exp.items() if a == ["forever"]]}
W("| 문구 | 전체 일치 | " + " | ".join(groups) + " | 기존256 중 스테이지 | 영구 | 런 | 시전(cast)인데 런·영구 |"); W("|---|---|" + "---|" * (len(groups) + 4))
best = {}
for v in ("v2", "A", "B", "S"):
    hit = {n: life(byname[n], v) in exp[n] for n in exp}
    cells = [f"{sum(hit[n] for n in g)}/{len(g)}" for g in groups.values()]
    dist = collections.Counter(life(k, v) for k in main); cast = [k for k in main if top(k, "role") == "cast"]
    cr = sum(life(k, v) in ("run", "forever") for k in cast)
    W(f"| {v} | {sum(hit.values())}/{len(hit)} | " + " | ".join(cells) + f" | {dist['stage']} ({dist['stage']/len(main):.0%}) | {dist['forever']} ({dist['forever']/len(main):.0%}) | {dist['run']} | {cr}/{len(cast)} ({cr/len(cast):.0%}) |")
W("\n분포 (기존 256개):")
for v in ("v2", "A", "B", "S"): W(f"- {v}:", dict(collections.Counter(life(k, v) for k in main)))
W("\n스테이지 기대 이름별 (v2 / A / B / S):")
for n in groups["스테이지 기대"] + [x for x in exp if exp[x] == ["stage", "turns"]]:
    k = byname[n]; W(f"- {n} (기대 {'|'.join(exp[n])}): " + " / ".join(f"{life(k, v)}" + (f" {P(k, {'v2':'lifetime_v2','A':'lifetime_A','B':'lifetime_B'}[v], life(k, v)):.2f}" if v != 'S' else f" {st.mean(a['lifetime_S']['score'] for a in rows[k]):.1f}") for v in ("v2", "A", "B", "S")))
W("\n어긋난 것 (각 문구):")
for v in ("v2", "A", "B", "S"):
    W(f"- {v}:", "; ".join(f"{n}→{life(byname[n], v)}(기대 {'|'.join(exp[n])})" for n in exp if life(byname[n], v) not in exp[n]))

W("\n## 3. 발동 조건·시점 (합친 구조)")
W("- trigger 분포(기존 256):", dict(collections.Counter(top(k, "trigger") for k in main).most_common()))
W("- timing 분포:", dict(collections.Counter(top(k, "timing") for k in main).most_common()))
W("- 조건이 있는(≥0.5) 이름:", ", ".join(f"{k[1]}→{top(k,'trigger')} {tp(k,'trigger'):.2f}" for k in main if top(k, "trigger") != "none" and tp(k, "trigger") >= .5))
tr = names3.EXPECT["trigger"]; W("- 사전 기대 6개:", ", ".join(f"{n}→{top(byname[n],'trigger')} {tp(byname[n],'trigger'):.2f}(기대 {'|'.join(a)}){' ✓' if top(byname[n],'trigger') in a else ' ✗'}" for n, a in tr.items()))

W("\n## 4. 범위 (자신+하나 → 단일)")
fl = [k for k in rows if len({max(a['range']['probabilities'], key=a['range']['probabilities'].get) for a in rows[k]}) > 1]
SELF = {"money", "draw", "recycle", "trash", "peek", "tempo", "energy", "create", "amplify"}
W(f"- 바뀐 이름 {len(fl)}/{len(rows)} (v2: 25/318). 그중 대상이 원래 자기 자신인 동사 {sum(top(k,'verb') in SELF for k in fl)}개 → 실질 영향 {sum(top(k,'verb') not in SELF for k in fl)}개")
W("- 분포(기존 256):", dict(collections.Counter(top(k, "range") for k in main).most_common()))

W("\n## 5. 구슬의 운명: 기존 문구 vs 자동 문구 재작성")
pas = names3.EXPECT["bagfate"]
for key in ("bagfate", "bagfate2"):
    W(f"- {key}: 사전 기대 {sum(top(byname[n], key) in a for n, a in pas.items())}/{len(pas)} | 분포(기존 256) {dict(collections.Counter(top(k, key) for k in main).most_common())} | passive 이름: {', '.join(k[1] for k in main if top(k, key) == 'passive')}")
    W(f"  - 부적 {top(byname['부적'], key)} {tp(byname['부적'], key):.2f} | 상태이상면역 {top(byname['상태이상면역'], key)} {tp(byname['상태이상면역'], key):.2f}")

W("\n## 6. 회귀 확인: v2에서 맞던 축이 그대로인가 (사전 기대)")
for key in ("material", "role", "trigger", "bagfate"):
    e = names3.EXPECT[key]; ok = sum(top(byname[n], key) in a for n, a in e.items() if n in byname)
    W(f"- {key}: {ok}/{sum(n in byname for n in e)} (v2: " + {"material": "43/44", "role": "41/42", "trigger": "5/6", "bagfate": "10/11"}[key] + ")")
open("analysis_v3_part1.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

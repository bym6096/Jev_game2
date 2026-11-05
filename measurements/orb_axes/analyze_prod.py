import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes_v3 as A, names5
import compose3 as C, compose4 as C4
rows = collections.defaultdict(list)
for l in open("out_prod.jsonl", encoding="utf-8"):
    r = json.loads(l); b, n = r["id"].split("|", 1); rows[n].append(r["answers"])
C.V3.update(rows); C.V2.update(rows)                       # compose3/4 read these dicts
P = lambda n, key, o: st.mean(a[key]["probabilities"][o] for a in rows[n])
top = lambda n, key: max(rows[n][0][key]["probabilities"], key=lambda o: P(n, key, o))
verbs = list(A.CHOICES["verb"][1])
sel = lambda n: [v for v, _ in C.select_verbs(rows[n])]
out = []; W = lambda *a: out.append(" ".join(str(x) for x in a))
W("# 생산 건물·일꾼·도구 이름 시험 (v3 축 그대로, 32개 × 3번)", "")
W("| 이름 | 역할 | 동사(선택) | 재료 | 지속(A) | 만들어진 구슬 (깨끗한) |", ) ; W("|---|---|---|---|---|---|")
for b, n in names5.POOL:
    c = C4.compose4(n)
    W(f"| {n} | {top(n,'role')} {P(n,'role',top(n,'role')):.2f} | {', '.join(f'{v} {P(n,chr(118)+chr(101)+chr(114)+chr(98),v):.2f}' for v in sel(n))} | {top(n,'material')} {P(n,'material',top(n,'material')):.2f} | {top(n,'lifetime_A')} | {c['text']} ({c['cost']}) |")
W("")
tot = [0, 0]; res = {}
def check(label, f, names):
    ok = [n for n in names if f(n)]; res[label] = (len(ok), len(names)); tot[0] += len(ok); tot[1] += len(names); return [n for n in names if not f(n)]
miss = {}
miss["역할"] = check("역할", lambda n: top(n, "role") == names5.ROLE[n], list(names5.ROLE))
miss["재료"] = check("재료", lambda n: top(n, "material") in names5.MATERIAL[n].split(), list(names5.MATERIAL))
miss["동사"] = check("동사", lambda n: set(sel(n)) & set(names5.VERB[n].split()), list(names5.VERB))
miss["소환물(일꾼)"] = check("소환물(일꾼)", lambda n: top(n, "unit") == "worker", names5.WORKER)
W("## 사전 기대와 일치")
for k, (a, b) in res.items(): W(f"- {k}: {a}/{b}" + (f"  — 어긋남: " + "; ".join(f"{n}({top(n,'role')}/{top(n,'material')}/{','.join(sel(n))})" for n in miss[k]) if miss[k] else ""))
W(f"\n**전체 {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.0%}**")
W("\n## 건물 이름 23개: 생산 건물로 쓸 수 있는 형태인가")
bd = names5.BUILD
usable = [n for n in bd if top(n, "role") == "build" and any(v in ("harvest", "grow", "money", "create") for v in sel(n)) and top(n, "material") != "none"]
W(f"- 역할=건물 + 자원 동사(채집·성장·돈·만들기) + 재료 있음: {len(usable)}/{len(bd)}")
W("- 아닌 것:", "; ".join(f"{n}({top(n,'role')}, {','.join(sel(n))}, {top(n,'material')})" for n in bd if n not in usable))
W("- 자원 생산 동사가 아닌 건물의 동사 분포:", dict(collections.Counter(v for n in bd for v in sel(n)[:1] if v not in ("harvest", "grow", "money", "create")).most_common()))
W("- p1 < 0.4(애매)인 건물:", ", ".join(f"{n}({max(P(n,'verb',o) for o in verbs):.2f})" for n in bd if max(P(n, 'verb', o) for o in verbs) < .4) or "없음")
W("- 지속: ", dict(collections.Counter(C.lifetime(rows[n], 'build', 2, '깨끗한') for n in bd)))
open("analysis_prod.md", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))

"""Effect descriptions: "카드" -> "구슬". Same names, same effect question, only the Korean option descriptions differ.
Runs old twice (to see Jev's own wobble) and new once. Output: out.json + printed summary."""
import sys, json, statistics as st
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "../../toys/card-forge")
import forge
src = open("../../toys/card-forge/make_samples.py", encoding="utf-8").read()
names = json.loads("[" + src.split("NAMES = [")[1].split("]")[0].replace("\n", " ") + "]")
# names aimed at the 11 effects whose description mentions a card, plus a few ordinary ones
names += ["복제 인간", "분신술", "거울 속의 나", "도서관", "고서점", "마법 서고", "예언자", "점쟁이", "수정 구슬", "타임머신",
          "자물쇠", "봉인된 상자", "쿠폰북", "반값 할인", "앵무새", "따라쟁이", "카멜레온", "변신 마법", "지우개", "기억 삭제",
          "쌍둥이", "메아리", "도박사의 주사위", "시간 되감기", "집중 훈련", "공명 종", "손오공", "이글이글 열매", "칼", "방패"]
names = list(dict.fromkeys(names))
OLD = {k: v[1] for k, v in forge.ALL_EFFECTS.items()}
NEW = {k: d.replace("카드", "구슬") for k, d in OLD.items()}
CHANGED = [k for k in OLD if OLD[k] != NEW[k]]
def ask(args):
    name, crit = args
    body = forge.build_request(name)
    body["questions"] = {"effect": body["questions"]["effect"]}
    body["questions"]["effect"]["criteria"] = crit
    for _ in range(3):
        try:
            pr = forge.call_jev(body)["answers"]["effect"]["probabilities"]
            return {k: round(p, 4) for k, p in pr.items()}
        except Exception as e:
            err = e
    raise err
jobs = [(n, c) for n in names for c in (OLD, OLD, NEW)]
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(ask, jobs))
rows = []
for i, n in enumerate(names):
    a, a2, b = res[3 * i:3 * i + 3]
    rows.append({"name": n, "old": a, "old2": a2, "new": b})
json.dump({"changed": CHANGED, "rows": rows}, open("out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
top = lambda d: max(d, key=d.get)
def l1(x, y): return sum(abs(x[k] - y[k]) for k in x) / 2          # 0 = same distribution, 1 = disjoint
def margin(d): s = sorted(d.values(), reverse=True); return s[0] - s[1]
print(f"{len(rows)} names, {len(CHANGED)} effects with changed description: {', '.join(forge.ALL_EFFECTS[k][0] for k in CHANGED)}\n")
print(f"{'name':16s} {'old':>9s} {'old2':>9s} {'new':>9s}   L1(old,old2) L1(old,new)")
for r in rows:
    flag = "" if top(r["old"]) == top(r["new"]) else "  <-- top1 changed" + ("" if top(r["old"]) != top(r["old2"]) else "")
    print(f"{r['name']:16s} {top(r['old']):>9s} {top(r['old2']):>9s} {top(r['new']):>9s}   {l1(r['old'],r['old2']):.3f}        {l1(r['old'],r['new']):.3f}{flag}")
n = len(rows)
print("\n--- summary ---")
print("top1 differs  old vs old2 (Jev's own wobble):", sum(top(r["old"]) != top(r["old2"]) for r in rows), "/", n)
print("top1 differs  old vs new                    :", sum(top(r["old"]) != top(r["new"]) for r in rows), "/", n)
print("mean L1       old vs old2:", round(st.mean(l1(r["old"], r["old2"]) for r in rows), 4), "| old vs new:", round(st.mean(l1(r["old"], r["new"]) for r in rows), 4))
print("mean top1 prob old:", round(st.mean(max(r["old"].values()) for r in rows), 3), "old2:", round(st.mean(max(r["old2"].values()) for r in rows), 3), "new:", round(st.mean(max(r["new"].values()) for r in rows), 3))
print("mean margin    old:", round(st.mean(margin(r["old"]) for r in rows), 3), "old2:", round(st.mean(margin(r["old2"]) for r in rows), 3), "new:", round(st.mean(margin(r["new"]) for r in rows), 3))
print("margin<0.1     old:", sum(margin(r["old"]) < .1 for r in rows), "old2:", sum(margin(r["old2"]) < .1 for r in rows), "new:", sum(margin(r["new"]) < .1 for r in rows))
print("\nper changed effect: times top1 (old / old2 / new) and total probability mass (old -> new) over all names")
for k in CHANGED:
    t = lambda s: sum(top(r[s]) == k for r in rows)
    m = lambda s: sum(r[s][k] for r in rows)
    print(f"  {forge.ALL_EFFECTS[k][0]:6s} top1 {t('old')} / {t('old2')} / {t('new')}   mass {m('old'):.2f} (old2 {m('old2'):.2f}) -> {m('new'):.2f}")

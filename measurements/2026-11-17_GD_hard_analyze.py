"""2차 어려운 문항 분석. python3 -I measurements/2026-11-17_GD_hard_analyze.py"""
import json, os, statistics as st
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
items = {it["id"]: it for it in json.load(open(os.path.join(HERE, "2026-11-17_GD_T6.items.json"), encoding="utf-8"))}
by = defaultdict(list)
for l in open(os.path.join(HERE, "2026-11-17_GD_T6.jsonl"), encoding="utf-8"):
    r = json.loads(l); by[(r["backend"], r["id"])].append(r["answers"]["q"]["probabilities"])
top = lambda p: max(p.items(), key=lambda kv: kv[1])[0]
BE = ("jev", "gemini")
out = []; say = out.append
say("## T6 어려운 정답 문항 (50문항 × 2회)")
say("| 유형 | 문항 | Jev 정답률 | Gemini 정답률 | Jev 정답 확률 | Gemini 정답 확률 |")
say("|---|---|---|---|---|---|")
cats = list(dict.fromkeys(it["cond"] for it in items.values()))
T = {b: [0, 0, [], []] for b in BE}   # ok, n, p_correct, conf_when_wrong
for c in cats + ["_all"]:
    ids = [i for i, it in items.items() if c == "_all" or it["cond"] == c]
    row = []
    for b in BE:
        ok = n = 0; pc = []
        for i in ids:
            for p in by[(b, i)]:
                n += 1; e = items[i]["expect"]["q"]; ok += top(p) == e; pc.append(p.get(e, 0))
                if c == "_all" and top(p) != e: T[b][3].append(max(p.values()))
        row.append((ok, n, st.mean(pc)))
    name = "**전체**" if c == "_all" else c
    say(f"| {name} | {len(ids)} | {row[0][0]}/{row[0][1]} ({100*row[0][0]/row[0][1]:.0f}%) | {row[1][0]}/{row[1][1]} ({100*row[1][0]/row[1][1]:.0f}%) | {row[0][2]:.2f} | {row[1][2]:.2f} |")
say("\n문항별 (정답 확률, 2회 평균. ✗ = 다수결 오답)")
only = {b: [] for b in BE}; both = []
for i, it in items.items():
    e = it["expect"]["q"]; cell = []
    wrong = {}
    for b in BE:
        p = st.mean(x.get(e, 0) for x in by[(b, i)]); t = top(by[(b, i)][0])
        wrong[b] = t != e
        cell.append(f"{b} {p:.2f}{' ✗→' + t if t != e else ''}")
    if wrong["jev"] and wrong["gemini"]: both.append(i)
    elif wrong["jev"]: only["jev"].append(i)
    elif wrong["gemini"]: only["gemini"].append(i)
    if any(wrong.values()):
        say(f"- {i} [{it['cond']}] 정답 {e}: " + " / ".join(cell))
say(f"\n- Jev만 틀림: {', '.join(only['jev']) or '없음'}")
say(f"- Gemini만 틀림: {', '.join(only['gemini']) or '없음'}")
say(f"- 둘 다 틀림: {', '.join(both) or '없음'}")
for b in BE:
    w = T[b][3]
    say(f"- {b} 틀렸을 때 1위 확률 평균: {st.mean(w):.2f} ({len(w)}회)" if w else f"- {b}: 오답 없음")
    flips = sum(top(by[(b, i)][0]) != top(by[(b, i)][1]) for i in items)
    say(f"  - {b} 2회 사이 1위 바뀐 문항: {flips}/50")
txt = "\n".join(out); open(os.path.join(HERE, "2026-11-17_GD_T6_summary.md"), "w", encoding="utf-8").write(txt + "\n"); print(txt)

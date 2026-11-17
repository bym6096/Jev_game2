"""Jev vs Gemini Decision 1 비교 분석 (2026-11-17). python3 -I measurements/2026-11-17_GD_analyze.py"""
import json, math, os, statistics as st, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: os.path.join(HERE, f"2026-11-17_GD_{n}")
BE = ("jev", "gemini")


def load(n):
    items = {it["id"]: it for it in json.load(open(P(n) + ".items.json", encoding="utf-8"))}
    rows = [json.loads(l) for l in open(P(n) + ".jsonl", encoding="utf-8")]
    return items, rows


def probs(ans):
    return ans["probabilities"]


def top(pr):
    return max(pr.items(), key=lambda kv: kv[1])[0]


def tvd(a, b):
    return 0.5 * sum(abs(a.get(k, 0) - b.get(k, 0)) for k in set(a) | set(b))


def pct(x):
    return f"{100 * x:.0f}%"


out = []
say = lambda *a: out.append(" ".join(str(x) for x in a))

# ---------- T1 ----------
items, rows = load("T1")
by = defaultdict(list)   # (be, id) -> [probs per rep]
for r in rows:
    by[(r["backend"], r["id"])].append(probs(r["answers"]["q"]))
cats = list(dict.fromkeys(it["cond"] for it in items.values()))
say("## T1 정답 있는 판정 (40문항 × 3회)")
say("| 유형 | Jev 정답률 | Gemini 정답률 | Jev 정답 확률 평균 | Gemini 정답 확률 평균 |")
say("|---|---|---|---|---|")
tot = {b: [0, 0, []] for b in BE}
for c in cats:
    cell = []
    for b in BE:
        ok = n = 0
        pc = []
        for i, it in items.items():
            if it["cond"] != c:
                continue
            for pr in by[(b, i)]:
                n += 1
                ok += top(pr) == it["expect"]["q"]
                pc.append(pr.get(it["expect"]["q"], 0))
        tot[b][0] += ok; tot[b][1] += n; tot[b][2] += pc
        cell.append((ok / n, st.mean(pc)))
    say(f"| {c} | {pct(cell[0][0])} | {pct(cell[1][0])} | {cell[0][1]:.2f} | {cell[1][1]:.2f} |")
say(f"| **전체** | **{pct(tot['jev'][0] / tot['jev'][1])}** | **{pct(tot['gemini'][0] / tot['gemini'][1])}** | {st.mean(tot['jev'][2]):.2f} | {st.mean(tot['gemini'][2]):.2f} |")

say("\n틀린 문항 (3회 중 다수결):")
for i, it in items.items():
    wrong = []
    for b in BE:
        tops = [top(pr) for pr in by[(b, i)]]
        maj = max(set(tops), key=tops.count)
        if maj != it["expect"]["q"]:
            p = st.mean(pr.get(it["expect"]["q"], 0) for pr in by[(b, i)])
            wrong.append(f"{b}→{maj}(정답 확률 {p:.2f})")
    if wrong:
        say(f"- {i} [{it['cond']}] 정답 {it['expect']['q']}: " + ", ".join(wrong))

say("\n반복 안정성·확률 모양:")
for b in BE:
    same = flips = 0
    spread, conf, ent, ext = [], [], [], 0
    for i in items:
        reps = by[(b, i)]
        tops = [top(pr) for pr in reps]
        same += len(set(tops)) == 1
        for k in reps[0]:
            vals = [pr.get(k, 0) for pr in reps]
            spread.append(max(vals) - min(vals))
        for pr in reps:
            m = max(pr.values())
            conf.append(m)
            ext += m > 0.9
            ent.append(-sum(p * math.log2(p) for p in pr.values() if p > 0))
    n = sum(len(by[(b, i)]) for i in items)
    say(f"- {b}: 3회 1위 같음 {same}/{len(items)}, 선택지 확률 흔들림 평균 {st.mean(spread):.3f}·최대 {max(spread):.2f}, "
        f"1위 확률 평균 {st.mean(conf):.2f}, 1위>0.9 {ext}/{n}, 엔트로피 평균 {st.mean(ent):.2f}비트")
agree = sum(top(by[("jev", i)][0]) == top(by[("gemini", i)][0]) for i in items)
say(f"- 두 모델 1위 일치(1회차): {agree}/{len(items)}, 분포 차이(TVD) 평균 {st.mean(tvd(by[('jev', i)][0], by[('gemini', i)][0]) for i in items):.2f}")

# ---------- T3 ----------
items, rows = load("T3")
pr3 = {(r["backend"], r["id"]): probs(r["answers"]["q"]) for r in rows}
bases = sorted({i.rsplit("_", 1)[0] for i in items})
say("\n## T3 맥락 민감도 (8상황 × 기준/관련/무관)")
say("| | 관련 맥락 TVD | 무관한 맥락 TVD | 관련 맥락이 정한 방향으로 움직임 | 관련 맥락으로 1위 바뀜 |")
say("|---|---|---|---|---|")
for b in BE:
    rel, irr, dirok, flip = [], [], 0, 0
    detail = []
    for x in bases:
        up = items[f"{x}_base"]["expect"]["q_up"]
        pb, prl, pir = pr3[(b, f"{x}_base")], pr3[(b, f"{x}_rel")], pr3[(b, f"{x}_irr")]
        rel.append(tvd(pb, prl)); irr.append(tvd(pb, pir))
        dirok += prl.get(up, 0) > pb.get(up, 0) or (pb.get(up, 0) > 0.97 and prl.get(up, 0) > 0.97)
        flip += top(pb) != top(prl)
        detail.append(f"{x}: {up} {pb.get(up, 0):.2f}→{prl.get(up, 0):.2f} (무관 {pir.get(up, 0):.2f})")
    say(f"| {b} | {st.mean(rel):.2f} | {st.mean(irr):.2f} | {dirok}/8 | {flip}/8 |")
    T3d = detail
    out.append(f"<!-- {b}: " + "; ".join(detail) + " -->")

# ---------- T4 ----------
items, rows = load("T4")
pr4 = {(r["backend"], r["id"]): probs(r["answers"]["q"]) for r in rows}
keys = sorted({i.rsplit("_", 1)[0] for i in items}, key=lambda s: int(s[1:]))
ANS = {"k1": "pain", "k2": "ice", "k3": "accept", "k4": "hurt", "k5": "does_not_buy", "k6": "fewer", "k8": "light",
       "k10": "hurt", "k11": "does_not", "k9": "mystic", "k12": "funny"}
say("\n## T4 한국어·영어 (12쌍)")
say("| | 한·영 1위 일치 | 한·영 분포 차이(TVD) | 한국어 정답 | 영어 정답 |")
say("|---|---|---|---|---|")
for b in BE:
    ag, d, ko_ok, en_ok = 0, [], 0, 0
    for k in keys:
        m = items[f"{k}_ko"]["map"]
        ko = {m[o]: p for o, p in pr4[(b, f"{k}_ko")].items()}
        en = pr4[(b, f"{k}_en")]
        ag += top(ko) == top(en); d.append(tvd(ko, en))
        if k in ANS:
            ko_ok += top(ko) == ANS[k]; en_ok += top(en) == ANS[k]
    say(f"| {b} | {ag}/12 | {st.mean(d):.2f} | {ko_ok}/{len(ANS)} | {en_ok}/{len(ANS)} |")

# ---------- T5 ----------
items, rows = load("T5")
sys.path.insert(0, os.path.join(HERE, "..", "phrase"))
import jev  # noqa: E402

score = defaultdict(list)   # (be, id) -> [score per rep]
for r in rows:
    it = items[r["id"]]
    g = it["game"]
    jev._call = lambda s, q, _a=r["answers"]: _a
    if g["kind"] == "brief":
        jev.render_ko = lambda *a, _l=g["line"], **k: _l
        hist = [{"cells": {"x": "x"}}] if it["cond"] == "brief_repeat" else []
        res = jev.judge(g["brief"], {"x": "x"}, history=hist)
    else:
        jev.render_free_ko = lambda *a, _l=g["line"], **k: _l
        res = jev.judge_rush(g["goal"], [{"t": "x"}] * max(1, len(g["line"].split())))
    score[(r["backend"], r["id"])].append(res["score"])
avg = {k: st.mean(v) for k, v in score.items()}
groups = sorted({i.rsplit("_", 1)[0] for i in items})
say("\n## T5 실제 게임 판정 (phrase/jev.py 점수식 그대로, 2회 평균)")
say("| | 잘 지은 줄 평균 | 뻔한 줄 평균 | 낱말 늘어놓기 평균 | 순서 good>plain>salad 지킨 의뢰 | good>salad 지킨 의뢰 | 같은 시안 다시 보내면 점수 하락 | 2회 점수 차 평균 |")
say("|---|---|---|---|---|---|---|---|")
for b in BE:
    tiers = {t: [avg[(b, f"{g}_{t}")] for g in groups if (b, f"{g}_{t}") in avg] for t in ("good", "plain", "salad")}
    order = gs = 0
    for g in groups:
        try:
            a, p_, s = avg[(b, f"{g}_good")], avg[(b, f"{g}_plain")], avg[(b, f"{g}_salad")]
        except KeyError:
            continue
        order += a > p_ > s; gs += a > s
    rep_drop = [(g, avg[(b, f"{g}_good")], avg[(b, f"{g}_repeat")]) for g in groups if (b, f"{g}_repeat") in avg]
    drop = sum(r < a for _, a, r in rep_drop)
    noise = st.mean(abs(v[0] - v[1]) for k, v in score.items() if k[0] == b and len(v) == 2)
    say(f"| {b} | {st.mean(tiers['good']):.0f} | {st.mean(tiers['plain']):.0f} | {st.mean(tiers['salad']):.0f} | {order}/{len(groups)} | {gs}/{len(groups)} | {drop}/{len(rep_drop)} | {noise:.0f} |")


def spearman(x, y):
    rk = lambda v: {i: r for r, i in enumerate(sorted(range(len(v)), key=lambda i: v[i]))}
    rx, ry = rk(x), rk(y)
    n = len(x)
    return 1 - 6 * sum((rx[i] - ry[i]) ** 2 for i in range(n)) / (n * (n * n - 1))


ids = [i for i in items if ("jev", i) in avg and ("gemini", i) in avg]
say(f"\n두 모델 점수 순위 상관(Spearman, {len(ids)}개 줄): {spearman([avg[('jev', i)] for i in ids], [avg[('gemini', i)] for i in ids]):.2f}")
say("\n줄별 점수 (Jev / Gemini):")
for g in groups:
    cells = []
    for t in ("good", "plain", "salad", "repeat"):
        i = f"{g}_{t}"
        if i in items:
            cells.append(f"{t} {avg.get(('jev', i), float('nan')):.0f}/{avg.get(('gemini', i), float('nan')):.0f}")
    say(f"- {g}: " + ", ".join(cells))

# ---------- 속도·토큰 ----------
say("\n## 속도·토큰 (전체 호출)")
for b in BE:
    lat, tok = [], []
    for n in ("T1", "T3", "T4", "T5"):
        for l in open(P(n) + ".jsonl", encoding="utf-8"):
            r = json.loads(l)
            if r["backend"] == b:
                lat.append(r["latency_ms"])
                u = r["usage"] or {}
                tok.append(u.get("input_tokens") or u.get("total_input_tokens") or 0)
    lat.sort()
    say(f"- {b}: {len(lat)}회, 응답 p50 {lat[len(lat) // 2]}ms · p95 {lat[int(len(lat) * .95)]}ms, 요청당 입력 토큰 평균 {st.mean(tok):.0f}")

text = "\n".join(out)
open(P("summary") + ".md", "w", encoding="utf-8").write(text + "\n")
print(text)

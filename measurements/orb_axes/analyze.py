import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, names
NOUL = list(axes.PAYLOAD) + list(axes.MODS_NOUL)
CH = list(axes.CHOICES)
def load(f):
    d = collections.defaultdict(list)
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); d[r["id"].split("|", 1)[1]].append(r["answers"])
    return d
ko, en = load("out_ko.jsonl"), load("out_en.jsonl")
N = [n[0] for n in names.NAMES]; EN = {n[0]: n[1] for n in names.NAMES}
nv = lambda a, k: a[k]["noul"]
def mean_noul(runs, k): return st.mean(nv(a, k) for a in runs)
def mean_prob(runs, k, o): return st.mean(a[k]["probabilities"][o] for a in runs)
def top(runs, k):
    opts = runs[0][k]["probabilities"]; return max(opts, key=lambda o: mean_prob(runs, k, o))

out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))

# A. repeat stability
P("## A. 같은 입력 3번 (한국어)")
P("| 축 | 평균 흔들림(최대-최소) | 흔들림 0.15↑ 비율 | 0.5선을 넘나든 비율 |"); P("|---|---|---|---|")
flip_all = []
for k in NOUL:
    sp = [max(nv(a, k) for a in ko[n]) - min(nv(a, k) for a in ko[n]) for n in N]
    fl = [(max(nv(a, k) for a in ko[n]) >= .5) != (min(nv(a, k) for a in ko[n]) >= .5) for n in N]
    flip_all += fl
    P(f"| {k} | {st.mean(sp):.3f} | {sum(s>=.15 for s in sp)/len(sp):.0%} | {sum(fl)/len(fl):.0%} |")
P(f"noul 전체 0.5선 넘나듦: {sum(flip_all)}/{len(flip_all)} = {sum(flip_all)/len(flip_all):.1%}")
P(); P("| 선택 축 | 1순위가 3번 중 달라진 이름 수 | 평균 1순위 확률 |"); P("|---|---|---|")
for k in CH:
    ch = sum(len({max(a[k]["probabilities"], key=a[k]["probabilities"].get) for a in ko[n]}) > 1 for n in N)
    pm = st.mean(max(mean_prob(ko[n], k, o) for o in axes.CHOICES[k][1]) for n in N)
    P(f"| {k} | {ch}/{len(N)} | {pm:.2f} |")

# B. expectations
P(); P("## B. 미리 적어 둔 기대값과 일치 (한국어 3회 평균 / 영어)")
res = collections.defaultdict(lambda: [0, 0, 0, 0]); miss = []
for ko_name, en_name, exp in names.NAMES:
    for t in names.parse(exp):
        for lab, runs in (("ko", ko[ko_name]), ("en", en[ko_name])):
            if t[0] == "+":
                ok = max(mean_noul(runs, a) for a in t[1]) >= .5; key = "+" + "|".join(t[1])
                val = max(t[1], key=lambda a: mean_noul(runs, a)); v = mean_noul(runs, val)
            elif t[0] == "-":
                ok = all(mean_noul(runs, a) < .3 for a in t[1]); key = "-" + t[1][0]
                val = max(t[1], key=lambda a: mean_noul(runs, a)); v = mean_noul(runs, val)
            else:
                got = top(runs, t[1]); ok = got in t[2]; key = "=" + t[1]; v = got
            i = 0 if lab == "ko" else 2
            res[key][i] += ok; res[key][i + 1] += 1
            if lab == "ko" and not ok: miss.append(f"{ko_name} ({en_name}) {t[0]}{'|'.join(t[1]) if t[0]!='=' else t[1]+'='+'|'.join(t[2])} → 실제 {v if isinstance(v,str) else round(v,2)}")
tot = [0, 0, 0, 0]
P("| 기대 | 한국어 일치 | 영어 일치 |"); P("|---|---|---|")
byaxis = collections.defaultdict(lambda: [0, 0, 0, 0])
for k, r in res.items():
    ax = k[1:].split("|")[0]
    for i in range(4): byaxis[(k[0], ax)][i] += r[i]; tot[i] += r[i]
for (s, ax), r in sorted(byaxis.items()):
    P(f"| {s}{ax} | {r[0]}/{r[1]} | {r[2]}/{r[3]} |")
P(f"**전체: 한국어 {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.0%}, 영어 {tot[2]}/{tot[3]} = {tot[2]/tot[3]:.0%}**")
P(); P("한국어에서 어긋난 것:"); [P("- " + m) for m in miss]

# C. coverage
P(); P("## C. 이름마다 켜진 동사 수 (0.5 이상, 한국어 평균)")
cnt = collections.Counter(); empties = []; many = []
for n in N:
    on = [k for k in axes.PAYLOAD if mean_noul(ko[n], k) >= .5]; cnt[len(on)] += 1
    if not on: empties.append(n)
    if len(on) >= 4: many.append((n, on))
P("개수별 이름 수:", dict(sorted(cnt.items())))
P("동사가 하나도 안 켜진 이름:", ", ".join(empties) or "없음")
P("4개 이상 켜진 이름:", "; ".join(f"{n}({','.join(o)})" for n, o in many) or "없음")
# top-1 payload prob distribution
t1 = [max(mean_noul(ko[n], k) for k in axes.PAYLOAD) for n in N]
P(f"동사 1순위 확률 평균 {st.mean(t1):.2f}, 중앙값 {st.median(t1):.2f}, 0.3 미만 {sum(x<.3 for x in t1)}개")

# D. redundancy
P(); P("## D. 서로 겹치는 축 (이름 56개에서 상관 0.6 이상)")
def corr(x, y):
    mx, my = st.mean(x), st.mean(y); sx = sum((a-mx)**2 for a in x)**.5; sy = sum((b-my)**2 for b in y)**.5
    return sum((a-mx)*(b-my) for a, b in zip(x, y)) / (sx*sy) if sx and sy else 0
M = {k: [mean_noul(ko[n], k) for n in N] for k in NOUL}
pairs = sorted(((corr(M[a], M[b]), a, b) for i, a in enumerate(NOUL) for b in NOUL[i+1:]), reverse=True)
for c, a, b in pairs[:8]: P(f"- {a} ~ {b}: {c:.2f}")
# choice vs noul links
P(); P("선택 축 분포 (한국어 1순위)")
for k in CH:
    c = collections.Counter(top(ko[n], k) for n in N); P(f"- {k}: {dict(c)}")

# E. ko vs en
P(); P("## E. 한국어 vs 영어 판정 일치 (이름×축, 0.5 기준)")
ag = {}
for k in NOUL:
    ag[k] = sum((mean_noul(ko[n], k) >= .5) == (mean_noul(en[n], k) >= .5) for n in N) / len(N)
P("noul 평균 일치:", f"{st.mean(ag.values()):.1%}", "| 가장 낮은 축:", ", ".join(f"{k} {v:.0%}" for k, v in sorted(ag.items(), key=lambda x: x[1])[:4]))
for k in CH: P(f"- {k} 1순위 일치: {sum(top(ko[n],k)==top(en[n],k) for n in N)}/{len(N)}")
P(f"평균 절대차(ko 3회평균 vs en): {st.mean(abs(mean_noul(ko[n],k)-mean_noul(en[n],k)) for n in N for k in NOUL):.3f}")

# F. calibration
P(); P("## F. noul 값 분포 (전체 이름×축)")
vals = [mean_noul(ko[n], k) for n in N for k in NOUL]
bins = collections.Counter(min(int(v*5), 4) for v in vals)
P("0~.2 / .2~.4 / .4~.6 / .6~.8 / .8~1 :", [bins[i] for i in range(5)])

# face table
P(); P("## 이름별 결과 (한국어 3회 평균): 켜진 동사(≥0.35) | 역할/시점/범위/대상/지속 | 힘")
for n in N:
    on = sorted(((mean_noul(ko[n], k), k) for k in NOUL if mean_noul(ko[n], k) >= .35), reverse=True)
    ch = "/".join(top(ko[n], k) for k in CH)
    pw = st.mean(a["power"]["score"] for a in ko[n])
    P(f"- {n} ({EN[n]}): " + (", ".join(f"{k} {v:.2f}" for v, k in on) or "—") + f" | {ch} | 힘 {pw:.1f}")
open("analysis.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))

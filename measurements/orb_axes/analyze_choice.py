import sys, json, collections, statistics as st
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, names
V = list(axes.PAYLOAD)
def load(f):
    d = collections.defaultdict(list)
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); d[r["id"][3:]].append(r["answers"])
    return d
ch, nl = load("out_verbchoice.jsonl"), load("out_ko.jsonl")
N = [n[0] for n in names.NAMES]
cp = lambda n: {k: st.mean(a["verb"]["probabilities"][k] for a in ch[n]) for k in V}   # choice probs (3-run mean)
npb = lambda n: {k: st.mean(a[k]["noul"] for a in nl[n]) for k in V}                     # yes/no probs
def rank(p): return sorted(p, key=lambda k: -p[k])

# stability
flip = sum(len({max(a["verb"]["probabilities"], key=a["verb"]["probabilities"].get) for a in ch[n]}) > 1 for n in N)
wig = st.mean(max(a["verb"]["probabilities"][k] for a in ch[n]) - min(a["verb"]["probabilities"][k] for a in ch[n])
              for n in N for k in V for _ in [0]) if False else None
print(f"선택 질문 1순위가 3번 중 달라진 이름: {flip}/{len(N)}")
sp = []
for n in N:
    for k in V:
        v = [a["verb"]["probabilities"][k] for a in ch[n]]; sp.append(max(v) - min(v))
print(f"확률 평균 흔들림 {st.mean(sp):.3f}, 0.1 이상 흔들린 칸 {sum(x>=.1 for x in sp)}/{len(sp)}")

# distribution
p1 = [rank(cp(n)) and cp(n)[rank(cp(n))[0]] for n in N]
p2 = [cp(n)[rank(cp(n))[1]] for n in N]; p3 = [cp(n)[rank(cp(n))[2]] for n in N]
print(f"1순위 확률 중앙 {st.median(p1):.2f} (최소 {min(p1):.2f}) | 2순위 중앙 {st.median(p2):.2f} | 3순위 중앙 {st.median(p3):.2f}")

# selection rules
def sel_top(p, k): return rank(p)[:k]
def sel_rel(p, r=.4, k=3):
    rk = rank(p); return [x for x in rk[:k] if p[x] >= r * p[rk[0]]]
def sel_noul(p, k=3):
    rk = [x for x in rank(p) if p[x] >= .5][:k]; return rk or rank(p)[:1]
rules = {"선택 1순위만": lambda n: sel_top(cp(n), 1), "선택 상위 2": lambda n: sel_top(cp(n), 2),
         "선택 상위 3": lambda n: sel_top(cp(n), 3), "선택 상위 5": lambda n: sel_top(cp(n), 5),
         "선택 상대규칙(1순위의 40%↑, 최대 3)": lambda n: sel_rel(cp(n)),
         "예/아니오 0.5↑ 최대 3(없으면 1개)": lambda n: sel_noul(npb(n)), "예/아니오 0.5↑ 제한 없음": lambda n: [x for x in rank(npb(n)) if npb(n)[x] >= .5]}
# expectations restricted to verb axes
exp = []
for ko, en, e in names.NAMES:
    for t in names.parse(e):
        if t[0] in "+-" and all(a in V for a in t[1]): exp.append((ko, t[0], t[1]))
npos = sum(t[1] == "+" for t in exp); nneg = len(exp) - npos
print(f"\n동사 기대값 {len(exp)}개 (있어야 함 {npos}, 없어야 함 {nneg})")
print("| 방식 | 평균 개수 | 있어야 하는 것이 포함 | 없어야 하는 것이 섞임 | 개수 분포 |"); print("|---|---|---|---|---|")
for lab, f in rules.items():
    S = {n: f(n) for n in N}
    hit = sum(t == "+" and any(a in S[n] for a in ax) for n, t, ax in exp)
    bad = sum(t == "-" and any(a in S[n] for a in ax) for n, t, ax in exp)
    c = collections.Counter(len(S[n]) for n in N)
    print(f"| {lab} | {st.mean(len(S[n]) for n in N):.1f} | {hit}/{npos} | {bad}/{nneg} | {dict(sorted(c.items()))} |")

# side by side
print("\n이름 | 선택 질문 상위 4 (확률) | 예/아니오 0.5↑")
for n in N:
    p = cp(n); rk = rank(p)[:4]
    print(f"{n} | " + ", ".join(f"{k} {p[k]:.2f}" for k in rk) + " | " + (", ".join(f"{k} {npb(n)[k]:.2f}" for k in rank(npb(n)) if npb(n)[k] >= .5) or "—"))

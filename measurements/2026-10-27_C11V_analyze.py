"""C11V 분석. 사전 등록 기준 그대로 계산한다."""
import json, os, statistics as st
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
F = lambda n, ext: os.path.join(D, f"2026-10-27_C11V_{n}.{ext}")

def items(n):
    return {it["id"]: it for it in json.load(open(F(n, "items.json")))}

def rows(n):
    out = defaultdict(list)
    for l in open(F(n, "jsonl")):
        r = json.loads(l)
        out[r["id"]].append(r["answers"])
    return out

def val(a):
    if a["type"] == "noul":
        return a["noul"]
    return a

def mean_ans(reps, q):
    return st.mean(val(r[q]) for r in reps)

def repdiff(reps, q):
    return abs(val(reps[0][q]) - val(reps[1][q])) if len(reps) > 1 else None

def choice_top(a):
    return a["choice"], a["probabilities"][a["choice"]]

M = lambda xs: round(st.mean(xs), 3) if xs else None
print("#################### K 각인 덱")
it = items("K1"); rw = rows("K1")
cell = {}  # (board, word) -> {role: v}
for iid, i in it.items():
    a = rw[iid][0]
    for wi, w in enumerate(i["meta"]["words"]):
        d = {}
        for l, role in i["meta"]["roles"].items():
            d[role] = val(a[f"w{wi}_{l}"])
        cell[(i["meta"]["board"], w)] = d
B_WORDS = ["inhuman", "toy", "machine", "alive", "broken", "monster", "plastic", "scary", "hostile", "amusement-park"]
C_WORDS = ["dangerous", "creepy", "rusty", "electric", "attacking", "wild", "out of control", "park attraction", "metal", "unwanted"]
def enemy_only(d):
    en = [v for r, v in d.items() if r.startswith("enemy")]
    return min(en) >= 0.6 and d["me"] <= 0.3 and d["bolt"] <= 0.3
def ally_hit(d):
    return max(d["me"], d["bolt"]) >= 0.6
eo_b = sum(enemy_only(cell[(b, w)]) for b in range(10) for w in B_WORDS)
print("K1 B낱말 적만침 칸:", eo_b, "/100")
for w in B_WORDS + C_WORDS:
    n = sum(enemy_only(cell[(b, w)]) for b in range(10))
    ah = sum(ally_hit(cell[(b, w)]) for b in range(10))
    gap = [M([v for r, v in cell[(b, w)].items() if r.startswith("enemy")]) - max(cell[(b, w)]["me"], cell[(b, w)]["bolt"]) for b in range(10)]
    en_mean = M([v for b in range(10) for r, v in cell[(b, w)].items() if r.startswith("enemy")])
    print(f"  {w:16s} 적만침 {n}/10  내편≥0.6 {ah}/10  적평균 {en_mean}  나평균 {M([cell[(b,w)]['me'] for b in range(10)])}  볼트평균 {M([cell[(b,w)]['bolt'] for b in range(10)])}  (적평균−내편최대)≥0.4 {sum(g>=0.4 for g in gap)}/10")
allc = [cell[(b, w)] for b in range(10) for w in B_WORDS + C_WORDS]
print("K1 내편≥0.6 칸 비율:", round(sum(ally_hit(d) for d in allc) / len(allc), 3))
print("K1 아무도 ≥0.6 아닌 칸 비율:", round(sum(max(d.values()) < 0.6 for d in allc) / len(allc), 3))
# per-enemy-description sanity: which enemies are hit by what
print("K1 판별 예시 (판0):")
b0 = items("K1")["k1-b0-g0"]["meta"]["roles"]; print("   roles", b0)

it = items("K2"); rw = rows("K2")
def k2vals(bi, cond):
    i = it[f"k2-b{bi}-{cond}"]; reps = rw[f"k2-b{bi}-{cond}"]
    out = {}
    for wi, w in enumerate(["wet", "sticky"]):
        for l, role in i["meta"]["roles"].items():
            out[(w, role)] = M([val(r[f"w{wi}_{l}"]) for r in reps])
    return out, i
rd = []
for bi in range(2):
    for cond in ["none", "soaked", "syrup", "blue", "partial"]:
        i = it[f"k2-b{bi}-{cond}"]; reps = rw[f"k2-b{bi}-{cond}"]
        for q in i["questions"]:
            rd.append(abs(val(reps[0][q]) - val(reps[1][q])))
print("K2 반복 차이 평균/최대:", M(rd), max(rd))
up_wet = up_sticky = 0; ctrl = []; leak = []; tot = 0
for bi in range(2):
    base, i = k2vals(bi, "none")
    so, _ = k2vals(bi, "soaked"); sy, _ = k2vals(bi, "syrup"); bl, _ = k2vals(bi, "blue"); pa, _ = k2vals(bi, "partial")
    roles = list(i["meta"]["roles"].values())
    order = [r for r, d in [(e[0], e[1]) for e in []]]
    for role in roles:
        tot += 1
        up_wet += so[("wet", role)] - base[("wet", role)] >= 0.3
        up_sticky += sy[("sticky", role)] - base[("sticky", role)] >= 0.3
        for w in ("wet", "sticky"):
            ctrl.append(abs(bl[(w, role)] - base[(w, role)]))
        print(f"  b{bi} {role:7s} wet {base[('wet',role)]:.2f}→soak {so[('wet',role)]:.2f} | sticky {base[('sticky',role)]:.2f}→syrup {sy[('sticky',role)]:.2f} | blue wet {bl[('wet',role)]:.2f} sticky {bl[('sticky',role)]:.2f} | partial wet {pa[('wet',role)]:.2f}")
print("K2 soaked→wet +0.3:", up_wet, "/", tot, " syrup→sticky +0.3:", up_sticky, "/", tot, " 대조 |Δ| 평균:", M(ctrl))
# leak: K2B index 0,1 modded -> roles enemy0, enemy1
for bi in range(2):
    base, i = k2vals(bi, "none"); pa, _ = k2vals(bi, "partial")
    for role in ["enemy2", "enemy3", "me", "bolt"]:
        leak.append(abs(pa[("wet", role)] - base[("wet", role)]))
    print(f"  partial b{bi} 꾸민 개체 wet:", [(r, round(base[('wet', r)], 2), round(pa[('wet', r)], 2)) for r in ["enemy0", "enemy1"]])
print("K2 누수 (꾸미지 않은 개체 wet |Δ| 평균):", M(leak), "최대", round(max(leak), 2))

def k3map(n):
    it = items(n); rw = rows(n); out = {}
    for iid, i in it.items():
        reps = rw[iid]
        for wi, w in enumerate(i["meta"]["words"]):
            for l, role in i["meta"]["roles"].items():
                out[(i["meta"]["board"], wi if n == "K3c" else w, role)] = M([val(r[f"w{wi}_{l}"]) for r in reps])
    return out
a = k3map("K3a"); b = k3map("K3b"); c = k3map("K3c"); dsh = k3map("K3d")
K3W = ["wet", "metal", "toy", "sticky", "inhuman"]
ab = [abs(a[k] - b[k]) for k in a]
print("K3 묶음 vs 따로 |Δ| 평균:", M(ab), "최대", round(max(ab), 2))
ko = []; top_match = 0; top_n = 0
for bi in range(2):
    for wi, w in enumerate(K3W):
        en = {k[2]: v for k, v in a.items() if k[0] == bi and k[1] == w}
        kr = {k[2]: v for k, v in c.items() if k[0] == bi and k[1] == wi}
        for r in en: ko.append(abs(en[r] - kr[r]))
        top_n += 1; top_match += max(en, key=en.get) == max(kr, key=kr.get)
        print(f"   b{bi} {w:8s} EN {{{', '.join(f'{r}:{en[r]:.2f}' for r in sorted(en))}}}  KO {{{', '.join(f'{r}:{kr[r]:.2f}' for r in sorted(kr))}}}")
print("K3 한영 |Δ| 평균:", M(ko), " 1위 일치:", top_match, "/", top_n)
shd = [abs(a[k] - dsh[k]) for k in a]
print("K3 섞기 |Δ| 평균:", M(shd), "최대", round(max(shd), 2))

print("\n#################### W 위장 단어")
it = items("W1"); rw = rows("W1")
cells = []; cr = []; gr = []
for iid, i in it.items():
    reps = rw[iid]
    for k in ROOMKEYS if False else ["typical", "fit", "misfit", "far", "chair", "box", "dup", "odd"]:
        g = M([val(r[f"g_{k}"]) for r in reps]); c = M([val(r[f"c_{k}"]) for r in reps])
        cells.append((iid, k, g, c))
        cr.append(abs(val(reps[0][f"c_{k}"]) - val(reps[1][f"c_{k}"])))
        gr.append(abs(val(reps[0][f"g_{k}"]) - val(reps[1][f"g_{k}"])))
grey = [x for x in cells if 0.25 <= x[2] < 0.55]
print("W1 구간: 즉시들킴", sum(x[2] < 0.25 for x in cells), " 회색", len(grey), " 통과", sum(x[2] >= 0.55 for x in cells), " / ", len(cells))
print("W1 회색 중 close≥0.5:", sum(x[3] >= 0.5 for x in grey), "/", len(grey))
print("W1 평균(close−glance):", M([x[3] - x[2] for x in cells]))
print("W1 close 반복차 평균:", M(cr), "최대", max(cr), " glance 반복차 평균:", M(gr))
gs = [x[2] for x in cells]; cs = [x[3] for x in cells]
print("W1 상관 r(glance, close):", round(st.correlation(gs, cs), 3))
by_k = defaultdict(list)
for x in cells: by_k[x[1]].append(x[2])
print("W1 종류별 glance 평균:", {k: M(v) for k, v in by_k.items()})
for x in cells: print("   ", x[0], x[1], round(x[2], 2), round(x[3], 2))
# single vs batch
its = items("W1s"); rws = rows("W1s")
bmap = {(x[0], x[1]): (x[2], x[3]) for x in cells}
sd = []; chkd = []; chk_fail = 0
for iid, i in its.items():
    a = rws[iid][0]; room = i["meta"]["room"]; k = i["meta"]["k"]
    bg, bc = bmap[(f"w1-{room}-event", k)]
    if i["cond"] == "single_chk":
        sd.append(abs(val(a["glance"]) - bg))
        t, p = choice_top(a["check"]); chk_fail += (t != "describes" and p >= 0.5)
        print(f"   단독 {room:8s} {k:7s} glance {val(a['glance']):.2f} (묶음 {bg:.2f}) close {val(a['close']):.2f} (묶음 {bc:.2f}) check {t} {p:.2f}")
for iid, i in its.items():
    if i["cond"] == "single_nochk":
        room = i["meta"]["room"]; a = rws[iid][0]; b = rws[f"w1s-{room}-fit-chk"][0]
        chkd.append(abs(val(a["glance"]) - val(b["glance"]))); chkd.append(abs(val(a["close"]) - val(b["close"])))
print("W1s 단독 vs 묶음 glance |Δ| 평균:", M(sd), "최대", round(max(sd), 2), " 정상 위장 검문소 오탐:", chk_fail, "/12")
print("W1s check 있음/없음 |Δ| 평균:", M(chkd), "최대", round(max(chkd), 2))

it = items("W2"); rw = rows("W2")
for room in ["bath", "kitchen", "banquet"]:
    a = mean_ans(rw[f"w2-{room}-a"], "g_me")
    bme = mean_ans(rw[f"w2-{room}-b"], "g_me"); bo1 = mean_ans(rw[f"w2-{room}-b"], "g_o1"); bo2 = mean_ans(rw[f"w2-{room}-b"], "g_o2")
    cme = mean_ans(rw[f"w2-{room}-c"], "g_me"); cd = mean_ans(rw[f"w2-{room}-c"], "g_dup"); co1 = mean_ans(rw[f"w2-{room}-c"], "g_o1")
    print(f"W2 {room:8s} a {a:.2f} | b me {bme:.2f} o1 {bo1:.2f} o2 {bo2:.2f} | c first {cme:.2f} second {cd:.2f} o1 {co1:.2f}")

it = items("W3ko"); rw = rows("W3ko")
kd = []; zone = 0; zn = 0
z = lambda v: 0 if v < 0.25 else (1 if v < 0.55 else 2)
for iid, i in it.items():
    reps = rw[iid]
    line = []
    for k in ["typical", "fit", "misfit", "far", "chair", "odd"]:
        e = mean_ans(reps, f"en_{k}"); kk = mean_ans(reps, f"ko_{k}")
        kd.append(abs(e - kk)); zn += 1; zone += z(e) == z(kk)
        line.append(f"{k} {e:.2f}/{kk:.2f}")
    print("  ", iid, " | ".join(line))
print("W3 한영 |Δ| 평균:", M(kd), " 구간 일치:", zone, "/", zn)
it = items("W3gen"); rw = rows("W3gen")
GEN = ["dust", "a shadow", "a cobweb", "a stain on the floor", "some trash", "a plastic bag"]
gpass = defaultdict(int); cl = defaultdict(list)
for iid in it:
    a = rw[iid][0]
    print("  ", iid, {q: round(val(v), 2) for q, v in a.items()})
    for gi in range(6): gpass[GEN[gi]] += val(a[f"gen{gi}"]) >= 0.55
    for ci in range(2): cl[ci].append(val(a[f"cl{ci}"]))
print("W3 만능 후보 통과 방 수(/6):", dict(gpass))
print("W3 주장형 glance ≤0.4 방 수:", {ci: sum(v <= 0.4 for v in vs) for ci, vs in cl.items()}, {ci: [round(v, 2) for v in vs] for ci, vs in cl.items()})
it = items("W3chk"); rw = rows("W3chk")
caught = 0
for iid in it:
    t, p = choice_top(rw[iid][0]["check"]); caught += (t != "describes" and p >= 0.5)
    print("  ", iid, t, round(p, 2), rw[iid][0]["check"]["probabilities"])
print("W3 주장형 검문소 걸림:", caught, "/6")

print("\n#################### D 딜러")
rw = rows("D1")
d1 = {k: (mean_ans(v, "bluff"), repdiff(v, "bluff")) for k, v in rw.items()}
for k, v in d1.items(): print(f"  {k:10s} bluff {v[0]:.3f} (반복차 {v[1]:.2f})")
for L in (2, 5, 8):
    a, b, c = d1[f"d1-L{L}-a"][0], d1[f"d1-L{L}-b"][0], d1[f"d1-L{L}-c"][0]
    print(f"D1 L{L}: a−b {a-b:.3f}  c {c:.3f} (a {a:.2f}, b {b:.2f}) c가 b쪽: {abs(c-b) < abs(c-a)} 사이: {min(a,b) <= c <= max(a,b)}")
print("D1 무관−없음:", round(d1["d1-ctrl"][0] - d1["d1-none"][0], 3))

rw = rows("D2")
for k, reps in rw.items():
    tops = [choice_top(r["notice"]) for r in reps]
    probs = {kk: round(st.mean(r["notice"]["probabilities"][kk] for r in reps), 2) for kk in reps[0]["notice"]["probabilities"]}
    print(f"  {k:10s} notice {[t for t, p in tops]} 평균확률 {probs}  bluff {mean_ans(reps, 'bluff'):.2f}")

rw = rows("D3"); it = items("D3")
base = mean_ans(rw["d3-00-none"], "bluff")
print(f"D3 말 없음 bluff {base:.3f}")
d3b = {}
for iid, reps in rw.items():
    b = mean_ans(reps, "bluff"); d3b[iid] = b
    chk = [choice_top(r["check"]) for r in reps] if "check" in reps[0] else None
    nt = [choice_top(r["notice"])[0] for r in reps]
    print(f"  {iid:20s} bluff {b:.3f} (Δ {b-base:+.3f}, 반복차 {repdiff(reps,'bluff'):.2f}) check {chk} notice {nt}")
pairs = []
for p in range(3):
    c = [v for k, v in d3b.items() if f"p{p}_clumsy" in k][0]; q = [v for k, v in d3b.items() if f"p{p}_polish" in k][0]
    pairs.append(abs(c - q)); print(f"D3 쌍{p} 서툰 {c:.3f} 매끄러운 {q:.3f} |Δ| {abs(c-q):.3f}")
print("D3 쌍 |Δ| 평균:", M(pairs))

rw = rows("D4")
for k, reps in rw.items():
    print(f"  {k} bluff {mean_ans(reps,'bluff'):.3f} reps {[val(r['bluff']) for r in reps]} check {[choice_top(r['check']) for r in reps]} notice {[choice_top(r['notice'])[0] for r in reps]}")
print("D4 (ii)−(i):", round(mean_ans(rw["d4-ii"], "bluff") - mean_ans(rw["d4-i"], "bluff"), 3),
      " 참고 D3 같은 말·기록 없음:", round(d3b["d3-01-normal"], 3))
d4 = rw
rw = rows("D4i"); it = items("D4i")
inter = []
for iid, i in it.items():
    v = val(rw[iid][0]["bluff"]); pair = i["meta"]["pair"]
    ref = d3b[pair] if pair.startswith("d3") else mean_ans(d4["d4-ii"], "bluff")
    inter.append(abs(v - ref)); print(f"  간섭 {iid}: 단독 {v:.2f} vs 묶음 {ref:.2f}")
print("D4i 간섭 |Δ| 평균:", M(inter))

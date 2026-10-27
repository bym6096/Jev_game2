import json, statistics as st, sys
L = lambda f: [json.loads(l) for l in open(f)]
base = L("2026-10-27_C9-M1x_gate_base.jsonl"); var = L("2026-10-27_C9-M1x_gate_var.jsonl"); x0 = L("2026-10-27_C9-M1x_x0.jsonl")
items = {i["id"]: i for i in json.load(open("2026-10-27_C9-M1x_gate_base.items.json")) + json.load(open("2026-10-27_C9-M1x_gate_var.items.json"))}
exec(open("2026-10-27_C9-M1x_gate_build.py").read().split("RULES =")[0])  # P1,P2
POOLS = {"P1": P1, "P2": P2}
v = lambda r: {k: a["noul"] for k, a in r["answers"].items()}
B = {}
for r in base: B.setdefault(r["id"], []).append(v(r))
out = {}
allv = [x for reps in B.values() for x in reps[0].values()]
gray = sum(0.25 <= x <= 0.75 for x in allv) / len(allv)
repd = [abs(B[i][0][k] - B[i][1][k]) for i in B for k in B[i][0]]
graystable = [abs(B[i][0][k]-B[i][1][k]) for i in B for k in B[i][0] if 0.25 <= B[i][0][k] <= 0.75]
both_gray = sum(1 for i in B for k in B[i][0] if 0.25<=B[i][0][k]<=0.75 and 0.25<=B[i][1][k]<=0.75)
print(f"G1 gray share rep0 {gray:.3f} (n={len(allv)}); rep1 {sum(0.25<=x<=0.75 for reps in B.values() for x in reps[1].values())/len(allv):.3f}; both reps gray {both_gray}")
print(f"   rep |d| mean {st.mean(repd):.3f} max {max(repd):.3f}; within gray mean {st.mean(graystable):.3f}")
hist = [0]*10
for x in allv: hist[min(9,int(x*10))]+=1
print("   histogram deciles", hist)
for i in B:
    vals = B[i][0]; m = {k:(B[i][0][k]+B[i][1][k])/2 for k in vals}
    pool = POOLS[items[i]["pool"]]
    g = [f"{pool[int(k[1:])-1][:28]}={m[k]:.2f}" for k in vals if 0.25<=m[k]<=0.75]
    print(f" {i} [{items[i]['rule']}] gray {len(g)}: {'; '.join(g)}")
mean = lambda i: {k:(B[i][0][k]+B[i][1][k])/2 for k in B[i][0]}
V = {r["id"]: v(r) for r in var}
def cmp(tag):
    res = []
    for vid in sorted(V):
        if not vid.endswith(tag): continue
        rid = vid.split("-")[1]; b = mean(f"G-{rid}"); d = {k: V[vid][k]-b[k] for k in b}
        k2 = sum(abs(x)>=0.2 for x in d.values()); md = st.mean(abs(x) for x in d.values())
        pool = POOLS[items[vid]["pool"]]
        top = sorted(d.items(), key=lambda kv: -abs(kv[1]))[:4]
        print(f" {vid} [{items['G-'+rid]['rule']} -> {items[vid]['rule']}] n|d|>=0.2={k2} mean|d|={md:.3f} top: " + "; ".join(f"{pool[int(k[1:])-1][:26]} {b[k]:.2f}->{V[vid][k]:.2f}" for k,_ in top))
        res.append((k2, md))
    return res
print("G2 one-word"); ow = cmp("-ow")
print("G3 paraphrase"); pa = cmp("-pa")
print(f"G2 pairs with 2..10 movers: {sum(2<=k<=10 for k,_ in ow)}/8; mean|d| {st.mean(m for _,m in ow):.3f}")
print(f"G3 pairs with <=2 movers: {sum(k<=2 for k,_ in pa)}/8; >=5 movers: {sum(k>=5 for k,_ in pa)}; mean|d| {st.mean(m for _,m in pa):.3f}")
# X0
print("X0")
for cond in ["x0_alone_q", "x0_single_state"]:
    ds = []
    for r in x0:
        if r["cond"] != cond: continue
        rid = r["id"].split("-")[1]; k = list(r["answers"])[0]
        b = mean(f"G-{rid}")[k]; x = r["answers"][k]["noul"]; ds.append(x-b)
        print(f"  {r['id']}: batch {b:.2f} -> {x:.2f}")
    print(f" {cond}: mean|d| {st.mean(map(abs,ds)):.3f} max {max(map(abs,ds)):.3f} signed mean {st.mean(ds):+.3f}")
ds=[]
for r in x0:
    if r["cond"]=="x0_reversed":
        rid=r["id"].split("-")[1]; b=mean(f"G-{rid}")
        ds += [abs(r["answers"][k]["noul"]-b[k]) for k in b]
print(f" reversed order: mean|d| {st.mean(ds):.3f} max {max(ds):.3f} n>=0.2 {sum(d>=0.2 for d in ds)}/{len(ds)}")
# latency by question count
lat = {}
for f in ["2026-10-27_C9-M1x_gate_base.jsonl","2026-10-27_C9-M1x_gate_var.jsonl","2026-10-27_C9-M1x_x0.jsonl"]:
    for r in L(f): lat.setdefault(len(r["answers"]), []).append(r["latency_ms"])
for n in sorted(lat):
    s = sorted(lat[n]); print(f" latency q={n}: n={len(s)} p50 {s[len(s)//2]} p95 {s[min(len(s)-1,int(0.95*len(s)))]} max {s[-1]}")

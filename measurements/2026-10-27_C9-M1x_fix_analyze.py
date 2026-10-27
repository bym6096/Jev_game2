import json, math, statistics as stt
R = {json.loads(l)["id"]: json.loads(l)["answers"] for l in open("2026-10-27_C9-M1x_fix.jsonl")}
lg = lambda p: math.log(min(.99, max(.01, p)) / (1 - min(.99, max(.01, p)))); sg = lambda x: 1/(1+math.exp(-x))
print("F4 plain-sentence fire")
for cid in ["I1", "I2", "I3", "I4", "I5", "C1"]:
    p0, pa, pb, pab = (R[f"F4-{cid}-{c}"]["target"]["noul"] for c in ["base", "A", "B", "AB"])
    pred = sg(lg(pa) + lg(pb) - lg(p0))
    print(f"  {cid}: base {p0:.2f} A {pa:.2f} B {pb:.2f} AB {pab:.2f} pred {pred:.2f} resid {pab-pred:+.2f}")
exec(open("2026-10-27_C9-M1x_gate_build.py").read().split("RULES =")[0])
A = {k: (R["G4-P2-alive-edible"][k]["noul"] + R["G4-P2-alive-edible#rep"][k]["noul"]) / 2 for k in R["G4-P2-alive-edible"]}
D = {k: (R["G4-P2-dangerous"][k]["noul"] + R["G4-P2-dangerous#rep"][k]["noul"]) / 2 for k in R["G4-P2-dangerous"]}
base = {}
for l in open("2026-10-27_C9-M1x_gate_base.jsonl"):
    r = json.loads(l)
    if r["id"] in ("G-R9", "G-R8"):
        for k, a in r["answers"].items(): base.setdefault((r["id"], k), []).append(a["noul"])
print("G4 atomic: alive, edible, OR(code)=1-(1-a)(1-e), combined-rule R9 value; dangerous vs R8")
gray_or = gray_r9 = 0
for i in range(1, 21):
    a, e = A[f"alive{i}"], A[f"edible{i}"]; orc = 1 - (1 - a) * (1 - e); r9 = stt.mean(base[("G-R9", f"a{i}")]); r8 = stt.mean(base[("G-R8", f"a{i}")])
    gray_or += .25 <= orc <= .75; gray_r9 += .25 <= r9 <= .75
    print(f"  {P2[i-1][:26]:26} alive {a:.2f} edible {e:.2f} OR {orc:.2f} | R9 {r9:.2f} || dangerous {D[f'dangerous{i}']:.2f} R8 {r8:.2f}")
print(f"gray OR(code) {gray_or}/20 vs R9 {gray_r9}/20; dangerous gray {sum(.25<=v<=.75 for v in D.values())}/20")

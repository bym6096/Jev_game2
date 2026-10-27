import json, statistics as stt
R = {}
for l in open("2026-10-27_C9-M1x_lobby.jsonl"):
    r = json.loads(l); R[r["id"]] = {k: a["probabilities"] for k, a in r["answers"].items()}
O = ["left", "right", "stop", "ask_staff"]; DEST = {"late_office": "left", "elderly": "left", "students": "right", "riders": "right", "family": "left", "nurses": "right"}
tvd = lambda p, q: 0.5 * sum(abs(p[o] - q[o]) for o in O)
dest_ok = n = 0; sel = []; inter = 0; noise = []; form = []
for j in ["J1", "J2", "J3"]:
    print(j)
    for g in DEST:
        p0, pa, pb, pab = (R[f"L-{j}-{c}"][g] for c in ["none", "A", "B", "AB"])
        z = {o: pa[o] * pb[o] / max(p0[o], .01) for o in O}; s = sum(z.values()); poe = {o: z[o] / s for o in O}
        dest_ok += max(p0, key=p0.get) == DEST[g]; n += 1
        noise.append(tvd(p0, R[f"L-{j}-none#rep"][g])); form.append(tvd(p0, R[f"L-{j}-none#random"][g]))
        inter += tvd(pab, poe) > .15
        f = lambda p: "/".join(f"{p[o]:.2f}" for o in O)
        print(f"  {g:11} none {f(p0)} A {f(pa)} B {f(pb)} AB {f(pab)} | tvdA {tvd(p0,pa):.2f} tvdB {tvd(p0,pb):.2f} AB-vs-PoE {tvd(pab,poe):.2f}")
    for c in ["A", "B"]:
        k = sum(tvd(R[f"L-{j}-none"][g], R[f"L-{j}-{c}"][g]) >= .15 for g in DEST); sel.append(k); print(f"  sign {c}: groups moved TVD>=0.15: {k}")
print(f"dest top-1 {dest_ok}/{n}; selective(2..4) {sum(2<=k<=4 for k in sel)}/6 {sel}; AB-vs-PoE>0.15 {inter}/18; noise TVD mean {stt.mean(noise):.3f} max {max(noise):.2f}; most-vs-random TVD mean {stt.mean(form):.3f} max {max(form):.2f}")

"""Post-hoc fix checks (added after main results, logged as such).
F4: W7-01 non-additivity in plain-sentence format. G4: W7-02 atomic tile questions."""
import json
exec(open("2026-10-27_C9-M1x_fire_build.py").read().split("def st")[0])  # CASES
exec(open("2026-10-27_C9-M1x_gate_build.py").read().split("RULES =")[0])  # P1, P2
items = []
for cid, t, a, b, exp in [c for c in CASES if c[0] in ("I1", "I2", "I3", "I4", "I5", "C1")]:
    for cond, ns in [("base", ["a stack of bricks"]), ("A", [a]), ("B", [b]), ("AB", [a, b])]:
        s = (f"In a dry storage room, {t} sits on a concrete floor, touching a wool blanket that is burning fiercely. "
             f"Right next to {t}: " + " and ".join(ns) + ".")
        items.append({"id": f"F4-{cid}-{cond}", "cond": cond, "state": s,
                      "questions": {"target": {"type": "noul", "instructions": f"Within the next minute, does {t} catch fire?"}}})
def gstate(arr):
    return "Items arriving at a quarantine gate: " + " ".join(f"({i+1}) {a}," for i, a in enumerate(arr)).rstrip(",") + "."
for rep in range(2):
    items.append({"id": "G4-P2-alive-edible" + ("#rep" if rep else ""), "cond": "atomic", "state": gstate(P2),
                  "questions": {**{f"alive{i}": {"type": "noul", "instructions": f"Is arrival ({i}) alive?"} for i in range(1, 21)},
                                **{f"edible{i}": {"type": "noul", "instructions": f"Is arrival ({i}) edible?"} for i in range(1, 21)}}})
    items.append({"id": "G4-P2-dangerous" + ("#rep" if rep else ""), "cond": "atomic", "state": gstate(P2),
                  "questions": {f"dangerous{i}": {"type": "noul", "instructions": f"Is arrival ({i}) dangerous?"} for i in range(1, 21)}})
json.dump(items, open("2026-10-27_C9-M1x_fix.items.json", "w"), indent=1); print(len(items))

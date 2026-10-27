"""C9-M1a (W7-02 gate) + C9-M1X (X0 interference/latency) item builder."""
import json
P1 = ["a wind-up music box", "a potted cactus", "a sleeping puppy in a crate", "a power bank",
      "a toy drone with its battery removed", "a birthday cake with candles", "a cordless electric drill",
      "a jar of live sourdough starter", "a child's drawing of a bomb", "a buzzing cooler box",
      "a box of kitchen knives", "a solar-powered garden gnome", "a bag of fresh oysters",
      "a pair of noise-cancelling headphones", "a goldfish in a plastic bag", "a mechanical pocket watch",
      "a vacuum-sealed pack of beef jerky", "a pair of ice skates", "an e-reader", "a bouquet of fresh tulips"]
P2 = ["a bottle of olive oil", "a sealed can of hairspray", "a garden hose", "a jar of honey with a dead bee in it",
      "a laptop with a cracked screen", "a parrot that can say 'fire'", "a bag of fertilizer", "a ceramic kitchen knife",
      "a pair of steel scissors", "a tube of toothpaste", "a snow globe", "a box of matches", "a frozen turkey",
      "a toy water pistol", "a hamster in a cage", "a beekeeping suit", "a bottle of perfume",
      "a camping gas stove", "a packet of flower seeds", "a pocket calculator"]
RULES = {  # id: (pool, rule)
 "R1": ("P1", "BLOCK: electric"), "R2": ("P1", "BLOCK: alive"), "R3": ("P1", "BLOCK: sharp OR electric"),
 "R4": ("P1", "ADMIT: edible"), "R5": ("P1", "BLOCK: makes noise"),
 "R6": ("P2", "BLOCK: flammable"), "R7": ("P2", "BLOCK: liquid"), "R8": ("P2", "ADMIT: NOT dangerous"),
 "R9": ("P2", "BLOCK: alive OR edible"), "R10": ("P2", "BLOCK: sharp")}
ONEWORD = {"R1": "BLOCK: electric moving", "R2": "BLOCK: alive small", "R3": "BLOCK: sharp AND electric",
 "R4": "ADMIT: edible fresh", "R5": "BLOCK: makes loud noise", "R6": "BLOCK: explosive",
 "R7": "BLOCK: liquid edible", "R8": "ADMIT: NOT sharp"}
PARA = {"R1": "BLOCK: anything that runs on electricity", "R2": "BLOCK: living things",
 "R3": "BLOCK: electric OR sharp", "R4": "ADMIT: things that can be eaten", "R5": "BLOCK: noisy",
 "R6": "BLOCK: catches fire easily", "R7": "BLOCK: anything liquid", "R8": "ADMIT: harmless"}
POOLS = {"P1": P1, "P2": P2}
def state(rule, arrivals, idx=None):
    idx = idx or list(range(1, len(arrivals) + 1))
    lst = " ".join(f"({i}) {a}," for i, a in zip(idx, arrivals)).rstrip(",") + "."
    return (f"Quarantine gate rule: \"{rule}\". The rule is applied literally by the gate staff. "
            f"Arrivals in line: {lst}")
def q(i): return {"type": "noul", "instructions": f"Does the gate rule apply to arrival ({i})?"}
def batch(rule, pool, order=None):
    n = len(POOLS[pool]); order = order or list(range(1, n + 1))
    return {f"a{i}": q(i) for i in order}
base, var, x0 = [], [], []
for rid, (pool, rule) in RULES.items():
    base.append({"id": f"G-{rid}", "cond": "base", "rule": rule, "pool": pool,
                 "state": state(rule, POOLS[pool]), "questions": batch(rule, pool)})
for rid, rule in ONEWORD.items():
    pool = RULES[rid][0]
    var.append({"id": f"G-{rid}-ow", "cond": "oneword", "rule": rule, "pool": pool,
                "state": state(rule, POOLS[pool]), "questions": batch(rule, pool)})
for rid, rule in PARA.items():
    pool = RULES[rid][0]
    var.append({"id": f"G-{rid}-pa", "cond": "para", "rule": rule, "pool": pool,
                "state": state(rule, POOLS[pool]), "questions": batch(rule, pool)})
# X0: rules R1 R2 R6 R7 R9, arrivals 1, 10, 16 (pre-registered positions)
for rid in ["R1", "R2", "R6", "R7", "R9"]:
    pool, rule = RULES[rid]
    for k in [1, 10, 16]:
        x0.append({"id": f"X-{rid}-a{k}-alone", "cond": "x0_alone_q", "state": state(rule, POOLS[pool]),
                   "questions": {f"a{k}": q(k)}})
        x0.append({"id": f"X-{rid}-a{k}-single", "cond": "x0_single_state",
                   "state": state(rule, [POOLS[pool][k - 1]], [k]), "questions": {f"a{k}": q(k)}})
    x0.append({"id": f"X-{rid}-rev", "cond": "x0_reversed", "state": state(rule, POOLS[pool]),
               "questions": batch(rule, pool, list(range(20, 0, -1)))})
both = P1 + P2
for j, rule in enumerate(["BLOCK: electric", "BLOCK: alive", "BLOCK: sharp"]):
    x0.append({"id": f"X-lat40-{j}", "cond": "x0_lat40", "state": state(rule, both),
               "questions": {f"a{i}": q(i) for i in range(1, 41)}})
json.dump(base, open("2026-10-27_C9-M1x_gate_base.items.json", "w"), indent=1)
json.dump(var, open("2026-10-27_C9-M1x_gate_var.items.json", "w"), indent=1)
json.dump(x0, open("2026-10-27_C9-M1x_x0.items.json", "w"), indent=1)
print(len(base), len(var), len(x0))

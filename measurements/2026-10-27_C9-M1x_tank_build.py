"""C9-M1f W7-06 aquarium: 3-way effects and junk reactions."""
import json
T = {
 "T1": ([("guppies", 3), ("green algae", 3), ("pond snails", 2), ("cherry shrimp", 2)], "a timer LED light (on 14 hours a day)", "an old copper coin"),
 "T2": ([("goldfish", 2), ("duckweed", 3), ("ramshorn snails", 3), ("java moss", 2)], "an air pump bubbler", "a heater set to 32°C"),
 "T3": ([("neon tetras", 3), ("hornwort", 2), ("cherry shrimp", 3), ("green algae", 2)], "a betta fish", "a dense thicket of java moss"),
}
JUNK = {"salt": ("a handful of aquarium salt", "active"), "oak": ("a dried oak leaf", "active"), "radio": ("a radio playing all night right next to the tank", "active"),
        "castle": ("a ceramic castle ornament", "inert"), "diver": ("a plastic toy diver", "inert"), "magnet": ("a magnet stuck to the outside of the glass", "inert")}
CR = {"vanishes": None, "shrinks": None, "holds": None, "grows": None, "takes_over": None}
def Q(occ):
    q = {o.replace(" ", "_"): {"type": "choice", "instructions": f"Next season, what happens to the {o} population?", "criteria": CR} for o, _ in occ}
    q["clear"] = {"type": "noul", "instructions": "Will the water be clear next season?"}
    return q
def st(occ, objs):
    s = "A 60-liter home aquarium. Occupants and population levels (0 none - 4 overrun): " + ", ".join(f"{o} {n}" for o, n in occ) + "."
    return s + (" Also in or by the tank: " + "; ".join(objs) + "." if objs else " Nothing else is in the tank.")
items = []
for tid, (occ, X, Y) in T.items():
    for c, objs in [("base", []), ("X", [X]), ("Y", [Y]), ("XY", [X, Y])]:
        items.append({"id": f"T-{tid}-{c}", "cond": c, "state": st(occ, objs), "questions": Q(occ)})
    for c, objs in [("base", []), ("XY", [X, Y])]:
        items.append({"id": f"T-{tid}-{c}#rep", "cond": c + "_rep", "state": st(occ, objs), "questions": Q(occ)})
for jid, (j, kind) in JUNK.items():
    items.append({"id": f"T-T1-junk-{jid}", "cond": "junk_" + kind, "state": st(T["T1"][0], [j]), "questions": Q(T["T1"][0])})
json.dump(items, open("2026-10-27_C9-M1x_tank.items.json", "w"), indent=1); print(len(items))

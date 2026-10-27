"""C9-M1c W7-04 needle: cumulative cards, singletons, reversed order, repeats."""
import json
SC = {
 "bridge": ("Scene: An old wooden footbridge over a river. A marching band of 40 people is about to cross it in step.",
            "Does the footbridge hold while the whole band crosses it?",
            [("It has rained heavily all week.", "-"), ("The band members wear rubber boots.", "0"),
             ("Army engineers reinforced the bridge last month.", "+"), ("200 spectators follow the band onto the bridge.", "-"),
             ("The band has been told to break step while crossing.", "+"), ("A flock of seagulls is sitting on the railing.", "0")]),
 "balloon": ("Scene: A hot-air balloon with three passengers is trying to fly over a hill and land in the meadow beyond.",
             "Does the balloon land safely in the meadow?",
             [("The pilot has 20 years of experience.", "+"), ("A thunderstorm is forming to the west.", "-"),
              ("One passenger is afraid of heights.", "0"), ("They carry extra propane tanks.", "+"),
              ("Power lines run along the edge of the meadow.", "-"), ("The balloon's fabric was patched last week.", "-")]),
 "cake": ("Scene: A three-tier wedding cake must be carried across a crowded garden party to the main table.",
          "Does the cake arrive at the main table intact?",
          [("It is a very hot afternoon and the cake has buttercream icing.", "-"), ("The two people carrying it are professional caterers.", "+"),
           ("A dog is running loose among the guests.", "-"), ("The cake has internal dowel supports.", "+"),
           ("The band starts playing a waltz.", "0"), ("The path is paved with uneven cobblestones.", "-")]),
}
def st(base, cards):
    if not cards: return base
    return base + " Added facts: " + " ".join(f"({i+1}) {c}" for i, c in enumerate(cards))
items = []
for sid, (base, q, cards) in SC.items():
    Q = {"needle": {"type": "noul", "instructions": q}}
    cs = [c for c, _ in cards]
    for k in range(7):
        items.append({"id": f"N-{sid}-cum{k}", "cond": "cum", "state": st(base, cs[:k]), "questions": Q})
    for k in range(6):
        items.append({"id": f"N-{sid}-single{k+1}", "cond": "single", "exp": cards[k][1], "state": st(base, [cs[k]]), "questions": Q})
    items.append({"id": f"N-{sid}-rev", "cond": "rev", "state": st(base, cs[::-1]), "questions": Q})
    items.append({"id": f"N-{sid}-cum0#rep", "cond": "rep", "state": st(base, []), "questions": Q})
    items.append({"id": f"N-{sid}-cum6#rep", "cond": "rep", "state": st(base, cs), "questions": Q})
json.dump({"scenes": {k: [c for c in v[2]] for k, v in SC.items()}}, open("2026-10-27_C9-M1x_needle.meta.json", "w"), indent=1)
json.dump(items, open("2026-10-27_C9-M1x_needle.items.json", "w"), indent=1); print(len(items))

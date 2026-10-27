"""C9-M1b W7-01 fire lab: non-additivity of neighbor pairs."""
import json
NEUT_E, NEUT_W = "a ceramic flower pot", "a stack of bricks"
CASES = [  # id, target, A (east), B (west), expected
 ("I1", "a cardboard box of old letters", "an open sack of flour", "an electric fan, switched on, blowing across the room", "interaction+"),
 ("I2", "a wooden crate of books", "a lump of sodium metal in a dish", "a bucket of water", "interaction+"),
 ("I3", "a cardboard box of old letters", "an aerosol can of hairspray", "an electric space heater, switched on", "interaction+"),
 ("I4", "a pile of laundry", "a pile of oily rags", "a leaking oxygen cylinder", "interaction+"),
 ("I5", "a wooden chair", "a bucket of sand", "a bucket of water", "interaction?"),
 ("C1", "a cardboard box of old letters", "a glass jar of marbles", "a pile of dry newspapers", "control"),
 ("C2", "a wooden chair", "a pile of dry newspapers", "a wooden pallet", "control"),
 ("C3", "a pile of laundry", "a bucket of sand", "a closed metal filing cabinet", "control"),
]
def st(target, east, west):
    return (f"Phenomenon: FIRE. A 3x3 patch of a storage room seen from above. CENTER (TARGET): {target}. "
            f"NORTH: a wool blanket, currently burning. EAST: {east}. SOUTH: a closed metal toolbox. WEST: {west}. "
            "Corners: bare concrete floor. The room is dry and there is no wind.")
Q = {"target": {"type": "noul", "instructions": "Within the next minute, does the fire reach and ignite the TARGET?"}}
items, rep = [], []
for cid, t, a, b, exp in CASES:
    for cond, e, w in [("base", NEUT_E, NEUT_W), ("A", a, NEUT_W), ("B", NEUT_E, b), ("AB", a, b), ("AB_swap", b, a)]:
        items.append({"id": f"F-{cid}-{cond}", "cond": cond, "exp": exp, "state": st(t, e, w), "questions": Q})
    rep.append({"id": f"F-{cid}-AB", "cond": "AB_rep", "exp": exp, "state": st(t, a, b), "questions": Q})
json.dump(items + rep, open("2026-10-27_C9-M1x_fire.items.json", "w"), indent=1)
print(len(items + rep))

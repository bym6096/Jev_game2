"""C9-M1d W7-03 headline market."""
import json
GOODS = {"fans": "electric fans", "candles": "candles", "coolers": "cooler boxes", "sunscreen": "sunscreen",
         "umbrellas": "umbrellas", "peaches": "canned peaches", "vinyl": "second-hand vinyl records", "locks": "bicycle locks"}
H = {"H0": "City library extends weekend opening hours", "H1": "Record heatwave expected all week",
     "H2": "Fire at main power substation, outages likely for days", "H3": "Typhoon to hit the coast this weekend",
     "H4": "Beloved local singer dies at 74", "H5": "Bicycle thefts triple downtown, police say",
     "H6": "Food safety scare: canned fruit recalled nationwide"}
CR = {"crash": "demand falls sharply", "fall": "demand falls", "flat": "about the same", "rise": "demand rises", "surge": "demand rises sharply"}
Q = {k: {"type": "choice", "instructions": f"How does demand for {g} at the market change tomorrow?", "criteria": CR} for k, g in GOODS.items()}
def st(hs):
    fp = "Today's front page has no major news." if not hs else "Today's front page headlines: " + " ".join(f"({i+1}) \"{H[h]}\"" for i, h in enumerate(hs))
    return f"A mid-sized coastal city. {fp} Goods sold at the city market: " + ", ".join(GOODS.values()) + "."
conds = {"base": [], "H0": ["H0"], **{f"H{i}": [f"H{i}"] for i in range(1, 7)},
         "P1": ["H1", "H2"], "P2": ["H3", "H4"], "P3": ["H1", "H3"], "P4": ["H2", "H5"]}
items = [{"id": f"M-{c}", "cond": c, "state": st(h), "questions": Q} for c, h in conds.items()]
items += [{"id": f"M-{c}#rep", "cond": c + "_rep", "state": st(conds[c]), "questions": Q} for c in ["base", "H1", "H2", "P1"]]
json.dump(items, open("2026-10-27_C9-M1x_market.items.json", "w"), indent=1); print(len(items))

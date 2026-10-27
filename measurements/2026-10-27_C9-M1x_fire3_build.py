"""Post-hoc rescue check for W7-01: (a) choice time-to-ignite on grid state, (b) plain-sentence state with noul."""
import json
src = {i["id"]: i for i in json.load(open("2026-10-27_C9-M1x_fire2.items.json"))}
QC = {"when": {"type": "choice", "instructions": "When does the TARGET catch fire, if ever?",
      "criteria": {"within_1_minute": None, "within_10_minutes": None, "within_an_hour": None, "never": "the target does not catch fire"}}}
items = []
for i in range(6):
    for k in ["neutral", "gasoline"]:
        it = dict(src[f"F2-{i}-{k}"]); it["id"] = f"F3c-{i}-{k}"; it["questions"] = QC; items.append(it)
    t = src[f"F2-{i}-neutral"]["target"]
    items.append({"id": f"F3p-{i}", "cond": "plain", "target": t,
                  "state": f"In a dry storage room, {t} sits on a concrete floor, touching a wool blanket that is burning fiercely.",
                  "questions": {"target": {"type": "noul", "instructions": f"Within the next minute, does {t} catch fire?"}}})
json.dump(items, open("2026-10-27_C9-M1x_fire3.items.json", "w"), indent=1); print(len(items))

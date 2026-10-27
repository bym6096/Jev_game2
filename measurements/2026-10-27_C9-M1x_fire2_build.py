"""Post-hoc (added after C9-M1b showed no neighbor effect): A's own Q1 design, targets of very different flammability."""
import json
exec(open("2026-10-27_C9-M1x_fire_build.py").read().split("CASES =")[0])
exec("def st" + open("2026-10-27_C9-M1x_fire_build.py").read().split("def st")[1].split("Q =")[0])
Q = {"target": {"type": "noul", "instructions": "Within the next minute, does the fire reach and ignite the TARGET?"}}
T = ["a steel safe", "a ceramic vase", "a wooden chair", "a cardboard box of old letters", "a pile of dry straw", "an open canister of gasoline"]
W = {"neutral": "a stack of bricks", "water": "a bucket of water", "gasoline": "a red can of gasoline"}
items = [{"id": f"F2-{i}-{k}", "cond": k, "target": t, "state": st(t, NEUT_E, w), "questions": Q}
         for i, t in enumerate(T) for k, w in W.items()]
json.dump(items, open("2026-10-27_C9-M1x_fire2.items.json", "w"), indent=1); print(len(items))

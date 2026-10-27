"""Added after G1 results (logged as post-hoc): question wording check for ADMIT/NOT/OR rules."""
import json
src = {i["id"]: i for i in json.load(open("2026-10-27_C9-M1x_gate_base.items.json"))}
out = []
for rid in ["G-R2", "G-R4", "G-R8", "G-R9"]:
    it = dict(src[rid]); it["id"] = rid + "-thru"; it["cond"] = "q_letthrough"
    it["questions"] = {k: {"type": "noul", "instructions": f"Under the gate rule, is arrival ({k[1:]}) let through the gate?"} for k in it["questions"]}
    out.append(it)
json.dump(out, open("2026-10-27_C9-M1x_gate_q2.items.json", "w"), indent=1)

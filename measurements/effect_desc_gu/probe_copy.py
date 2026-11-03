"""Follow-up: the plain swap weakened the 복제 (copy) effect. Try two rewordings of that one description (all other changed ones stay 구슬).
Compares against the stored old runs in out.json."""
import sys, json, statistics as st
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "../../toys/card-forge")
import forge
d = json.load(open("out.json", encoding="utf-8")); rows = d["rows"]; names = [r["name"] for r in rows]
OLD = {k: v[1] for k, v in forge.ALL_EFFECTS.items()}
BASE = {k: x.replace("카드", "구슬") for k, x in OLD.items()}
VAR = {"plain": "이 구슬을 하나 더 만든다", "V1": "이 구슬을 똑같이 하나 더 만든다", "V2": "이 구슬의 복사본을 하나 더 만든다"}
def ask(args):
    name, desc = args
    crit = dict(BASE); crit["copy"] = desc
    body = forge.build_request(name); body["questions"] = {"effect": body["questions"]["effect"]}
    body["questions"]["effect"]["criteria"] = crit
    for _ in range(3):
        try: return forge.call_jev(body)["answers"]["effect"]["probabilities"]
        except Exception as e: err = e
    raise err
jobs = [(n, VAR[v]) for v in ("V1", "V2") for n in names]
with ThreadPoolExecutor(6) as ex: res = list(ex.map(ask, jobs))
out = {"V1": res[:len(names)], "V2": res[len(names):]}
json.dump(out, open("out_copy.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
top = lambda p: max(p, key=p.get)
l1 = lambda x, y: sum(abs(x[k] - y[k]) for k in x) / 2
COPYY = ["분신술", "복제 인간", "쌍둥이", "거울 속의 나", "메아리"]
print("variant       meanL1(vs old)  top1 differs  copy prob on", COPYY)
def line(label, get):
    ps = [get(i) for i in range(len(names))]
    cp = [round(ps[names.index(n)]["copy"], 2) for n in COPYY]
    print(f"{label:12s}  {st.mean(l1(rows[i]['old'], ps[i]) for i in range(len(names))):.3f}           {sum(top(rows[i]['old']) != top(ps[i]) for i in range(len(names)))}/{len(names)}         {cp}")
line("old2 (noise)", lambda i: rows[i]["old2"])
line("plain 구슬", lambda i: rows[i]["new"])
line("V1 똑같이", lambda i: out["V1"][i])
line("V2 복사본", lambda i: out["V2"][i])
print("old copy prob:", [round(rows[names.index(n)]["old"]["copy"], 2) for n in COPYY])
print("copy top1 count old/plain/V1/V2:", sum(top(r["old"]) == "copy" for r in rows), sum(top(r["new"]) == "copy" for r in rows), sum(top(p) == "copy" for p in out["V1"]), sum(top(p) == "copy" for p in out["V2"]))

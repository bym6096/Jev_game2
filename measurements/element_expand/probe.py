"""Element list 58 vs 98: same names, same question, only the element options differ. Output: out.json + printed summary."""
import sys, json, copy, statistics as st
sys.path.insert(0, "../../toys/card-forge")
import forge
NEW = set("storm lava star moon ocean forest mountain wood stone gold crystal cloth fruit bird fish dragon ghost flower egg demon fear hope justice void sports medicine clothes tool weapon vehicle house book villain child king thief magic dance festival science".split())
OLD = [k for k in forge.ALL_ELEMENTS if k not in NEW]
assert len(OLD) == 58 and len(NEW) == 40
src = open("../../toys/card-forge/make_samples.py", encoding="utf-8").read()
names = json.loads("[" + src.split("NAMES = [")[1].split("]")[0].replace("\n", " ") + "]")
names += ["이글이글열매", "이글이글 열매", "불타는 열매", "열매", "손오공", "손오공 2호", "슈퍼맨", "드래곤", "바나나", "곰돌이 인형", "사과", "마법 지팡이", "축구공", "도깨비 방망이"]
def ask(name, keys):
    body = forge.build_request(name)
    body["questions"] = {"element": body["questions"]["element"]}
    body["questions"]["element"]["criteria"] = {k: forge.ELEMENT_DESC.get(k) for k in keys}
    pr = forge.call_jev(body)["answers"]["element"]["probabilities"]
    top = sorted(pr.items(), key=lambda x: -x[1])[:3]
    return [(k, round(p, 3)) for k, p in top]
rows = []
for n in names:
    a, b = ask(n, OLD), ask(n, list(forge.ALL_ELEMENTS))
    rows.append({"name": n, "old": a, "new": b})
    print(f"{n:14s} 58: {a[0][0]:10s}{a[0][1]:.2f} m{a[0][1]-a[1][1]:.2f} | 98: {b[0][0]:10s}{b[0][1]:.2f} m{b[0][1]-b[1][1]:.2f} {'<-- new' if b[0][0] in NEW else ''}")
json.dump(rows, open("out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
m = lambda k: [r[k][0][1] - r[k][1][1] for r in rows]; t = lambda k: [r[k][0][1] for r in rows]
print("top1 prob mean", round(st.mean(t("old")), 3), "->", round(st.mean(t("new")), 3))
print("margin mean   ", round(st.mean(m("old")), 3), "->", round(st.mean(m("new")), 3))
print("margin<0.1    ", sum(x < .1 for x in m("old")), "->", sum(x < .1 for x in m("new")), "of", len(rows))
print("changed top1  ", sum(r["old"][0][0] != r["new"][0][0] for r in rows), "| new-element wins", sum(r["new"][0][0] in NEW for r in rows))

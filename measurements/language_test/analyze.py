# -*- coding: utf-8 -*-
import sys, os, json, statistics as st
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe, forge
from collections import defaultdict

rows = probe.load()
C = {c[0]: c for c in probe.CONCEPTS}
main0 = {(r["lang"], r["concept"]): r for r in rows if r["tag"] == "main" and r["rep"] == 0}
main1 = {(r["lang"], r["concept"]): r for r in rows if r["tag"] == "main" and r["rep"] == 1}
fam = forge.ELEMENT_FAMILY_OF
pct = lambda x, n: 100 * x / n if n else float("nan")
res = {}
for l in probe.LANGS:
    ok = same = fsame = kok = gfp = 0; conf = []; pw = []; ad = []; mana = []; uniq = 0; n = 0; nm = 0
    worst = []
    for cid in probe.ids if hasattr(probe, "ids") else [c[0] for c in probe.CONCEPTS]:
        r = main0[(l, cid)]; e = main0[("en", cid)]
        n += 1
        t1 = r["top3"][0][0]
        good = t1 in C[cid][1]
        ok += good
        same += t1 == e["top3"][0][0]
        fsame += fam[t1] == fam[e["top3"][0][0]]
        kok += r["kind"] in C[cid][2]
        gfp += r["guard"] == "instructs_the_evaluator"
        conf.append(r["top3"][0][1]); pw.append(r["power"]); ad.append(r["attack"] + r["defense"])
        if r["status"] != "scribble":
            mana.append(r["mana"]); uniq += bool(r["unique"])
        if not good:
            worst.append((cid, r["name"], r["top3"], r["guard"]))
    flips = fl = 0
    for (ll, cid), r2 in main1.items():
        if ll != l: continue
        flips += 1; fl += r2["top3"][0][0] != main0[(l, cid)]["top3"][0][0]
    res[l] = dict(ok=pct(ok, n), same=pct(same, n), fsame=pct(fsame, n), kok=pct(kok, n), gfp=pct(gfp, n),
                  conf=st.mean(conf), power=st.mean(pw), ad=st.mean(ad), mana=st.mean(mana), nmana=len(mana),
                  uniq=pct(uniq, len(mana)), flip=pct(fl, flips), worst=worst)
en = res["en"]
for l in res:
    res[l]["pratio"] = res[l]["power"] / en["power"]; res[l]["adratio"] = res[l]["ad"] / en["ad"]
    res[l]["manadiff"] = res[l]["mana"] - en["mana"]

order = sorted(res, key=lambda l: -(res[l]["ok"] + res[l]["same"]))
out = []
out.append("| 언어 | 허용% | 영어와 같음% | 계열 같음% | 종류% | 가드오탐% | 확신도 | 위력비 | (공+방)비 | 마나평균 | 고유% | 뒤집힘% |")
out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
for l in order:
    r = res[l]
    out.append(f"| {l} | {r['ok']:.0f} | {r['same']:.0f} | {r['fsame']:.0f} | {r['kok']:.0f} | {r['gfp']:.0f} | {r['conf']:.2f} | {r['pratio']:.2f} | {r['adratio']:.2f} | {r['mana']:.2f} | {r['uniq']:.0f} | {r['flip']:.0f} |")
out.append("")
out.append("## worst")
for l in order:
    out.append(f"### {l}  ({len(res[l]['worst'])} wrong)")
    for cid, name, top, g in res[l]["worst"][:5]:
        out.append(f"- {cid} / 「{name}」 -> " + ", ".join(f"{k} {p:.2f}" for k, p in top) + (f" [guard={g}]" if g != "names_something" else ""))
out.append("")
out.append("## short")
for s in probe.SHORT:
    line = [s[0]]
    for l in ("ko", "ja", "zh-Hans", "en"):
        r = [x for x in rows if x["tag"] == "short" and x["lang"] == l and x["concept"] == s[0]][0]
        line.append(f"{l}:{r['name']}->{r['top3'][0][0]}({r['top3'][0][1]:.2f}){'OK' if r['top3'][0][0] in s[1] else 'X'}")
    out.append(" | ".join(line))
for l in ("ko", "ja", "zh-Hans", "en"):
    rs = [x for x in rows if x["tag"] == "short" and x["lang"] == l]
    sm = {s[0]: s[1] for s in probe.SHORT}
    enr = {x["concept"]: x for x in rows if x["tag"] == "short" and x["lang"] == "en"}
    okc = sum(x["top3"][0][0] in sm[x["concept"]] for x in rs)
    sc = sum(x["top3"][0][0] == enr[x["concept"]]["top3"][0][0] for x in rs)
    cf = st.mean(x["top3"][0][1] for x in rs); gf = sum(x["guard"] != "names_something" for x in rs)
    out.append(f"SHORT {l}: ok {okc}/10 same-as-en {sc}/10 conf {cf:.2f} guardFP {gf} power {st.mean(x['power'] for x in rs):.2f}")
open(os.path.join(probe.HERE, "analysis.txt"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))

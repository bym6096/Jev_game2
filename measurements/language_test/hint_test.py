# -*- coding: utf-8 -*-
"""Does telling Jev which language the name is written in help? Variants: plain / inline tag "Pain[French]" / separate line.
Reads probe.py (concepts, translations) read-only. Writes hint_out.jsonl and prints a summary."""
import sys, os, json, time, concurrent.futures as cf
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe
forge = probe.forge
LANG_EN = {"ko": "Korean", "de": "German", "pt-BR": "Brazilian Portuguese", "vi": "Vietnamese", "fr": "French", "it": "Italian",
           "pl": "Polish", "tr": "Turkish", "id": "Indonesian", "es": "Spanish"}
OUT = os.path.join(HERE, "hint_out.jsonl")

def ask(variant, lang, name):
    L = LANG_EN[lang]
    body = forge.build_request(f"{name}[{L}]" if variant == "inline" else name)
    if variant == "line":
        body["state"] += f"\nThe card name above is written in {L}."
    for i in range(6):
        try:
            return forge.call_jev(body)["answers"]
        except Exception as e:
            if i == 5: raise
            time.sleep(2 * (i + 1))

def one(variant, lang, ci, name):
    a = ask(variant, lang, name)
    top = sorted(a["element"]["probabilities"].items(), key=lambda x: -x[1])[:3]
    card = forge.make_card(name, "en", a)
    r = {"variant": variant, "lang": lang, "concept": probe.CONCEPTS[ci][0], "name": name, "top3": [[k, round(p, 3)] for k, p in top],
         "guard": a["guard"]["choice"], "power": a["power"]["score"], "mana": card.get("mana"), "status": card["status"]}
    return r

if __name__ == "__main__":
    jobs = [(v, l, i, probe.T[l][i]) for v in ("plain", "inline", "line") for l in LANG_EN for i in range(30)]
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            r = json.loads(l); done.add((r["variant"], r["lang"], r["concept"]))
    jobs = [j for j in jobs if (j[0], j[1], probe.CONCEPTS[j[2]][0]) not in done]
    print("jobs", len(jobs), flush=True)
    errs = 0
    with cf.ThreadPoolExecutor(4) as ex, open(OUT, "a", encoding="utf-8") as f:
        for fut in [ex.submit(one, *j) for j in jobs]:
            try: f.write(json.dumps(fut.result(), ensure_ascii=False) + "\n"); f.flush()
            except Exception as e: errs += 1; print("ERR", str(e)[:120], flush=True)
    print("done; errors", errs)

"""Embed sample cards and the shared tables into the page -> index.html"""
import json
samples = json.load(open("samples.json", encoding="utf-8"))
import forge, fragments
html = (open("template.html", encoding="utf-8").read()
        .replace("__SAMPLES__", json.dumps(samples, ensure_ascii=False))
        .replace("__EFFECT_COST__", json.dumps(forge.EFFECT_COST, ensure_ascii=False))
        .replace("__LANGS__", json.dumps(forge.LANGUAGES, ensure_ascii=False))
        .replace("__MAX_RAW__", str(forge.MAX_RAW))
        .replace("__FRAGS__", json.dumps(fragments.as_json(), ensure_ascii=False))
        .replace("__COMBOS__", json.dumps(forge.COMBOS_KO, ensure_ascii=False)))
open("index.html", "w", encoding="utf-8").write(html)
print(len(samples), "samples;", len(html), "bytes")

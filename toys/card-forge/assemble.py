"""Embed sample cards and the shared tables into the page -> index.html"""
import json
samples = json.load(open("samples.json", encoding="utf-8"))
import forge, fragments, forge_orb
HINTS = {"words": [{"k": k, "label": forge_orb.orbs.TRAITS[k][0], "pos": pos, "t": w, "sp": sp} for k, pos, w, sp in forge_orb.orbs.HINT_WORDS], "share": forge_orb.orbs.HINT_SHARE, "mult": forge_orb.orbs.HINT_MULT,
         "mods": [{"k": k, "name": forge_orb.orbs.MOD_RULES[k][0], "text": forge_orb.orbs.MOD_RULES[k][1], "pos": pos, "t": w, "sp": sp} for k, pos, w, sp in forge_orb.orbs.MOD_WORDS]}
html = (open("template.html", encoding="utf-8").read()
        .replace("__SAMPLES__", json.dumps(samples, ensure_ascii=False))
        .replace("__EFFECT_COST__", json.dumps(forge.EFFECT_COST, ensure_ascii=False))
        .replace("__LANGS__", json.dumps(forge.LANGUAGES, ensure_ascii=False))
        .replace("__MAX_RAW__", str(forge.MAX_RAW))
        .replace("__HINTS__", json.dumps(HINTS, ensure_ascii=False))
        .replace("__FRAGS__", json.dumps(fragments.as_json(), ensure_ascii=False))
        .replace("__ELFAM__", json.dumps({v: forge.ELEMENT_FAMILY_OF[k] for k, v in forge.ALL_ELEMENTS.items()}, ensure_ascii=False))
        .replace("__COMBOS__", json.dumps(forge.COMBOS_KO, ensure_ascii=False)))
open("index.html", "w", encoding="utf-8").write(html)
print(len(samples), "samples;", len(html), "bytes")

"""Checks that the Unity data export still matches the web toy (run after changing forge.py / template.html / fragments.py):
    python3 test_unity_export.py
It compares the exported JSON with the tables the page and the server really use, so the Unity port cannot silently drift."""
import json, os, re, sys
import forge, fragments, export_unity

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

rules = export_unity.build()
on_disk = json.load(open(os.path.join(export_unity.OUT, "JevRules.json"), encoding="utf-8"))
check(rules == on_disk, "JevRules.json is stale: run python3 export_unity.py")

html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
tiers = [{"name": n, "cap": int(c), "price": int(p), "frag": float(f)} for n, c, p, f in
         re.findall(r'\{name:"([^"]+)", cap:(\d+),\s*price:(\d+),\s*frag:([\d.]+)\}', html)]
check(tiers == rules["tiers"], f"blank grades differ from template.html TIERS: {tiers} vs {rules['tiers']}")
m = re.search(r"const DECK_MAX = (\d+)", html); check(m and int(m.group(1)) == rules["deck_max"], "DECK_MAX differs")
m = re.search(r"const VARIANT_RATE = ([\d.]+)", html); check(m and float(m.group(1)) == rules["variant_rate"], "VARIANT_RATE differs")
check(rules["effect_cost"] == forge.EFFECT_COST, "effect_cost differs")
check(set(rules["languages"]) == set(forge.LANGUAGES) and rules["language_order"] == list(forge.LANGUAGES), "languages differ")
check(set(rules["fragments"]) == set(forge.LANGUAGES), "a language has no pre-written words")
check(len(rules["combos"]) == len(forge.COMBOS), "combo count differs")
check(set(rules["fonts"]) == set(forge.LANGUAGES), "a language has no font entry")
check(rules["mana_cap"] == forge.MANA_CAP and rules["max_raw"] == forge.MAX_RAW, "mana cap / max raw differ")
for k, v in rules["languages"].items():
    cfg = forge.LANGUAGES[k]
    check(v["cap"] == cfg["cap"] and v["spaces_count"] == cfg["spaces_count"] and v["marks"] == cfg["marks"] and v["ranges"] == [list(r) for r in cfg["ranges"]], f"language {k} differs")
# the samples must be readable by the C# Card class: every field it declares has the type the server writes
samples = json.load(open(os.path.join(export_unity.OUT, "JevSamples.json"), encoding="utf-8"))
check(len(samples) == len(json.load(open(os.path.join(HERE, "samples.json"), encoding="utf-8"))), "samples not exported")
for c in samples:
    if c.get("status") == "scribble":
        continue
    check(isinstance(c.get("effects"), list) and isinstance(c.get("mana"), int) and isinstance(c.get("color"), str), f"sample {c.get('name')} has an unexpected shape")
print("OK" if not fails else "\n".join("FAIL: " + f for f in fails))
sys.exit(1 if fails else 0)

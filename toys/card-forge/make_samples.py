"""Forge the sample beads shown in the gallery (used when no server is running): one per profile language.
Each name is written in its own language's letters (the same name rules as a player's), on a clean blank in the page.
Run:  python3 make_samples.py   (calls Jev, 13 requests)  then  python3 assemble.py  and  python3 export_unity.py"""
import json, forge

SAMPLES = [   # (language, name): different kinds of things on purpose, so the shelf shows different colors and moods
    ("ko", "화염검"), ("en", "Lucky penny"), ("ja", "桜吹雪"), ("zh-Hans", "空城计"), ("zh-Hant", "櫻花風暴"),
    ("es", "Gato negro"), ("fr", "Pluie d'or"), ("de", "Kirschblüten"), ("pt-BR", "Espada de fogo"), ("vi", "Mèo đen"),
    ("ru", "Вишнёвый шторм"), ("th", "พายุซากุระ"), ("ar", "سيف اللهب"),
]
assert [l for l, _ in SAMPLES] == list(forge.LANGUAGES), "one sample per language, in the language table's order"
cards = []
for lang, n in SAMPLES:
    c, _ = forge.forge(n, lang)
    cards.append(c)
    print(lang, c["status"], c.get("mana"), n, c.get("element"), [e["name"] for e in c.get("effects", [])], c.get("kind"), c.get("color"))
json.dump(cards, open("samples.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

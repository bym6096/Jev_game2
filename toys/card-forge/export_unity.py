"""Export the card-forge rules for the Unity port -> unity/JevOrbs/Assets/Resources/JevRules.json (+ JevSamples.json).

forge.py / fragments.py / template.html stay the single source of truth. The Unity project reads this JSON instead of
keeping its own copy of the tables, so the two cannot drift. Run it again after any rule change:

    python3 export_unity.py
"""
import json, os, re
import forge, fragments

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "unity", "JevOrbs", "Assets", "JevOrbs", "Resources"))

# Blank grades (same numbers as TIERS in template.html)
TIERS = [
    {"name": "낡은 구슬", "cap": 5, "price": 1, "frag": 1.0},
    {"name": "평범한 구슬", "cap": 7, "price": 3, "frag": 0.5},
    {"name": "깨끗한 구슬", "cap": 9, "price": 6, "frag": 0.25},
    {"name": "금박 구슬", "cap": 12, "price": 12, "frag": 0.1},
]
DECK_MAX = 20
VARIANT_RATE = 0.12   # gacha: chance a card is quietly read a different way (VARIANT_RATE in template.html)

# OS fonts to try, per language, when no font file is dropped into Resources/JevFonts/<lang>.ttf.
# "brush" is the Google Fonts family the web version engraves with (use it for the dropped-in file).
FONTS = {
    "ko": {"brush": "Nanum Brush Script", "os": ["Batang", "Malgun Gothic", "AppleMyungjo", "Apple SD Gothic Neo", "Noto Serif CJK KR", "Noto Sans CJK KR"]},
    "en": {"brush": "Kaushan Script", "os": ["Georgia", "Palatino Linotype", "Times New Roman", "Arial"]},
    "ja": {"brush": "Yuji Boku", "os": ["Yu Mincho", "Hiragino Mincho ProN", "Noto Serif CJK JP", "Meiryo", "MS Mincho"]},
    "zh-Hans": {"brush": "Ma Shan Zheng", "os": ["SimSun", "Songti SC", "Noto Serif CJK SC", "Microsoft YaHei"]},
    "zh-Hant": {"brush": "Ma Shan Zheng", "os": ["PMingLiU", "Songti TC", "Noto Serif CJK TC", "Microsoft JhengHei"]},
    "es": {"brush": "Kaushan Script", "os": ["Georgia", "Palatino Linotype", "Times New Roman", "Arial"]},
    "fr": {"brush": "Kaushan Script", "os": ["Georgia", "Palatino Linotype", "Times New Roman", "Arial"]},
    "de": {"brush": "Kaushan Script", "os": ["Georgia", "Palatino Linotype", "Times New Roman", "Arial"]},
    "pt-BR": {"brush": "Kaushan Script", "os": ["Georgia", "Palatino Linotype", "Times New Roman", "Arial"]},
    "vi": {"brush": "Pacifico", "os": ["Times New Roman", "Georgia", "Arial"]},
    "ru": {"brush": "Marck Script", "os": ["Times New Roman", "Georgia", "Arial"]},
    "th": {"brush": "Charmonman", "os": ["Leelawadee UI", "Thonburi", "Tahoma", "Noto Sans Thai"]},
    "ar": {"brush": "Aref Ruqaa", "os": ["Traditional Arabic", "Geeza Pro", "Arial", "Tahoma"]},
}


def _ko_fragments():
    """The Korean pre-written words live in template.html (PRE, SUF_SP, SUF_ATT); read them from there so there is one list."""
    src = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

    def words(name):
        m = re.search(r"const %s = \((.*?)\)\.split\(\"\|\"\)" % name, src, re.S)
        assert m, name
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
        return "".join(parts).split("|")
    pre, sp, att = words("PRE"), words("SUF_SP"), words("SUF_ATT")
    assert len(pre) > 100 and len(sp) > 40 and len(att) > 20, (len(pre), len(sp), len(att))
    return ([{"t": t, "pos": "pre", "sp": True} for t in pre] + [{"t": t, "pos": "suf", "sp": True} for t in sp]
            + [{"t": t, "pos": "suf", "sp": False} for t in att])


def build():
    frags = {"ko": _ko_fragments(), **fragments.as_json()}
    return {
        "max_raw": forge.MAX_RAW,
        "deck_max": DECK_MAX,
        "variant_rate": VARIANT_RATE,
        "mana_cap": forge.MANA_CAP,
        "tiers": TIERS,
        "language_order": list(forge.LANGUAGES),
        "languages": {k: {"label": v["label"], "jev": v["jev"], "ranges": [list(r) for r in v["ranges"]], "cap": v["cap"],
                          "spaces_count": v["spaces_count"], "marks": v["marks"]} for k, v in forge.LANGUAGES.items()},
        "statless": sorted(forge.STATLESS),
        "effect_cost": forge.EFFECT_COST,
        "combos": forge.COMBOS_KO,
        "element_family_of": {v: forge.ELEMENT_FAMILY_OF[k] for k, v in forge.ALL_ELEMENTS.items()},
        "element_family_names": list(forge.ELEMENT_FAMILIES),
        "themes": list(forge.THEMES.values()),
        "theme_keys": list(forge.THEMES),
        "fragments": frags,
        "fonts": FONTS,
    }


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rules = build()
    with open(os.path.join(OUT, "JevRules.json"), "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=1)
    samples = json.load(open(os.path.join(HERE, "samples.json"), encoding="utf-8"))
    with open(os.path.join(OUT, "JevSamples.json"), "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False)
    print("rules:", len(rules["languages"]), "languages,", sum(len(v) for v in rules["fragments"].values()), "fragments,",
          len(rules["element_family_of"]), "elements,", len(rules["combos"]), "combos;", len(samples), "samples ->", OUT)

"""Orb axes v2 (2026-11-05): after the composition test and the director's design additions.
Removed: side (derived from verb by rule), pay, persist (split into lifetime + bagfate), conditional (replaced by trigger).
New: material, lifetime, bagfate, trigger, unit, allegiance. role loses 'lasting' (duration is now lifetime)."""
import sys
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, axes_v1
STATE, LANG_LINE = axes.STATE, axes.LANG_LINE
VERBS = dict(axes_v1.VERBS)
VERBS["create"] = "making or conjuring a brand-new item, tool, or material (not a creature or a building)"   # was: any new thing; overlapped summon
MODS = {k: axes.MODS_NOUL[k] for k in ("scaling", "risky", "random", "network")}
CHOICES = {
  "guard": axes_v1.CHOICES["guard"],
  "role": ("What would an orb with this name mainly do when used?",
    {"cast":   "does something once, right away, like a spell, a strike, or an action",
     "build":  "places a structure, building, or lasting object on the map",
     "summon": "calls a person, creature, or machine to fight or work",
     "move":   "moves someone or something to another place"}),
  "timing": ("When would the effect of an orb with this name happen?",
    {"now":       "right away when used",
     "delayed":   "a few turns later, like a timer, a fuse, or a slow process",
     "repeating": "again and again every turn",
     "trigger":   "only when something specific happens, like a trap or a reaction"}),
  "trigger": ("If the effect has to wait for something, what would set it off?",
    {"none":     "nothing; it simply happens",
     "hit":      "when someone is hit or takes damage",
     "death":    "when someone dies or is destroyed",
     "turn":     "at the start or the end of a turn",
     "orb":      "when another orb is used",
     "approach": "when an enemy comes near or steps on it"}),
  "range": axes_v1.CHOICES["range"],
  "material": ("What is the thing named mostly made of, or what would it mainly produce or need?",
    {"wood":  "wood: trees, logs, planks, timber",
     "ore":   "ore: stone, metal, minerals, gems",
     "food":  "food: crops, fruit, bread, meat, fish, cooking",
     "gold":  "money: coins, treasure, trade, banking",
     "none":  "nothing physical: magic, ideas, feelings, energy, or natural forces"}),
  "lifetime": ("How long would the effect or object of the thing named last?",
    {"instant": "it happens once and is over at once",
     "turns":   "a few turns, like a spell, a mood, a potion, or a fire",
     "stage":   "about one battle or one level, like weather, a camp, or a siege",
     "run":     "a long time, a whole journey, like a building, a tree, a monument, or a vow",
     "forever": "permanent and unchanging, like an eternal law, an unbreakable curse, or a mountain"}),
  "bagfate": ("What happens to an orb with this name after it is used?",
    {"used_up": "it is a one-time thing that gets used up",
     "returns": "it is a tool or ability that can be used again and again",
     "passive": "it is never really used: it works just by being carried"}),
  "verb": ("Which effect would the thing named most naturally have when used in this game?", VERBS),
  "unit": ("If the thing named were a helper or a creature in a game, what kind would it be?",
    {"soldier":   "a fighter or guard: soldier, knight, archer, warrior",
     "worker":    "a civilian or worker: farmer, merchant, builder, villager",
     "beast":     "an animal or a monster",
     "spirit":    "a ghost, spirit, god, or magical being",
     "construct": "a machine, golem, statue, or robot"}),
  "allegiance": ("Would a creature or person with this name normally fight for the player or against the player?",
    {"ally":     "a friendly helper, hero, worker, or pet",
     "hostile":  "a monster, enemy, villain, or pest"}),
}
def build_request(name, lang="ko"):
    q = {k: {"type": "choice", "instructions": i, "criteria": o} for k, (i, o) in CHOICES.items()}
    for k, d in MODS.items():
        q[k] = {"type": "noul", "instructions": f"Is the thing named strongly associated with {d}?"}
    q["power"] = {"type": "score", "instructions": "How grand and powerful is the thing named, overall?", "criteria": axes.POWER}
    return {"model": "jev-latest", "state": STATE.format(name=name) + (LANG_LINE.format(lang=axes.LANGS[lang]) if lang != "en" else ""), "questions": q}

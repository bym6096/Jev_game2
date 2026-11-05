"""Headless rules simulator for the orb game (NO GUI). Ring-distance hex model: enemies come from ring 6 toward the player at ring 0.
ALL NUMBERS ARE PLACEHOLDERS. The point is to find orbs that are far too strong / useless and to test whether the structure holds together.
Orbs are built from the measured Jev axes (measurements/orb_axes/out_*.jsonl) with the same rules as compose4.py."""
import os, json, random, math, copy, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.join(HERE, "..", "measurements", "orb_axes")
def _load(f):
    d = collections.defaultdict(list)
    for l in open(os.path.join(AX, f), encoding="utf-8"):
        r = json.loads(l); d[r["id"].split("|", 1)[1]].append(r["answers"])
    return d
V3, V2, V4, PROD = _load("out_v3.jsonl"), _load("out_v2.jsonl"), _load("out_v4.jsonl"), _load("out_prod.jsonl")
V3.update(PROD)
mp = lambda rows, key, o: sum(a[key]["probabilities"][o] for a in rows) / len(rows)
best = lambda rows, key: max(rows[0][key]["probabilities"], key=lambda o: mp(rows, key, o))
LV = ["instant", "turns", "stage", "run", "forever"]
T = {"instant": 1.0, "turns": 1.6, "stage": 2.4, "run": 3.2, "forever": 4.0}; N = {"instant": 1, "turns": 3, "stage": 12, "run": 40, "forever": 100}
CD = {"instant": 1.0, "turns": 1.2, "stage": 1.6, "run": 2.2, "forever": 3.5}; CR = {"single": 1.0, "line": 1.1, "around": 1.3, "wide": 1.6}
RM = {"single": 1.0, "line": .8, "around": .6, "wide": .4}; NT = {"single": 1, "line": 2, "around": 3, "wide": 99}
ENEMY_V = {"damage", "debuff", "control", "steal", "drain"}; BAG_V = {"draw", "recycle", "trash", "peek", "tempo", "energy", "amplify", "create"}
RAW = ("wood", "ore", "food")

class Orb:
    def __init__(s, **k): s.__dict__.update(k)
    def __repr__(s): return f"<{s.name} {s.role} {[v for v,_ in s.verbs]} {s.life} m{s.mana}>"

def verb_probs(name):
    src = V4 if name in V4 else V3
    return {o: mp(src[name], "verb", o) for o in src[name][0]["verb"]["probabilities"]}
def select_verbs(p, rel=.4, floor=.2, cap=3):
    rk = sorted(p, key=lambda o: -p[o]); return [(o, p[o]) for i, o in enumerate(rk[:cap]) if i == 0 or p[o] >= max(rel * p[rk[0]], floor)]

def make_orb(name, grade="깨끗한", cost_model="naive", gold_mult=1.0):
    r = V3[name]; r2 = V2.get(name) or PROD.get(name)
    vp = verb_probs(name); vs = select_verbs(vp); p1 = vs[0][1]; amb = p1 < .4
    pw = sum(a["power"]["score"] for a in r) / len(r); pe = pw * (1.0 if p1 >= .5 else .85 if p1 >= .4 else .6)
    role, timing, trig, rng, mat = (best(r, k) for k in ("role", "timing", "trigger", "range", "material"))
    if amb:
        vs = vs[:1]; trig = "none"
        if mp(r, "role", role) < .6: role = "cast"
    if mp(r, "trigger", trig) < .5: trig = "none"
    # lifetime (A + stage promotion, build floor, power promotion, forever gate)
    L = max(LV, key=lambda o: mp(r, "lifetime_A", o))
    if L in ("turns", "run") and mp(r, "lifetime_A", "stage") >= .15: L = "stage"
    if role == "build" and L in ("instant", "turns"): L = "run"
    if L == "turns" and pe >= 1.5: L = "stage"
    if L == "forever" and not (grade == "금박" and pe >= 3 and mp(r, "lifetime_A", "forever") >= .7): L = "run"
    fate = best(r, "bagfate2") if mp(r, "bagfate2", best(r, "bagfate2")) >= .5 else "returns"
    if timing == "delayed" and role == "cast" and L in ("turns", "stage"): L = "instant"
    if fate == "passive" and L == "instant": L = "run"
    v0 = vs[0][0]
    if role == "cast" and L in ("stage", "run", "forever") and rng == "single" and v0 in ENEMY_V: rng = "around"      # rule: long duration needs an aura, not one enemy
    B = 5 * (1 + 2 * pe); mat = None if mat == "none" else mat
    def mag(share):
        v = B * .3 * RM[rng] if role in ("build", "summon") else (B * RM[rng] if L == "instant" else B * T[L] / N[L] * RM[rng])
        return max(1, round(v * share))
    payload = []
    for (v, _), sh in zip(vs, (1, .7, .5)):
        m = mag(sh)
        if role == "cast" and v in ("harvest", "grow", "money", "create", "steal"): m = max(1, m // 2)               # instant resource gain is inefficient
        mt = mat if v in ("harvest", "grow", "create") else None
        if v == "harvest" and not mt: mt = "ore"
        if v == "grow" and not mt: mt = "food"
        if v in ("money", "steal") or (mt == "gold" and v in ("harvest", "grow", "create")): m = max(1, round(m * gold_mult))      # direct gold gain nerf
        payload.append((v, m, mt))
    mods = sorted(((sum(a[m]["noul"] for a in r) / len(r), m) for m in ("scaling", "risky", "random", "network")), reverse=True)
    mod = mods[0][1] if mods[0][0] >= .6 and not amb else None
    mana = max(1, round(.5 * pe * CD[L] * CR[rng])) + len(vs) - 1
    o = Orb(name=name, role=role, payload=payload, verbs=vs, rng=rng, life=L, timing=timing, trig=trig, mat=mat, fate=fate, mod=mod, pe=pe, B=B, mana=mana, amb=amb,
            delay=1 + int(pe // 2), hp=max(1, round(B)), bag_only=all(v in BAG_V for v, _, _ in payload))
    o.bcost = (mat or "wood", max(1, round(B * .5 / 5)), max(1, round(B * .4 / 5))) if role == "build" else None
    unit = best(r2, "unit") if r2 and "unit" in r2[0] else "soldier"; o.hostile = bool(r2 and "allegiance" in r2[0] and best(r2, "allegiance") == "hostile")
    o.unit = unit; o.lvl = 1 + int(pe // 1.5)
    if cost_model == "value": o.mana = cost_from_value(est_total_value(o))
    elif cost_model == "linear": o.mana = cost_linear(est_total_value(o))
    return o

# ---- gold-equivalent value of one orb (also used by the bot and by the "value" cost model) --------------------------------------------
RATE = {"damage": .15, "guard": .10, "heal": .25, "money": 1.0, "harvest": .5, "grow": .5, "buff": .4, "debuff": .4, "control": 1.5, "steal": 1.0, "drain": .3,
        "process": .6, "energy": 2.0, "tempo": 2.0, "draw": 1.5, "recycle": 1.0, "trash": .5, "create": 2.0, "amplify": 3.0, "remove": 0, "transform": 0, "peek": 0}
DUR = {"instant": 1, "turns": 3, "stage": 10, "run": 24, "forever": 24}
def est_total_value(o):
    t = 0
    for v, m, _ in o.payload:
        nt = min(NT[o.rng], 4)                                           # expected number of enemies hit is capped
        if v in ("damage", "drain", "debuff"): base = m * RATE[v] * nt
        elif v == "control": base = RATE["control"] * nt                  # control does not scale with magnitude, only with how many are held
        elif v in BAG_V: base = RATE.get(v, 0) * (3 if o.life != "instant" else 1)
        else: base = m * RATE.get(v, 0)
        n = 1 if v in BAG_V else (DUR[o.life] if (o.role in ("build", "summon") or o.life != "instant") else 1)
        if o.role == "build": n = DUR["stage"] + 8
        if o.role == "summon": n = 10
        t += base * min(n, 24)
    if o.role == "summon" and o.hostile: t = max(0, o.lvl * 2 * 2 - o.lvl * 4)
    return t
def cost_from_value(v): return max(1, min(8, round(.9 + .8 * math.log2(1 + v / 4))))
def cost_linear(v): return max(1, min(8, round(v / 10)))

# ---- the game ---------------------------------------------------------------------------------------------------------------------------
FAM = {"money": "gold", "steal": "gold", "damage": "dmg", "drain": "dmg", "guard": "def", "heal": "def", "control": "ctl", "debuff": "ctl", "harvest": "eco", "grow": "eco", "create": "eco", "process": "eco",
       "draw": "bag", "recycle": "bag", "trash": "bag", "tempo": "bag", "energy": "bag", "peek": "bag", "buff": "amp", "amplify": "amp", "remove": "misc", "transform": "misc"}
STAGE_TYPES = {"balanced": (1.0, 1.0), "hostile": (1.6, .5), "rich": (.6, 2.0)}
class Game:
    def __init__(g, bag, seed, due, rng_cfg=None, bot="greedy", reward_pick="best3", pool_names=None, cost_model="naive", stages=3, turns=15, cfg=None):
        g.cfg = dict(hp=60, mana=6, hand=5, ehp=1.0, eatk=1.0, rest=20); g.cfg.update(cfg or {})
        g.R = random.Random(seed); g.RD = random.Random(seed * 7919 + 1); g.RR = random.Random(seed * 104729 + 3)
        g.due, g.bot, g.reward_pick, g.pool_names, g.stages, g.turns_per = due, bot, reward_pick, pool_names or [], stages, turns
        g.bag = [copy.copy(o) for o in bag]; g.draw = []; g.disc = []; g.hand = []
        g.hp = g.max_hp = g.cfg["hp"]; g.shield = 0; g.gold = 0; g.res = dict.fromkeys(RAW, 0); g.items = 0
        g.pick_key = None; g.fam_turn = collections.Counter(); g.cap_b = 6; g.cap_s = 5; g.cleared = 0; g.deaths = 0; g.failed = None; g.buildings = []; g.fx = []; g.stats = collections.Counter(); g.played = collections.Counter(); g.contrib = collections.Counter()
    # --- helpers
    def reshuffle(g):
        g.draw = [o for o in g.bag if o.fate != "passive"]; g.R.shuffle(g.draw)
    def drawn(g, n):
        for _ in range(n):
            if not g.draw:
                g.draw = [o for o in g.disc if o in g.bag]; g.disc = []; g.RD.shuffle(g.draw)
            if g.draw: g.hand.append(g.draw.pop())
    def enemies_sorted(g): return sorted(g.en, key=lambda e: e["ring"])
    def targets(g, o):
        es = g.enemies_sorted(); return es[: NT[o.rng]]
    # --- effects
    def apply(g, o, payload, src_mult=1.0, from_building=None):
        for v, m, mt in payload:
            m = max(1, round(m * src_mult * g.amp)); 
            if o.mod == "random": m = max(1, round(m * g.R.uniform(.5, 1.5)))
            if o.mod == "network": m = round(m * (1 + .1 * len(g.buildings)))
            if o.mod == "scaling": m = round(m * (1 + .1 * g.uses[o.name]))
            if o.mod == "risky": g.hp -= max(1, m // 4)
            bonus = 1 + g.dmgb
            if v in ("damage", "drain"):
                for e in g.targets(o):
                    b2 = bonus * (g.cfg.get("weak_bonus", 1.0) if (e["weak"] > 0 or e["stun"] > 0) else 1.0)
                    e["hp"] -= m * b2; g.contrib[o.name] += m * b2 * RATE["damage"]
                    if v == "drain": g.hp = min(g.max_hp, g.hp + m // 2)
                g.reap(o)
            elif v == "guard": g.shield = min(40, g.shield + m); g.contrib[o.name] += m * RATE["guard"] if g.en else 0
            elif v == "heal":
                h = min(m, g.max_hp - g.hp); g.hp += h; g.contrib[o.name] += h * RATE["heal"]
            elif v == "money": g.stats["g_money"] += m; g.gold += m; g.contrib[o.name] += m
            elif v == "steal":
                if g.en: g.stats["g_money"] += m; g.gold += m; g.contrib[o.name] += m
            elif v in ("harvest", "grow") and mt == "gold":
                g.gold += m; g.contrib[o.name] += m * RATE["harvest"]
            elif v in ("harvest", "grow"):
                if v == "harvest":
                    take = min(m, g.pool[mt]); g.pool[mt] -= take
                else:
                    take = min(m, g.pool["land"]); g.pool["land"] -= take
                g.res[mt] += take; g.contrib[o.name] += take * RATE["harvest"]
            elif v == "process":
                raw = [k for k in RAW if g.res[k] > 0]; n = 0
                for k in raw:
                    t = min(m - n, g.res[k]); g.res[k] -= t; n += t
                g.stats["g_process"] += int(n * g.cfg.get("process_ratio", 1.5)); g.gold += int(n * g.cfg.get("process_ratio", 1.5)); g.contrib[o.name] += n * 0.9 * RATE["process"]
            elif v == "buff": g.dmgb = min(1.0, g.dmgb + m / 60)
            elif v == "debuff":
                for e in g.targets(o): e["weak"] = max(e["weak"], 3); g.contrib[o.name] += RATE["debuff"] * m
            elif v == "control":
                n = 1 if o.life in ("stage", "run", "forever") else 1 + int(o.B // 30)
                for e in g.targets(o): e["stun"] = max(e["stun"], n); g.contrib[o.name] += RATE["control"] * n
            elif v == "draw": g.drawn(1 + int(o.pe // 2.5))
            elif v == "recycle":
                if g.disc: g.hand.append(g.disc.pop(g.R.randrange(len(g.disc))))
            elif v == "trash":
                cands = [x for x in g.disc if x is not o]
                if cands:
                    w = min(cands, key=lambda x: est_total_value(x)); g.disc.remove(w); g.stats["trashed"] += 1
                    if w in g.bag: g.bag.remove(w)
            elif v == "tempo": g.mana += 1
            elif v == "energy": g.mana += max(1, int(o.pe // 1.5)); g.contrib[o.name] += RATE["energy"]
            elif v == "create": 
                if mt == "gold": g.gold += 2
                elif mt: g.res[mt] += 2
                else: g.items += 1
                g.contrib[o.name] += RATE["create"]
            elif v == "amplify": g.amp = 2.0
    def reap(g, o=None):
        for e in [e for e in g.en if e["hp"] <= 0]:
            g.en.remove(e); g.gold += e["bounty"]; g.kills += 1; g.stats["kills"] += 1; g.stats["g_bounty"] += e["bounty"]
            if e.get("farm"): g.stats["g_bounty_farm"] += e["bounty"]
            if o is not None: g.contrib[o.name] += e["bounty"]
    # --- playing an orb
    def can_play(g, o):
        if o.mana > g.mana: return False
        if o.role == "build":
            mt, x, y = o.bcost
            if mt == "gold": return g.gold >= x + y and len(g.buildings) < g.cap_b
            return g.res[mt] >= x and g.gold >= y and len(g.buildings) < g.cap_b
        if o.role == "summon" and not o.hostile: return len(g.summons) < g.cap_s
        return True
    def play(g, o):
        g.mana -= o.mana; g.played[o.name] += 1; g.uses[o.name] += 1
        if o.role == "build":
            mt, x, y = o.bcost
            if mt == "gold": g.gold -= x + y
            else: g.res[mt] -= x; g.gold -= y
            g.buildings.append({"o": o, "hp": o.hp, "age": 0, "life": o.life})
        elif o.role == "summon":
            if o.hostile:
                for _ in range(2): g.spawn(o.lvl); g.en[-1]["farm"] = True; g.en[-1]["bounty"] = max(1, round(g.en[-1]["bounty"] * g.cfg.get("farm_bounty", 1.0)))
            else: g.summons.append({"o": o, "hp": o.hp, "age": 0})
        else:
            fam = FAM.get(o.payload[0][0], "misc"); fm = g.cfg.get("fam_decay", 1.0) ** g.fam_turn[fam]; g.fam_turn[fam] += 1
            if o.trig != "none":
                g.fx.append({"kind": "trig", "o": o, "cond": o.trig, "uses": 1 if o.life == "instant" else 3, "left": 99})
            elif o.timing == "delayed": g.fx.append({"kind": "delay", "o": o, "at": g.turn + o.delay})
            elif o.life == "instant": g.apply(o, o.payload, fm)
            elif o.bag_only: g.apply(o, o.payload, fm); g.fx.append({"kind": "dur", "o": o, "left": {"turns": 3, "stage": 10, "run": 24, "forever": 24}[o.life] if o.life != "turns" else 3, "charges": 3})
            else:
                g.apply(o, o.payload, fm); g.fx.append({"kind": "dur", "o": o, "left": {"turns": 3, "stage": 10**6, "run": 10**6, "forever": 10**6}[o.life], "charges": 99})
        g.amp = 1.0 if o.payload[0][0] != "amplify" else g.amp
        if o.fate == "used_up": g.bag.remove(o); g.stats["exhausted"] += 1
        else: g.disc.append(o)
        g.hand.remove(o)
    def spawn(g, lvl):
        g.en.append({"ring": 6, "hp": (14 + 8 * lvl) * g.cfg["ehp"], "atk": (3 + 2 * lvl) * g.cfg["eatk"], "lvl": lvl, "bounty": g.cfg.get("bounty0", 1) + g.cfg.get("bountyk", 1) * lvl, "stun": 0, "weak": 0})
    # --- bot: choose the best affordable subset of the hand (brute force, <=5 orbs)
    def value(g, o, depth=0):
        threat = len(g.en) > 0; t_left = max(1, g.turns_per - g.turn)
        v = 0
        for p, m, mt in o.payload:
            if p in ("damage", "drain"): r = (min(m * NT[o.rng], sum(e["hp"] for e in g.targets(o))) * RATE["damage"]) * (g.cfg.get("weak_bonus", 1.0) if any(e["weak"] > 0 or e["stun"] > 0 for e in g.targets(o)) else 1.0) if threat else 0
            elif p == "guard": r = m * RATE["guard"] if threat and g.shield < 30 else 0
            elif p == "heal": r = min(m, g.max_hp - g.hp) * RATE["heal"]
            elif p in ("debuff", "control"): r = (RATE[p] * (min(NT[o.rng], len(g.en)))) * (m if p == "debuff" else 1) * (1.4 if (depth == 0 and any(x.payload[0][0] in ("damage", "drain") for x in g.hand if x is not o)) else 1.0) if threat else 0
            elif p == "steal": r = m if threat else 0
            elif p == "amplify": r = 0.5 * max([g.value(x, 1) for x in g.hand if x is not o and x.payload[0][0] != "amplify"] + [0]) if depth == 0 else 0
            elif p in BAG_V: r = RATE[p] if not (p == "energy" and len(g.hand) < 2) else 0
            elif p == "process": r = .6 * min(m, sum(g.res.values()))
            elif p == "buff": r = m * RATE["buff"] if threat else 0
            else: r = m * RATE.get(p, 0)
            v += r
        if o.role in ("build", "summon") or o.life != "instant":
            per = v; n = t_left + (6 if o.role == "build" else 0)
            if o.life == "turns": n = 3
            v = per * n if not (o.role == "summon" and o.hostile) else (o.lvl * 2 * 2 - o.lvl * 4 * (1 if g.hp < 30 else 0.5))
        return v
    def bot_turn(g):
        g.fam_turn = collections.Counter()
        if g.items and g.hp < g.max_hp * .5: g.items -= 1; g.hp = min(g.max_hp, g.hp + 15)
        if g.res["food"] >= 2 and g.hp < g.max_hp * .6: g.res["food"] -= 2; g.hp = min(g.max_hp, g.hp + 6)
        guard = 0
        while guard < 12:
            guard += 1; cand = [o for o in g.hand if g.can_play(o)]
            if not cand: break
            pick = max(cand, key=lambda o: (g.value(o) / (o.mana + .5), -o.mana))
            if g.value(pick) <= 0.05: break
            g.play(pick)
        g.amp = 1.0                                                                                       # an unused amplify must not leak into upkeep
    # --- end-of-turn world update
    def upkeep(g):
        # effects
        for f in list(g.fx):
            o = f["o"]
            if f["kind"] == "delay" and g.turn >= f["at"]: g.apply(o, o.payload); g.fx.remove(f)
            elif f["kind"] == "dur":
                if f["left"] <= 0 or f["charges"] <= 0: g.fx.remove(f); continue
                g.apply(o, o.payload); f["left"] -= 1; f["charges"] -= 1 if o.bag_only else 0
        for o in g.bag:                                                                                 # passive orbs work just by being in the bag
            if o.fate == "passive" and o.role == "cast" and o.trig == "none": g.apply(o, o.payload, .7)
        if g.cfg.get("upkeep"): g.gold = max(0, g.gold - g.cfg["upkeep"] * len(g.buildings))
        # buildings and summons
        for b in list(g.buildings):
            b["age"] += 1; o = b["o"]
            if o.timing == "delayed" and b["age"] <= o.delay: continue
            if o.trig == "approach":
                if any(e["ring"] <= 3 for e in g.en) and b.get("fired", 0) < 3: g.apply(o, o.payload); b["fired"] = b.get("fired", 0) + 1
            else: g.apply(o, o.payload)
        for s in list(g.summons):
            s["age"] += 1; g.apply(s["o"], s["o"].payload)
        # enemies
        for e in list(g.en):
            if e["stun"] > 0: e["stun"] -= 1; continue
            if e["ring"] > 1: e["ring"] -= 1; continue
            atk = max(1, e["atk"] - (3 if e["weak"] > 0 else 0)); e["weak"] = max(0, e["weak"] - 1)
            tg = ["p"] + list(g.buildings) + list(g.summons); t = g.R.choice(tg)
            if t == "p":
                d = atk
                if g.shield: a = min(g.shield, d); g.shield -= a; d -= a
                g.hp -= d; g.stats["dmg_taken"] += atk
                for f in list(g.fx):                                                                      # hit / death triggers
                    if f["kind"] == "trig" and f["cond"] == "hit" and f["uses"] > 0: g.apply(f["o"], f["o"].payload); f["uses"] -= 1
            else:
                t["hp"] -= atk
                if t["hp"] <= 0: (g.buildings if t in g.buildings else g.summons).remove(t)
        for f in g.fx:
            if f["kind"] == "trig" and f["cond"] == "approach" and f["uses"] > 0 and any(e["ring"] <= 3 for e in g.en): g.apply(f["o"], f["o"].payload); f["uses"] -= 1
        if g.hp <= 0:
            for f in g.fx:
                if f["kind"] == "trig" and f["cond"] == "death" and f["uses"] > 0 and g.hp <= 0:
                    g.hp = 1; g.apply(f["o"], f["o"].payload); f["uses"] -= 1
            if g.hp <= 0: g.failed = "사망"
        g.dmgb *= .75
    # --- one run
    def run(g):
        for o in g.bag:
            if o.fate == "passive": pass
        for si in range(g.stages):
            typ = g.RR.choice(list(STAGE_TYPES)); typ = g.cfg.get("force_type") or typ; ec, rc = STAGE_TYPES[typ]; g.stats[typ] += 1
            nb = sum(1 for o in g.bag if o.role == "build"); ns = sum(1 for o in g.bag if o.role == "summon" and not o.hostile); nn = max(1, len(g.bag))
            g.cap_b = g.cfg.get("cap_b", 6) + (g.cfg.get("hero_b", 0) if nb >= .4 * nn else 0); g.cap_s = g.cfg.get("cap_s", 5) + (g.cfg.get("hero_s", 0) if ns >= .4 * nn else 0)
            g0 = g.gold; died = False
            g.pool = {k: int(30 * rc) for k in RAW}; g.pool["land"] = int(g.cfg["land"] * rc) if g.cfg.get("land") else 10**9; g.en = []; g.summons = []; g.kills = 0; g.uses = collections.Counter(); g.amp = 1.0; g.dmgb = 0.0
            g.fx = [f for f in g.fx if f["o"].life in ("run", "forever")]; g.buildings = [b for b in g.buildings if b["life"] in ("run", "forever")]
            lvl = 1 + si; waves = {1: 3, 5: 4, 9: 5}
            g.disc = []; g.reshuffle(); g.hand = []
            for g.turn in range(1, g.turns_per + 1):
                if g.turn in waves:
                    for _ in range(max(1, round(waves[g.turn] * ec * (1 + g.cfg.get("grow", .35) * si)))): g.spawn(lvl)
                g.disc += g.hand; g.hand = []; g.mana = g.cfg["mana"]; g.drawn(g.cfg["hand"])
                g.bot_turn(); g.upkeep()
                if g.failed:
                    if g.failed == "사망" and g.cfg.get("death") == "forfeit": died = True; g.failed = None; g.deaths += 1; break
                    return g.result()
            # stage end: sell leftovers, pay rent
            if died: g.gold = min(g.gold, g0); g.res = dict.fromkeys(RAW, 0); g.hp = int(g.max_hp * .5)       # the stage's net gold and resources are lost
            else: g.stats["g_sale"] += int(sum(g.res.values()) * .3); g.gold += int(sum(g.res.values()) * .3); g.res = dict.fromkeys(RAW, 0)
            if g.gold < g.due[si]: g.failed = f"정산 실패(스테이지 {si+1})"; return g.result()
            g.gold -= g.due[si]; g.cleared += 1; g.hp = min(g.max_hp, g.hp + g.cfg["rest"])
            if g.pool_names and si < g.stages - 1 and not died:                                                       # reward: write one new orb
                cands = [g.RR.choice(g.pool_names) for _ in range(3 if g.reward_pick == "best3" else 1)]
                if g.reward_pick == "bestall": cands = g.pool_names
                g.bag.append(copy.copy(max(cands, key=g.pick_key or (lambda o: est_total_value(o) / (o.mana + .5))) if len(cands) > 1 else cands[0]))
        return g.result()
    def result(g): return {"src": dict(g.stats), "deaths": g.deaths, "cleared": g.cleared, "gold": g.gold, "hp": g.hp, "failed": g.failed, "score": 100 * g.cleared + g.gold, "kills": g.stats["kills"], "played": dict(g.played), "contrib": dict(g.contrib)}

STARTER = ["금화 주머니", "금화 주머니", "화염검", "화염검", "방패", "곡괭이", "씨앗", "병사"]
ALL_NAMES = sorted(n for n in V3 if n in V3)

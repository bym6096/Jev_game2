"""Hex stage engine for the web prototype (rules in Python; the browser only draws). Axial hex coordinates (q, r); player in the middle.
Same rule set as sim 'r4' (same-family decay, weak bonus, direct gold x0.25 is baked into the orbs, anti-farming, land limit, building cap with class bonus).
NUMBERS ARE PLACEHOLDERS."""
import random, copy, collections, itertools
DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
R = 5
TILES = [(q, r) for q in range(-R, R + 1) for r in range(max(-R, -q - R), min(R, -q + R) + 1)]
def hd(a, b): dq, dr = a[0] - b[0], a[1] - b[1]; return (abs(dq) + abs(dr) + abs(dq + dr)) // 2
def nb(p): return [(p[0] + d[0], p[1] + d[1]) for d in DIRS]
def key(p): return f"{p[0]},{p[1]}"
FAM = {"money": "gold", "steal": "gold", "damage": "dmg", "drain": "dmg", "guard": "def", "heal": "def", "control": "ctl", "debuff": "ctl", "harvest": "eco", "grow": "eco", "create": "eco", "process": "eco",
       "draw": "bag", "recycle": "bag", "trash": "bag", "tempo": "bag", "energy": "bag", "peek": "bag", "buff": "amp", "amplify": "amp", "remove": "misc", "transform": "misc"}
NT = {"single": 1, "line": 2, "around": 6, "wide": 99}
RAW = ("wood", "ore", "food")
STAGE_TYPES = {"balanced": dict(name="균형", enemy=1.0, trees=8, ores=6), "hostile": dict(name="적 많음", enemy=1.6, trees=4, ores=3), "rich": dict(name="자원 많음", enemy=.6, trees=14, ores=10)}
CFG = dict(hp=100, mana=6, hand=5, ehp=.5, eatk=.5, fam_decay=.6, weak_bonus=1.5, process_ratio=1.5, bounty0=2, bountyk=2, farm_bounty=.3, land=25, cap_b=3, hero_b=2, cap_s=3, hero_s=2, turns=15, due=150, lvl=1)

class HexGame:
    def __init__(s, orbs, stage_type="balanced", seed=None, cfg=None):
        s.cfg = dict(CFG); s.cfg.update(cfg or {}); s.R = random.Random(seed); s.stage_type = stage_type; st = STAGE_TYPES[stage_type]
        s.inst = {}; s.nid = 1; s.bag = []
        for o in orbs: s.add_orb(o)
        s.hp = s.max_hp = s.cfg["hp"]; s.shield = 0; s.gold = 8; s.res = {"wood": 6, "ore": 4, "food": 3}; s.items = 0
        s.tiles = {}
        free = [t for t in TILES if hd(t, (0, 0)) >= 2]; s.R.shuffle(free)
        near = [t for t in free if hd(t, (0, 0)) == 3]                      # guarantee reachable resources: tiles next to the placeable ring (distance 2)
        trees = [near.pop(), near.pop()]; ores = [near.pop(), near.pop()]
        for t in trees: s.tiles[t] = {"t": "tree", "amt": 12}; free.remove(t)
        for t in ores: s.tiles[t] = {"t": "ore", "amt": 12}; free.remove(t)
        for i in range(max(0, st["trees"] - 2)): s.tiles[free.pop()] = {"t": "tree", "amt": 12}
        for i in range(max(0, st["ores"] - 2)): s.tiles[free.pop()] = {"t": "ore", "amt": 12}
        s.land = s.cfg["land"] * (2 if stage_type == "rich" else 1 if stage_type == "balanced" else 1) if True else 0
        s.buildings = []; s.summons = []; s.enemies = []; s.fx = []; s.logs = []; s.kills = 0; s.turn = 0; s.phase = "setup"; s.result = None
        s.draw = []; s.disc = []; s.hand = []; s.mana = 0; s.amp = 1.0; s.dmgb = 0.0; s.fam_turn = collections.Counter(); s.g0 = s.gold; s.died = False; s.stats = collections.Counter()
        s.uid = 1; s.warned = set()
    # ---- bag
    def add_orb(s, o):
        i = s.nid; s.nid += 1; s.inst[i] = {"id": i, "o": copy.deepcopy(o), "uses": 0}; s.bag.append(i); return i
    def log(s, t): s.logs.append(t); s.logs = s.logs[-60:]
    def start(s):
        s.phase = "play"; s.turn = 0; nb_ = sum(1 for i in s.bag if s.inst[i]["o"]["role"] == "build"); ns = sum(1 for i in s.bag if s.inst[i]["o"]["role"] == "summon" and not s.inst[i]["o"]["hostile"]); n = max(1, len(s.bag))
        s.cap_b = s.cfg["cap_b"] + (s.cfg["hero_b"] if nb_ >= .4 * n else 0); s.cap_s = s.cfg["cap_s"] + (s.cfg["hero_s"] if ns >= .4 * n else 0)
        if nb_ >= .4 * n: s.log(f"주머니의 건물 구슬이 많아 '건축가' 전직: 건물 {s.cap_b}칸")
        s.draw = [i for i in s.bag if s.inst[i]["o"]["fate"] != "passive"]; s.R.shuffle(s.draw); s.disc = []; s.hand = []
        s.next_turn()
    def drawn(s, n):
        for _ in range(n):
            if not s.draw:
                s.draw = [i for i in s.disc if i in s.bag]; s.disc = []; s.R.shuffle(s.draw)
            if s.draw: s.hand.append(s.draw.pop())
    def next_turn(s):
        s.turn += 1
        if s.turn > s.cfg["turns"]: return s.finish()
        waves = {1: 3, 5: 4, 9: 5}
        if s.turn in waves:
            n = max(1, round(waves[s.turn] * STAGE_TYPES[s.stage_type]["enemy"]));
            for _ in range(n): s.spawn(s.cfg["lvl"])
            s.log(f"{s.turn}턴: 적 {n}마리가 가장자리에 나타났다")
        s.disc += s.hand; s.hand = []; s.mana = s.cfg["mana"]; s.fam_turn = collections.Counter(); s.drawn(s.cfg["hand"])
    # ---- spawn
    def occupied(s): 
        o = {(0, 0)}; o |= {(b["q"], b["r"]) for b in s.buildings}; o |= {(u["q"], u["r"]) for u in s.summons}; o |= {(e["q"], e["r"]) for e in s.enemies}; return o
    def spawn(s, lvl, farm=False):
        occ = s.occupied(); edge = [t for t in TILES if hd(t, (0, 0)) == R and t not in occ and t not in s.tiles]
        if not edge: return
        t = s.R.choice(edge); bounty = s.cfg["bounty0"] + s.cfg["bountyk"] * lvl
        if farm: bounty = max(1, round(bounty * s.cfg["farm_bounty"]))
        s.enemies.append({"id": s.uid, "q": t[0], "r": t[1], "hp": (14 + 8 * lvl) * s.cfg["ehp"], "max": (14 + 8 * lvl) * s.cfg["ehp"], "atk": (3 + 2 * lvl) * s.cfg["eatk"], "lvl": lvl, "bounty": bounty, "stun": 0, "weak": 0}); s.uid += 1
    # ---- play rules
    def reason(s, iid):
        o = s.inst[iid]["o"]
        if o.get("scribble"): pass
        if o["mana"] > s.mana: return "마나 부족"
        if o["role"] == "build":
            mt, x, y = o["bcost"]
            if len(s.buildings) >= s.cap_b: return f"건물 칸 부족({s.cap_b}칸)"
            if mt == "gold":
                if s.gold < x + y: return "골드 부족"
            elif s.res[mt] < x or s.gold < y: return "재료 또는 골드 부족"
        if o["role"] == "summon" and not o["hostile"] and len(s.summons) >= s.cap_s: return f"소환물 칸 부족({s.cap_s}칸)"
        return None
    def needs_tile(s, o): return o["role"] == "build" or (o["role"] == "summon" and not o["hostile"])
    def valid_tiles(s, iid):
        o = s.inst[iid]["o"]; occ = s.occupied()
        lim = 2
        return [t for t in TILES if 1 <= hd(t, (0, 0)) <= lim and t not in occ and t not in s.tiles]
    def tile_hint(s, o, t):
        """Good tiles: next to a matching resource tile (harvest) or next to a building of a different family (synergy)."""
        verbs = [p[0] for p in o["payload"]]
        if "harvest" in verbs:
            kind = {"wood": "tree", "ore": "ore"}.get(next((p[2] for p in o["payload"] if p[0] == "harvest"), None))
            if kind and any(s.tiles.get(n, {}).get("t") == kind and s.tiles[n]["amt"] > 0 for n in nb(t)): return True
        fam = FAM.get(o["payload"][0][0])
        return any(FAM.get(b["o"]["payload"][0][0]) not in (None, fam) for b in s.buildings if hd((b["q"], b["r"]), t) == 1)
    def play(s, hand_idx, tile=None):
        if s.phase != "play": return {"error": "플레이 중이 아닙니다"}
        if hand_idx < 0 or hand_idx >= len(s.hand): return {"error": "손패에 없는 구슬입니다"}
        iid = s.hand[hand_idx]; it = s.inst[iid]; o = it["o"]; why = s.reason(iid)
        if why: return {"error": why}
        if s.needs_tile(o):
            if tile is None or tuple(tile) not in s.valid_tiles(iid): return {"error": "놓을 수 있는 칸을 고르세요", "need_tile": True}
        s.mana -= o["mana"]; it["uses"] += 1; s.stats["plays"] += 1
        fam = FAM.get(o["payload"][0][0], "misc"); fm = s.cfg["fam_decay"] ** s.fam_turn[fam]; 
        if o["role"] == "build":
            mt, x, y = o["bcost"]
            if mt == "gold": s.gold -= x + y
            else: s.res[mt] -= x; s.gold -= y
            t = tuple(tile); s.buildings.append({"id": s.uid, "iid": iid, "q": t[0], "r": t[1], "hp": o["hp"], "max": o["hp"], "age": 0, "o": o}); s.uid += 1; s.log(f"건물 설치: {o['name']}")
        elif o["role"] == "summon":
            if o["hostile"]:
                for _ in range(2): s.spawn(o["lvl"], farm=True)
                s.log(f"{o['name']}: 적대 웨이브가 나타났다")
            else:
                t = tuple(tile); s.summons.append({"id": s.uid, "iid": iid, "q": t[0], "r": t[1], "hp": o["hp"], "max": o["hp"], "o": o}); s.uid += 1; s.log(f"소환: {o['name']}")
        else:
            s.fam_turn[fam] += 1
            if o["trig"] != "none": s.fx.append({"kind": "trig", "iid": iid, "o": o, "cond": o["trig"], "uses": 1 if o["life"] == "instant" else 3}); s.log(f"{o['name']}: 발동 대기({o['trig']})")
            elif o["timing"] == "delayed": s.fx.append({"kind": "delay", "iid": iid, "o": o, "at": s.turn + o["delay"]}); s.log(f"{o['name']}: {o['delay']}턴 뒤 발동")
            elif o["life"] == "instant": s.apply(o, o["payload"], fm)
            elif o["bag_only"]: s.apply(o, o["payload"], fm); s.fx.append({"kind": "dur", "iid": iid, "o": o, "left": 3 if o["life"] == "turns" else 10, "charges": 3})
            else: s.apply(o, o["payload"], fm); s.fx.append({"kind": "dur", "iid": iid, "o": o, "left": 3 if o["life"] == "turns" else 10 ** 6, "charges": 99})
        if o["payload"][0][0] != "amplify": s.amp = 1.0
        s.hand.remove(iid)
        if o["fate"] == "used_up": s.bag.remove(iid); s.stats["exhausted"] += 1
        else: s.disc.append(iid)
        s.check_end_of_stage_death(); return {"ok": True}
    # ---- effects
    def targets(s, o, src):
        es = sorted(s.enemies, key=lambda e: (hd((e["q"], e["r"]), src), e["id"]))
        if src != (0, 0): es = [e for e in es if hd((e["q"], e["r"]), src) <= 3]
        rng = o["rng"]
        if rng == "single": return es[:1]
        if rng == "line": return es[:2]
        if rng == "around":
            if not es: return []
            c = (es[0]["q"], es[0]["r"]); return [e for e in es if hd((e["q"], e["r"]), c) <= 1][:6]
        return es
    def apply(s, o, payload, mult=1.0, src=(0, 0), building=None):
        for v, m, mt in payload:
            m = max(1, round(m * mult * s.amp)); uses = s.inst[building["iid"]]["uses"] if building else 0
            if o["mod"] == "random": m = max(1, round(m * s.R.uniform(.5, 1.5)))
            if o["mod"] == "network": n = sum(1 for b in s.buildings if hd((b["q"], b["r"]), src) == 1) if building else len(s.buildings); m = round(m * (1 + .15 * n))
            if o["mod"] == "scaling": m = round(m * (1 + .1 * s.inst.get(building["iid"] if building else -1, {"uses": 0})["uses"]))
            if o["mod"] == "risky": s.hp -= max(1, m // 4)
            if building:
                fams = {FAM.get(x["o"]["payload"][0][0]) for x in s.buildings if hd((x["q"], x["r"]), src) == 1 and x is not building} - {FAM.get(o["payload"][0][0])}
                if fams: m = round(m * (1 + .2 * len(fams))); s.stats["adj_bonus"] += 1
            bonus = 1 + s.dmgb
            if v in ("damage", "drain"):
                for e in s.targets(o, src):
                    b2 = bonus * (s.cfg["weak_bonus"] if (e["weak"] > 0 or e["stun"] > 0) else 1.0); e["hp"] -= m * b2
                    if v == "drain": s.hp = min(s.max_hp, s.hp + m // 2)
                s.reap()
            elif v == "guard": s.shield = min(40, s.shield + m)
            elif v == "heal": s.hp = min(s.max_hp, s.hp + m)
            elif v == "money": s.gold += m; s.stats["g_money"] += m
            elif v == "steal":
                if s.enemies: s.gold += m; s.stats["g_money"] += m
            elif v in ("harvest", "grow") and mt == "gold": s.gold += m
            elif v == "harvest":
                kind = {"wood": "tree", "ore": "ore"}.get(mt); got = 0
                if kind:
                    lim = 1 if building else 3
                    cands = sorted([t for t, d in s.tiles.items() if d["t"] == kind and d["amt"] > 0 and hd(t, src) <= lim], key=lambda t: hd(t, src))
                    need = m
                    for t in cands:
                        k = min(need, s.tiles[t]["amt"]); s.tiles[t]["amt"] -= k; need -= k; got += k
                        if need <= 0: break
                    if got == 0 and (o["name"], src) not in s.warned: s.warned.add((o["name"], src)); s.log(f"{o['name']}: 근처에 {'나무' if kind=='tree' else '광석'} 타일이 없다")
                    elif building and cands and hd(cands[0], src) == 1 and got: got = round(got * 1.5)
                else:
                    k = min(m, s.land); s.land -= k; got = k
                s.res[mt or "ore"] += got
            elif v == "grow":
                k = min(m, s.land); s.land -= k; s.res[mt or "food"] += k
            elif v == "process":
                n = 0
                for k in RAW:
                    t = min(m - n, s.res[k]); s.res[k] -= t; n += t
                g = int(n * s.cfg["process_ratio"]); s.gold += g; s.stats["g_process"] += g
            elif v == "buff": s.dmgb = min(1.0, s.dmgb + m / 60)
            elif v == "debuff":
                for e in s.targets(o, src): e["weak"] = max(e["weak"], 3)
            elif v == "control":
                n = 1 if o["life"] in ("stage", "run", "forever") else 1 + int(o["B"] // 30)
                for e in s.targets(o, src): e["stun"] = max(e["stun"], n)
            elif v == "draw": s.drawn(1 + int(o["pe"] // 2.5))
            elif v == "recycle":
                if s.disc: s.hand.append(s.disc.pop(s.R.randrange(len(s.disc))))
            elif v == "trash":
                c = [i for i in s.disc if s.inst[i]["o"]["name"] != o["name"]]
                if c: w = c[0]; s.disc.remove(w); s.bag.remove(w); s.log(f"폐기: {s.inst[w]['o']['name']}")
            elif v == "tempo": s.mana += 1
            elif v == "energy": s.mana += max(1, int(o["pe"] // 1.5))
            elif v == "create":
                if mt == "gold": s.gold += 2
                elif mt: s.res[mt] += 2
                else: s.items += 1
            elif v == "amplify": s.amp = 2.0
            elif v == "peek": s.log("주머니 위: " + ", ".join(s.inst[i]["o"]["name"] for i in s.draw[-3:][::-1]))
    def reap(s):
        for e in [e for e in s.enemies if e["hp"] <= 0]:
            s.enemies.remove(e); s.gold += e["bounty"]; s.kills += 1; s.stats["g_bounty"] += e["bounty"]
    # ---- end turn
    def end_turn(s):
        if s.phase != "play": return {"error": "플레이 중이 아닙니다"}
        s.amp = 1.0
        if s.items and s.hp < s.max_hp * .5: s.items -= 1; s.hp = min(s.max_hp, s.hp + 15); s.log("아이템 사용: 체력 15")
        if s.res["food"] >= 2 and s.hp < s.max_hp * .6: s.res["food"] -= 2; s.hp = min(s.max_hp, s.hp + 6); s.log("식량을 먹었다: 체력 6")
        # effects
        for f in list(s.fx):
            o = f["o"]
            if f["kind"] == "delay" and s.turn >= f["at"]: s.apply(o, o["payload"]); s.fx.remove(f); s.log(f"{o['name']} 발동")
            elif f["kind"] == "dur":
                if f["left"] <= 0 or f["charges"] <= 0: s.fx.remove(f); continue
                s.apply(o, o["payload"]); f["left"] -= 1; f["charges"] -= 1 if o["bag_only"] else 0
        for i in s.bag:
            o = s.inst[i]["o"]
            if o["fate"] == "passive" and o["role"] == "cast" and o["trig"] == "none": s.apply(o, o["payload"], .7)
        for b in list(s.buildings):
            b["age"] += 1; o = b["o"]
            if o["timing"] == "delayed" and b["age"] <= o["delay"]: continue
            src = (b["q"], b["r"])
            if o["trig"] == "approach":
                if any(hd((e["q"], e["r"]), src) <= 3 for e in s.enemies) and b.get("fired", 0) < 3: s.apply(o, o["payload"], 1.0, src, b); b["fired"] = b.get("fired", 0) + 1
            else: s.apply(o, o["payload"], 1.0, src, b)
        for u in list(s.summons): s.apply(u["o"], u["o"]["payload"], 1.0, (u["q"], u["r"]), u)
        s.enemy_phase()
        for f in s.fx:
            if f["kind"] == "trig" and f["cond"] == "approach" and f["uses"] > 0 and any(hd((e["q"], e["r"]), (0, 0)) <= 3 for e in s.enemies): s.apply(f["o"], f["o"]["payload"]); f["uses"] -= 1
        s.dmgb *= .75
        if s.hp <= 0:
            for f in s.fx:
                if f["kind"] == "trig" and f["cond"] == "death" and f["uses"] > 0 and s.hp <= 0: s.hp = 1; s.apply(f["o"], f["o"]["payload"]); f["uses"] -= 1; s.log(f"{f['o']['name']}: 죽음에서 돌아왔다")
        if s.hp <= 0: s.died = True; s.log("쓰러졌다 — 이 스테이지에서 번 골드와 자원을 잃는다"); return s.finish()
        s.next_turn(); return {"ok": True}
    def check_end_of_stage_death(s):
        if s.hp <= 0 and s.phase == "play": s.died = True; s.finish()
    def enemy_phase(s):
        s.enemies.sort(key=lambda e: hd((e["q"], e["r"]), (0, 0)))
        for e in list(s.enemies):
            if e["hp"] <= 0: continue
            if e["stun"] > 0: e["stun"] -= 1; continue
            pos = (e["q"], e["r"]); atk = max(1, e["atk"] - (3 if e["weak"] > 0 else 0)); e["weak"] = max(0, e["weak"] - 1)
            tg = []
            if hd(pos, (0, 0)) == 1: tg.append("p")
            tg += [b for b in s.buildings if hd(pos, (b["q"], b["r"])) == 1]; tg += [u for u in s.summons if hd(pos, (u["q"], u["r"])) == 1]
            if tg:
                t = s.R.choice(tg)
                if t == "p":
                    d = atk
                    if s.shield: a = min(s.shield, d); s.shield -= a; d -= a
                    s.hp -= d; s.stats["dmg_taken"] += atk
                    for f in list(s.fx):
                        if f["kind"] == "trig" and f["cond"] == "hit" and f["uses"] > 0: s.apply(f["o"], f["o"]["payload"]); f["uses"] -= 1
                else:
                    t["hp"] -= atk
                    if t["hp"] <= 0: (s.buildings if t in s.buildings else s.summons).remove(t); s.log(f"{t['o']['name']}이(가) 파괴되었다")
                continue
            occ = s.occupied(); opts = [p for p in nb(pos) if p in set(TILES) and p not in occ and p not in s.tiles]
            if opts:
                best = min(hd(p, (0, 0)) for p in opts)
                if best < hd(pos, (0, 0)) or True:
                    c = [p for p in opts if hd(p, (0, 0)) == best]; p = s.R.choice(c)
                    if hd(p, (0, 0)) < hd(pos, (0, 0)) or not [x for x in opts if hd(x, (0, 0)) < hd(pos, (0, 0))]: e["q"], e["r"] = p
    # ---- finish
    def finish(s):
        s.phase = "over"
        if s.died: s.gold = min(s.gold, s.g0); s.res = dict.fromkeys(RAW, 0)
        else:
            sale = int(sum(s.res.values()) * .3); s.gold += sale; s.res = dict.fromkeys(RAW, 0)
        ok = s.gold >= s.cfg["due"] and not (s.died and s.gold < s.cfg["due"])
        s.result = {"pass": bool(s.gold >= s.cfg["due"]), "gold": s.gold, "due": s.cfg["due"], "died": s.died, "kills": s.kills, "turns": min(s.turn, s.cfg["turns"]), "src": dict(s.stats)}
        s.log(("정산 통과" if s.result["pass"] else "정산 실패") + f": 골드 {s.gold} / 낼 돈 {s.cfg['due']}")
        return {"ok": True, "over": True}
    # ---- view
    def view(s):
        playable = []
        for idx, iid in enumerate(s.hand):
            o = s.inst[iid]["o"]; why = s.reason(iid) if s.phase == "play" else "대기"
            vt = s.valid_tiles(iid) if (s.needs_tile(o) and not why) else []
            playable.append({"idx": idx, "iid": iid, "o": o, "why": why, "need_tile": s.needs_tile(o), "tiles": [list(t) for t in vt], "hint": [list(t) for t in vt if s.tile_hint(o, t)]})
        return {"phase": s.phase, "turn": s.turn, "turns": s.cfg["turns"], "stage_type": s.stage_type, "stage_name": STAGE_TYPES[s.stage_type]["name"], "hp": round(s.hp), "max_hp": s.max_hp, "shield": s.shield, "mana": s.mana, "max_mana": s.cfg["mana"],
                "gold": s.gold, "res": s.res, "items": s.items, "due": s.cfg["due"], "land": s.land, "bag": len(s.bag), "draw": len(s.draw), "disc": len(s.disc), "dmgb": round(s.dmgb, 2),
                "tiles": [{"q": t[0], "r": t[1], **d} for t, d in s.tiles.items() if d["amt"] > 0], "hand": playable,
                "buildings": [{"id": b["id"], "q": b["q"], "r": b["r"], "hp": round(b["hp"]), "max": b["max"], "name": b["o"]["name"], "fam": FAM.get(b["o"]["payload"][0][0])} for b in s.buildings],
                "summons": [{"id": u["id"], "q": u["q"], "r": u["r"], "hp": round(u["hp"]), "max": u["max"], "name": u["o"]["name"]} for u in s.summons],
                "enemies": [{"id": e["id"], "q": e["q"], "r": e["r"], "hp": round(e["hp"]), "max": round(e["max"]), "lvl": e["lvl"], "stun": e["stun"], "weak": e["weak"]} for e in s.enemies],
                "fx": [{"name": f["o"]["name"], "kind": f["kind"], "cond": f.get("cond")} for f in s.fx], "log": s.logs[-14:], "result": s.result, "caps": {"b": getattr(s, "cap_b", s.cfg["cap_b"]), "s": getattr(s, "cap_s", s.cfg["cap_s"])},
                "buildings_n": len(s.buildings), "summons_n": len(s.summons)}

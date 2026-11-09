"""Hex stage engine for the web prototype (rules in Python; the browser only draws). Axial hex coordinates (q, r); player in the middle.
Same rule set as sim 'r4' (same-family decay, weak bonus, direct gold x0.25 is baked into the orbs, anti-farming, land limit, building cap with class bonus).
NUMBERS ARE PLACEHOLDERS."""
import random, copy, collections, itertools, math
DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
R = 5
TILES = [(q, r) for q in range(-R, R + 1) for r in range(max(-R, -q - R), min(R, -q + R) + 1)]
def hd(a, b): dq, dr = a[0] - b[0], a[1] - b[1]; return (abs(dq) + abs(dr) + abs(dq + dr)) // 2
def nb(p): return [(p[0] + d[0], p[1] + d[1]) for d in DIRS]
def key(p): return f"{p[0]},{p[1]}"
def josa(w, a="이", b="가"):
    """받침이 있으면 a(이·은·을), 없으면 b(가·는·를). 한글이 아니면 a(b) 꼴."""
    c = w[-1] if w else ""
    if not ("가" <= c <= "힣"): return f"{w}{a}({b})"
    return w + (a if (ord(c) - 0xAC00) % 28 else b)
FAM = {"money": "gold", "steal": "gold", "damage": "dmg", "drain": "dmg", "burn": "dmg", "guard": "def", "heal": "def", "control": "ctl", "debuff": "ctl", "harvest": "eco", "grow": "eco", "create": "eco", "process": "eco",
       "draw": "bag", "recycle": "bag", "trash": "bag", "tempo": "bag", "energy": "bag", "peek": "bag", "buff": "amp", "amplify": "amp", "remove": "misc", "transform": "misc"}
ENEMY_V = ("damage", "drain", "debuff", "control", "burn")   # 적을 겨냥하는 동사
TURN_V = ("draw", "recycle", "tempo", "energy", "peek")
def draw_n(o): return 1 + int(o["pe"] // 2.5)                       # '더 뽑기'로 뽑는 구슬 수
def energy_gain(o): return max(2, 1 + int(o["pe"] // 1.5))          # '마나 충전'으로 얻는 마나(최소 2: 가격 1을 내고도 남게)              # 그 턴의 손패·마나에 작용하는 동사(턴 끝에 생기면 다음 턴으로 미룬다)
# ---- 시너지: 사건 알림(emit) · 화상 · 종류별 증폭(buff) · 구슬 태그. 숫자는 임시.
BURN_DMG, BURN_MAX = 2, 8          # 화상 1중첩당 턴 피해 / 한 적의 최대 중첩(턴마다 1중첩 줄어든다)
TRIG_PER_TURN = 2                  # 반응 하나가 한 턴에 터질 수 있는 최대 횟수(무한 연쇄 방지)
MULT_CAP = 1.5                     # 종류별 증폭의 합 상한(+150%)
SALE_RATE = .3                     # 스테이지 끝에 남은 자원을 골드로 파는 비율(가치 모델이 자원 값어치의 바닥으로 씀)
BOOST_KINDS = ("dmg", "burn", "income", "growth", "defense", "unit", "bounty")   # buff 동사가 키우는 것: 피해·화상·골드 수입·채집/재배·방어/회복·건물과 소환물
KIND = {"damage": "dmg", "drain": "dmg", "money": "income", "steal": "income", "process": "income", "harvest": "growth", "grow": "growth", "guard": "defense", "heal": "defense"}
ECO_V = ("harvest", "grow", "create", "process", "money", "steal")
COND_KO = {"hit": "피격 시", "death": "사망 시", "orb": "다른 구슬을 쓸 때", "approach": "적이 다가오면", "orb_attack": "공격 구슬을 쓸 때", "orb_eco": "채집·수입 구슬을 쓸 때", "orb_plant": "식물 구슬을 쓸 때",
           "orb_build": "건물 구슬을 쓸 때", "orb_summon": "소환 구슬을 쓸 때", "orb_defense": "방어·회복 구슬을 쓸 때", "kill": "적을 처치할 때", "harvest": "자원을 거둘 때"}
BOOST_KO = {"dmg": "피해", "burn": "화상", "income": "골드 수입", "growth": "채집·재배", "defense": "방어·회복", "unit": "건물·소환물", "bounty": "처치 보상"}
def tags(o):
    """구슬이 어떤 종류인가 — 'X 구슬을 쓸 때' 반응이 보는 꼬리표."""
    vs = [p[0] for p in o["payload"]]; t = set()
    if o["role"] == "build": t.add("build")
    if is_plant(o): t.add("plant")
    if o["role"] == "summon" and not o["hostile"]: t.add("summon")
    if o["role"] == "cast" and any(v in ENEMY_V for v in vs): t.add("attack")
    if any(v in ECO_V for v in vs): t.add("eco")
    if any(v in ("guard", "heal") for v in vs): t.add("defense")
    return t
def trig_uses(o): return {"instant": 2, "turns": 4}.get(o["life"], 10 ** 6)       # 반응을 깔면 몇 번 터지는가(스테이지 이상이면 스테이지 끝까지, 단 턴당 TRIG_PER_TURN회)
def trig_match(cond, kind, info):
    """반응 조건 cond 가 사건 kind 에 맞는가. cond: orb(아무 구슬)·orb_<태그>·kill·harvest·hit·death(건물·소환물이 부서질 때, kind=lost)"""
    if cond == "orb": return kind == "orb"
    if cond.startswith("orb_"): return kind == "orb" and cond[4:] in info.get("tags", ())
    if cond == "death": return kind == "lost"
    return cond == kind
HP_REF = .5                                          # 구슬 수치(측정 모델의 크기 B)가 가정한 적 체력 배율. CFG['ehp']가 이보다 크면 건물·소환물·지속 피해 수치를 그 비율만큼 올린다(orbs.shape)
PLACE_RANGE = 1                                      # 건물·식물·소환물을 놓을 수 있는 거리(내 위치에 인접한 칸만; 이동 구슬은 따로 구슬이 정한 칸 수)
CAST_RANGE = 4                                       # 플레이어가 쓴 공격 구슬의 사거리(내 위치 기준 칸)
UNIT_RANGE = {"soldier": 1, "worker": 1, "beast": 1, "spirit": 2, "construct": 2}   # 소환물 종류별 공격 사거리(병사는 근접)
def unit_range(o): return 2 if o["role"] == "build" else UNIT_RANGE.get(o.get("unit"), 1)   # 건물은 2칸
ICON = {"wood": "🌲", "ore": "⛏", "food": "🌾", "gold": "🪙"}
def sustained(o):
    """한 번 쓰면 스테이지(이상) 내내 이어지는 시전 구슬. 효과가 쌓이지 않으므로 값어치가 '한 번 쓴 값'이고, 쓰면 그 스테이지 동안 소멸한다(슬레이 더 스파이어의 소멸)."""
    return o["role"] == "cast" and o["life"] in ("stage", "run", "forever")
def manual_target(o):   # 플레이어가 직접 대상을 고르는 구슬: 즉발 시전 중 적을 겨냥하는 것(지속·지연·조건부·건물·소환물은 자동으로 가장 가까운 적)
    return o["role"] == "cast" and o["life"] == "instant" and o["timing"] != "delayed" and o["trig"] == "none" and o["fate"] != "passive" and any(p[0] in ENEMY_V for p in o["payload"])
NT = {"single": 1, "line": 2, "around": 6, "wide": 99}
RAW = ("wood", "ore", "food")
PASSIVE_K = .7                                      # 자동 구슬(손패에 안 오고 주머니에 있으면 일함)의 효과 배율
STAGE_TYPES = {"balanced": dict(name="균형", enemy=1.0, trees=8, ores=6), "hostile": dict(name="적 많음", enemy=1.6, trees=4, ores=3), "rich": dict(name="자원 많음", enemy=.6, trees=14, ores=10)}
WAVES = {1: 3, 5: 4, 9: 5}  # 등장 턴: 기본 적 수(스테이지 종류 배율은 별도)
CFG = dict(hp=100, mana=6, hand=5, ehp=1.5, eatk=.5, fam_decay=.6, weak_bonus=1.5, process_ratio=1.5, bounty0=3, bountyk=3, farm_bounty=.3, land=80, tile_amt=40, cap_b=3, hero_b=2, cap_s=3, hero_s=2, turns=15, due=150, lvl=1, cap_p=3, grow_turns=2, move_range=2,
           # ---- 런(2026-11-09 디렉터 결정: 사망 = 런 종료, 보스 스테이지도 정산, 영지 효율 감소 없음, 명성 대신 처치 보상을 키우는 구슬). 숫자는 run_bot.py로 맞춘 임시값
           stages=12, due_r=1.4, boss_at=(4, 8, 12), mana_every=0, lvl_every=2, wave_grow=.25, rest_heal=.3, boss_hp=10, boss_atk=2, boss_bounty=8, boss_call=3)
STAGE_HINT = {"balanced": "평탄한 들판", "hostile": "발소리가 많다", "rich": "숲과 광맥"}      # 출구 힌트에 보이는 지형 말
REWARD_TIERS = (("평범한", .6), ("깨끗한", .3), ("금박", .1))                                 # 출구 너머 스테이지에 도착하면 받는 빈 구슬 등급(보스를 깨면 금박 하나 더)
def due_for(n, cfg=CFG): return int(round(cfg["due"] * cfg["due_r"] ** (n - 1) / 5) * 5)      # n번째 스테이지의 정산액(5 단위)
def lvl_for(n, cfg=CFG): return cfg["lvl"] + (n - 1) // cfg["lvl_every"]

def is_plant(o):   # 식물 = 경작지를 쓰는 건물형 구슬: 재배(grow) 또는 식량 수확(harvest food)
    if o["role"] != "build" or not o["payload"]: return False
    v, _, mt = o["payload"][0]; return v == "grow" or (v == "harvest" and mt == "food")

class HexGame:
    pos = (0, 0)   # 플레이어 위치(이동 구슬로 바뀜)
    def __init__(s, orbs, stage_type="balanced", seed=None, cfg=None):
        s.cfg = dict(CFG); s.cfg.update(cfg or {}); s.R = random.Random(seed); s.stage_type = stage_type; st = STAGE_TYPES[stage_type]
        s.inst = {}; s.nid = 1; s.bag = []
        for o in orbs: s.add_orb(o)
        s.hp = s.max_hp = s.cfg["hp"]; s.shield = 0; s.gold = 8; s.res = {"wood": 6, "ore": 4, "food": 3}; s.items = 0
        s.stage_n = 1; s.estates = []; s.exits = []; s.history = []; s.reward = None; s.clear = False
        s.logs = []; s.fx = []; s.kills = 0; s.stats = collections.Counter(); s.uid = 1
        s.new_map(stage_type)
    def new_map(s, stage_type):
        """스테이지 하나의 맵·적·칸을 새로 만든다(런의 골드·자원·주머니·영지·체력·런 지속 효과는 그대로)."""
        s.stage_type = stage_type; st = STAGE_TYPES[stage_type]; s.pos = (0, 0)
        s.due = due_for(s.stage_n, s.cfg); s.lvl = lvl_for(s.stage_n, s.cfg); s.max_mana = s.cfg["mana"] + ((s.stage_n - 1) // s.cfg["mana_every"] if s.cfg["mana_every"] else 0)      # 2026-11-09 디렉터: 스테이지마다 자동 성장은 하지 않음(나중에 상점·레벨업으로). 0 = 끔
        s.boss = s.stage_n in tuple(s.cfg["boss_at"])
        s.tiles = {}
        free = [t for t in TILES if hd(t, (0, 0)) >= 2]; s.R.shuffle(free)
        near = [t for t in free if hd(t, (0, 0)) == 3]                      # guarantee reachable resources: tiles next to the placeable ring (distance 2)
        trees = [near.pop(), near.pop()]; ores = [near.pop(), near.pop()]
        for t in trees: s.tiles[t] = {"t": "tree", "amt": s.tile_amt()}; free.remove(t)
        for t in ores: s.tiles[t] = {"t": "ore", "amt": s.tile_amt()}; free.remove(t)
        for i in range(max(0, st["trees"] - 2)): s.tiles[free.pop()] = {"t": "tree", "amt": s.tile_amt()}
        for i in range(max(0, st["ores"] - 2)): s.tiles[free.pop()] = {"t": "ore", "amt": s.tile_amt()}
        s.land = s.cfg["land"] * (2 if stage_type == "rich" else 1 if stage_type == "balanced" else 1) if True else 0
        s.buildings = []; s.summons = []; s.enemies = []; s.turn = 0; s.phase = "setup"; s.result = None; s.shield = 0
        s.fx = [f for f in s.fx if f["o"]["life"] in ("run", "forever") and f["o"]["fate"] != "passive"]      # 런·영구 지속 효과만 다음 스테이지로(자동 반응은 start에서 다시 깐다)
        s.draw = []; s.disc = []; s.exh = []; s.hand = []; s.mana = 0; s.amp = 1.0; s.dmgb = 0.0; s.fam_turn = collections.Counter(); s.g0 = s.gold; s.died = False
        s.stage_kills = 0; s.gold_hist = []; s.warned = set()
    # ---- bag
    def add_orb(s, o):
        i = s.nid; s.nid += 1; s.inst[i] = {"id": i, "o": copy.deepcopy(o), "uses": 0}; s.bag.append(i); return i
    def log(s, t): s.logs.append(t); s.logs = s.logs[-60:]; s.recent = getattr(s, "recent", []) + [t]
    def tile_amt(s): return round(s.cfg["tile_amt"] * s.R.uniform(.75, 1.25))   # 자원 칸 하나의 양(스테이지당 수십)
    def ev(s, what, a, b=None, **kw):   # 화면 이펙트용 사건 기록(공격·생산·발동). 위치는 칸 좌표
        e = getattr(s, "events", None)
        if e is None: e = s.events = []
        e.append(dict(k=what, a=list(a), b=(list(b) if b else None), **kw))
    def start(s):
        s.phase = "play"; s.turn = 0; nb_ = sum(1 for i in s.bag if s.inst[i]["o"]["role"] == "build" and not is_plant(s.inst[i]["o"])); ns = sum(1 for i in s.bag if s.inst[i]["o"]["role"] == "summon" and not s.inst[i]["o"]["hostile"]); n = max(1, len(s.bag))
        s.cap_b = s.cfg["cap_b"] + (s.cfg["hero_b"] if nb_ >= .4 * n else 0); s.cap_s = s.cfg["cap_s"] + (s.cfg["hero_s"] if ns >= .4 * n else 0)
        if nb_ >= .4 * n: s.log(f"주머니의 건물 구슬이 많아 '건축가' 전직: 건물 {s.cap_b}칸")
        s.draw = [i for i in s.bag if s.inst[i]["o"]["fate"] != "passive"]; s.R.shuffle(s.draw); s.disc = []; s.exh = []; s.hand = []
        for i in s.bag:                                          # 자동(주머니에 있으면 자동) 반응 구슬: 손패에 오지 않으니 스테이지 시작에 반응을 깔아 둔다(자동 효과와 같은 ×PASSIVE_K)
            o = s.inst[i]["o"]
            if o["fate"] == "passive" and o["role"] == "cast" and o["trig"] != "none": s.add_trig(i, o, PASSIVE_K)
        s.next_turn()
    def drawn(s, n):
        for _ in range(n):
            if not s.draw:
                s.draw = [i for i in s.disc if i in s.bag]; s.disc = []; s.R.shuffle(s.draw)
            if s.draw: s.hand.append(s.draw.pop())
    def next_turn(s):
        s.turn += 1
        if s.turn > s.cfg["turns"]: return s.finish()
        if s.turn in WAVES:
            n = s.wave_size(s.turn)
            for k in range(n): s.spawn(s.lvl + (1 if s.turn >= 9 and k % 3 == 2 else 0))      # 마지막 웨이브엔 한 단계 높은 적이 섞인다
            s.log(f"{s.turn}턴: 적 {n}마리가 가장자리에 나타났다")
        if s.boss and s.turn == 1: s.spawn_boss()
        if s.boss and s.turn > 1 and (s.turn - 1) % s.cfg["boss_call"] == 0:
            b = next((e for e in s.enemies if e.get("boss")), None)
            if b:
                for _ in range(2): s.spawn(s.lvl, near=(b["q"], b["r"]))
                s.log(f"보스가 졸개 2마리를 불렀다")
        s.gold_hist.append(s.gold)
        for f in s.fx: f["tn"] = 0                              # 반응의 턴당 횟수 초기화
        for b in s.buildings + s.summons: b["tn"] = 0
        s.disc += [i for i in s.hand if not s.inst[i]["o"].get("copy")]; s.hand = []; s.mana = s.max_mana; s.fam_turn = collections.Counter(); s.drawn(s.cfg["hand"])
        s.ending = False; pend = getattr(s, "pending", []); s.pending = []
        if pend:
            for v, o in pend: s.apply(o, [(v, 1, None)])
            n = collections.Counter(v for v, _ in pend); s.log("턴 시작 보너스: " + ", ".join(f"{ {'draw': '더 뽑기', 'recycle': '되돌림', 'tempo': '마나', 'energy': '마나', 'peek': '엿보기'}[v]} ×{k}" for v, k in n.items()))
    # ---- spawn
    def occupied(s): 
        o = {s.pos}; o |= {(b["q"], b["r"]) for b in s.buildings}; o |= {(u["q"], u["r"]) for u in s.summons}; o |= {(e["q"], e["r"]) for e in s.enemies}; return o
    def wave_size(s, t): return max(1, round(WAVES[t] * STAGE_TYPES[s.stage_type]["enemy"] * (1 + s.cfg["wave_grow"] * (s.stage_n - 1))))
    def spawn(s, lvl, farm=False, near=None):
        occ = s.occupied(); edge = [t for t in TILES if hd(t, (0, 0)) == R and t not in occ and t not in s.tiles]
        if near:                                                   # 보스 졸개: 보스 옆 빈 칸
            edge = [t for t in TILES if hd(t, near) == 1 and t not in occ and t not in s.tiles] or edge
        if not edge: return
        t = s.R.choice(edge); bounty = s.cfg["bounty0"] + s.cfg["bountyk"] * lvl
        if farm: bounty = max(1, round(bounty * s.cfg["farm_bounty"]))
        s.enemies.append({"id": s.uid, "q": t[0], "r": t[1], "hp": (14 + 8 * lvl) * s.cfg["ehp"], "max": (14 + 8 * lvl) * s.cfg["ehp"], "atk": (3 + 2 * lvl) * s.cfg["eatk"], "lvl": lvl, "bounty": bounty, "stun": 0, "weak": 0, "burn": 0}); s.uid += 1
        return s.enemies[-1]
    def spawn_boss(s):
        """보스: 그 레벨 적의 체력 ×boss_hp, 공격 ×boss_atk, 처치 보상 ×boss_bounty. boss_call턴마다 졸개 2마리를 부른다. 행동 불가는 1턴만 먹는다."""
        e = s.spawn(s.lvl + 1)
        if not e: return
        e["hp"] = e["max"] = e["max"] * s.cfg["boss_hp"]; e["atk"] *= s.cfg["boss_atk"]; e["bounty"] *= s.cfg["boss_bounty"]; e["boss"] = True
        s.log(f"보스가 나타났다 (체력 {round(e['max'])})")
    # ---- play rules
    def reason(s, iid):
        o = s.inst[iid]["o"]
        if o.get("scribble"): pass
        if o["mana"] > s.mana: return "마나 부족"
        if o["role"] == "build":
            if is_plant(o):
                if sum(1 for b in s.buildings if is_plant(b["o"])) >= s.cfg["cap_p"]: return f"식물 칸 부족({s.cfg['cap_p']}칸)"
            elif sum(1 for b in s.buildings if not is_plant(b["o"])) >= s.cap_b: return f"건물 칸 부족({s.cap_b}칸)"
        if o["role"] == "summon" and not o["hostile"] and len(s.summons) >= s.cap_s: return f"소환물 칸 부족({s.cap_s}칸)"
        if o["role"] in ("build", "summon") and not o["hostile"] and o.get("bcost"):       # 재료·골드 비용(건물, 그리고 가치가 커서 비용이 붙은 소환물)
            mt, x, y = o["bcost"]
            if mt == "gold":
                if s.gold < x + y: return "골드 부족"
            elif s.res[mt] < x or s.gold < y: return "재료 또는 골드 부족"
        if o["role"] == "move" and not s.valid_tiles(iid): return "이동할 빈 칸이 없음"
        if o["role"] != "move" and s.needs_tile(o) and not s.valid_tiles(iid): return "놓을 수 있는 빈 칸이 없음"
        if manual_target(o) and not s.in_range(): return f"사거리({CAST_RANGE}칸) 안에 적이 없음"
        if sustained(o) and any(f["kind"] in ("dur", "trig", "mult", "delay") and f["o"]["name"] == o["name"] for f in s.fx): return "이미 작동 중"
        return None
    def in_range(s): return [e for e in s.enemies if hd((e["q"], e["r"]), s.pos) <= CAST_RANGE]
    def needs_target(s, o): return manual_target(o) and bool(s.in_range())
    def needs_tile(s, o): return o["role"] in ("build", "move") or (o["role"] == "summon" and not o["hostile"])
    def move_range(s, o): return o.get("mv", s.cfg["move_range"])
    def valid_tiles(s, iid):
        o = s.inst[iid]["o"]; occ = s.occupied()
        lim = s.move_range(o) if o["role"] == "move" else PLACE_RANGE          # 건물·식물·소환은 내게 인접한 칸, 이동은 구슬이 정한 칸 수
        return [t for t in TILES if 1 <= hd(t, s.pos) <= lim and t not in occ and t not in s.tiles]
    def tile_hint(s, o, t):
        """Good tiles: next to a matching resource tile (harvest) or next to a building of a different family (synergy)."""
        if o["role"] == "move": return False
        verbs = [p[0] for p in o["payload"]]
        if "harvest" in verbs:
            kind = {"wood": "tree", "ore": "ore"}.get(next((p[2] for p in o["payload"] if p[0] == "harvest"), None))
            if kind and any(s.tiles.get(n, {}).get("t") == kind and s.tiles[n]["amt"] > 0 for n in nb(t)): return True
        fam = FAM.get(o["payload"][0][0])
        return any(FAM.get(b["o"]["payload"][0][0]) not in (None, fam) for b in s.buildings if hd((b["q"], b["r"]), t) == 1)
    def play(s, hand_idx, tile=None, target=None):
        if s.phase != "play": return {"error": "플레이 중이 아닙니다"}
        s.events = []; s.pick = None; s.recent = []
        if hand_idx < 0 or hand_idx >= len(s.hand): return {"error": "손패에 없는 구슬입니다"}
        iid = s.hand[hand_idx]; it = s.inst[iid]; o = it["o"]; why = s.reason(iid)
        if why: return {"error": why}
        if s.needs_tile(o):
            if tile is None or tuple(tile) not in s.valid_tiles(iid): return {"error": "놓을 수 있는 칸을 고르세요", "need_tile": True}
        if target is not None and s.needs_target(o):     # 직접 고른 대상(없으면 가장 가까운 적)
            e = next((e for e in s.enemies if e["id"] == target), None)
            if e is None: return {"error": "대상으로 고른 적이 없습니다"}
            if hd((e["q"], e["r"]), s.pos) > CAST_RANGE: return {"error": f"사거리({CAST_RANGE}칸) 밖의 적입니다"}
            s.pick = target
        s.mana -= o["mana"]; it["uses"] += 1; s.stats["plays"] += 1; s.cur_iid = iid; s.choice = None
        s.emit("orb", tags=tags(o), name=o["name"])         # 이미 깔려 있는 반응이 먼저 반응한다(이 구슬 자신의 반응은 아래에서 깔리므로 자기 자신에겐 안 터짐)
        fam = FAM.get(o["payload"][0][0], "misc"); fm = s.cfg["fam_decay"] ** s.fam_turn[fam]; 
        if o["role"] in ("build", "summon") and not o["hostile"] and o.get("bcost"):
            mt, x, y = o["bcost"]
            if mt == "gold": s.gold -= x + y
            else: s.res[mt] -= x; s.gold -= y
        if o["role"] == "build":
            t = tuple(tile); s.buildings.append({"id": s.uid, "iid": iid, "q": t[0], "r": t[1], "hp": o["hp"], "max": o["hp"], "age": 0, "o": o}); s.uid += 1; s.log(f"건물 설치: {o['name']}")
        elif o["role"] == "move":
            s.pos = tuple(tile); s.log(f"이동: {o['name']}")
            extra = [p for p in o["payload"] if p[0] != "move"]
            if extra: s.apply(o, extra, fm)
        elif o["role"] == "summon":
            if o["hostile"]:
                for _ in range(2): s.spawn(o["lvl"], farm=True)
                s.log(f"{o['name']}: 적대 웨이브가 나타났다")
            else:
                t = tuple(tile); s.summons.append({"id": s.uid, "iid": iid, "q": t[0], "r": t[1], "hp": o["hp"], "max": o["hp"], "o": o}); s.uid += 1; s.log(f"소환: {o['name']}")
        else:
            s.fam_turn[fam] += 1
            if o["trig"] != "none": s.add_trig(iid, o)
            elif o["timing"] == "delayed": s.fx.append({"kind": "delay", "iid": iid, "o": o, "at": s.turn + o["delay"]}); s.log(f"{o['name']}: {o['delay']}턴 뒤 발동")
            elif o["life"] == "instant": s.apply(o, o["payload"], fm)
            elif o["bag_only"]: s.apply(o, o["payload"], fm); s.add_dur(iid, o, 3 if o["life"] == "turns" else 10, 3)
            else: s.apply(o, o["payload"], fm); s.add_dur(iid, o, 3 if o["life"] == "turns" else 10 ** 6, 99)
        if o["payload"][0][0] != "amplify": s.amp = 1.0
        if o.get("echo") and not o.get("copy"): s.make_echo(o)
        s.hand.remove(iid)
        if o.get("copy"): pass                                   # 메아리 사본은 쓰면 사라진다(주머니에도 버린 더미에도 안 감)
        elif o["fate"] == "used_up": s.bag.remove(iid); s.stats["exhausted"] += 1
        elif sustained(o): s.exhaust(iid)       # 지속 구슬은 쓰면 이 스테이지 동안 소멸(주머니엔 남아 다음 스테이지에 돌아옴) — 손패에 못 쓰는 채로 남지 않게
        else: s.disc.append(iid)
        s.pick = None; s.check_end_of_stage_death(); return {"ok": True}
    def offer_peek(s, o):
        """엿보기: 뽑을 더미 위 3개를 보여 주고 1개를 골라 손패로(pick). 고르지 않으면 다음 구슬을 쓰거나 턴을 끝낼 때 사라진다(나머지는 그대로 더미 위)."""
        if not s.draw: s.draw = [i for i in s.disc if i in s.bag]; s.disc = []; s.R.shuffle(s.draw)
        ids = s.draw[-3:][::-1]
        if ids: s.choice = {"kind": "peek", "ids": ids, "src": o["name"]}; s.log(f"{o['name']}: 주머니 위 {len(ids)}개 중 1개를 고르세요")
    def take_choice(s, k):       # (s.pick은 겨냥한 적 id라 이름을 따로 씀)
        c = getattr(s, "choice", None)
        if not c or s.phase != "play": return {"error": "고를 것이 없습니다"}
        if not (0 <= k < len(c["ids"])): return {"error": "없는 선택지입니다"}
        s.recent = []; i = c["ids"][k]; s.draw.remove(i); s.hand.append(i); s.choice = None; s.log(f"엿보기: {s.inst[i]['o']['name']}을(를) 손패로"); return {"ok": True}
    def make_echo(s, o):
        """메아리(사전단어): 이 구슬의 사본이 이번 턴 손패에 생긴다. 사본은 마나 −1(최소 1), 쓰면 사라지고 턴이 끝나도 사라진다."""
        c = copy.deepcopy(o); c["mana"] = max(1, o["mana"] - 1); c["echo"] = False; c["copy"] = True; c["text"] = "[사본: 이번 턴에 쓰지 않으면 사라짐] " + o["text"]
        i = s.nid; s.nid += 1; s.inst[i] = {"id": i, "o": c, "uses": 0}; s.hand.append(i); s.log(f"{o['name']}: 메아리 — 사본이 손패에 생겼다")
    def exhaust(s, iid):
        """소멸: 이 스테이지가 끝날 때까지 뽑는 순환(손패·뽑을 것·버린 것)에서 빠진다. 같은 이름의 다른 사본도 함께 소멸한다(효과가 쌓이지 않아 어차피 못 쓰고 손패만 막으므로)."""
        name = s.inst[iid]["o"]["name"]; s.exh = getattr(s, "exh", [])
        for pile in (s.hand, s.draw, s.disc):
            for i in [i for i in pile if i == iid or s.inst[i]["o"]["name"] == name]: pile.remove(i); s.exh.append(i)
        if iid not in s.exh: s.exh.append(iid)
        s.stats["exhausted_stage"] += 1; s.log(f"{name}: 소멸(이 스테이지 동안 다시 나오지 않음)")
    # ---- 사건 알림과 반응
    def trig_uses(s, o): return trig_uses(o)
    def add_trig(s, iid, o, k=1.0):
        f = next((f for f in s.fx if f["kind"] == "trig" and f["o"]["name"] == o["name"]), None)
        if f: f["uses"] = max(f["uses"], s.trig_uses(o)); s.log(f"{o['name']}: 반응 갱신")        # 같은 반응은 쌓이지 않고 횟수만 갱신
        else: s.fx.append({"kind": "trig", "iid": iid, "o": o, "cond": o["trig"], "uses": s.trig_uses(o), "tn": 0, "k": k}); s.log(f"{o['name']}: 발동 대기({COND_KO.get(o['trig'], o['trig'])})")
    def add_mult(s, iid, o, stat, pct, left):
        f = next((f for f in s.fx if f["kind"] == "mult" and f["o"]["name"] == o["name"]), None)
        if f: f["pct"] = max(f["pct"], pct); f["left"] = max(f["left"], left)
        else: s.fx.append({"kind": "mult", "iid": iid, "o": o, "stat": stat, "pct": pct, "left": left}); s.log(f"{o['name']}: {BOOST_KO.get(stat, stat)} +{pct}%")
    def mm(s, stat):    # 종류별 증폭 배율. 서로 다른 구슬의 증폭은 더해지고(+%), 합은 MULT_CAP까지
        return 1 + min(MULT_CAP, sum(f["pct"] for f in s.fx if f["kind"] == "mult" and f["stat"] == stat) / 100)
    def emit(s, kind, **info):
        """사건 알림: orb(구슬 사용, tags) · kill · harvest · hit(플레이어 피격) · lost(건물·소환물 파괴). 깔려 있는 반응(시전 구슬의 trig 효과, 건물·소환물의 trig)이 조건에 맞으면 터진다.
        반응이 만든 사건은 한 단계까지만 이어진다(무한 연쇄 방지). 반응 하나는 한 턴에 TRIG_PER_TURN회까지."""
        d = getattr(s, "_depth", 0)
        if d >= 2: return
        s._depth = d + 1
        try:
            for f in list(s.fx):
                c = f.get("cond")
                if f["kind"] != "trig" or c in ("approach", "death") or f["uses"] <= 0 or f.get("tn", 0) >= TRIG_PER_TURN or not trig_match(c, kind, info): continue
                f["tn"] = f.get("tn", 0) + 1; f["uses"] -= 1; s.stats["reactions"] += 1
                s.ev("pop", s.pos, text=f"{f['o']['name']} 발동", tone="trig"); s.apply(f["o"], f["o"]["payload"], f.get("k", 1.0))
            for grp in (s.buildings, s.summons):
                for b in list(grp):
                    o = b["o"]; c = o["trig"]
                    if c in ("none", "approach") or b not in grp or b.get("tn", 0) >= TRIG_PER_TURN or not trig_match(c, kind, info): continue
                    if is_plant(o) and b.get("age", 0) <= s.cfg["grow_turns"]: continue
                    b["tn"] = b.get("tn", 0) + 1; s.stats["reactions"] += 1; src = (b["q"], b["r"])
                    s.ev("pop", src, text=f"{o['name']} 발동", tone="trig"); s.apply(o, o["payload"], 1.0, src, b)
        finally: s._depth = d
    # ---- effects
    def add_dur(s, iid, o, left, charges):   # 같은 구슬의 지속 효과는 쌓이지 않고 시간만 갱신(쌓이면 매 턴 다시 써서 비용 대비 값어치가 폭주함)
        f = next((f for f in s.fx if f["kind"] == "dur" and f["o"]["name"] == o["name"]), None)
        if f: f["left"] = max(f["left"], left); f["charges"] = max(f["charges"], charges); s.log(f"{o['name']}: 지속 시간 갱신")
        else: s.fx.append({"kind": "dur", "iid": iid, "o": o, "left": left, "charges": charges})
    def targets(s, o, src, limit=None):
        es = sorted(s.enemies, key=lambda e: (hd((e["q"], e["r"]), src), e["id"]))
        if limit is not None: es = [e for e in es if hd((e["q"], e["r"]), src) <= limit]
        pk = getattr(s, "pick", None)
        c = next((e for e in es if e["id"] == pk), None) if pk is not None else None
        if c: es = [c] + sorted([e for e in es if e is not c], key=lambda e: (hd((e["q"], e["r"]), (c["q"], c["r"])), e["id"]))   # 직접 고른 적을 중심으로
        rng = o["rng"]
        if rng == "single": return es[:1]
        if rng == "line": return es[:2]
        if rng == "around":
            if not es: return []
            c = (es[0]["q"], es[0]["r"]); return [e for e in es if hd((e["q"], e["r"]), c) <= 1][:6]
        return es
    def apply(s, o, payload, mult=1.0, src=None, building=None):
        player = src is None; src = s.pos if player else src; at = src; lim = CAST_RANGE if player else (unit_range(building["o"]) if building else 2)      # 사거리: 플레이어 4칸, 건물 2칸, 소환물은 종류별(병사 1칸)
        for v, m, mt in payload:
            m = max(1, round(m * mult * s.amp)); uses = s.inst[building["iid"]]["uses"] if building else 0
            kd = "income" if (mt == "gold" and v in ("harvest", "grow", "create")) else KIND.get(v)         # 종류별 증폭(buff): 피해·골드 수입·채집·방어, 건물·소환물이 낸 효과는 'unit'도 곱한다
            if kd: m = max(1, round(m * s.mm(kd)))
            if not player: m = max(1, round(m * s.mm("unit")))
            if o["mod"] == "random": m = max(1, round(m * s.R.uniform(.5, 1.5)))
            if o["mod"] == "network": n = sum(1 for b in s.buildings if hd((b["q"], b["r"]), src) == 1) if building else len(s.buildings); m = round(m * (1 + .15 * n))
            if o["mod"] == "scaling":             # 쓸수록 +10%: 그 구슬을 쓴 횟수(건물·소환물은 놓은 구슬). 소수는 구슬마다 모아 두었다가 1이 되면 더한다(작은 수치도 자라게)
                it = s.inst.get(building["iid"] if building else getattr(s, "cur_iid", -1))
                if it:
                    x = m * (1 + .1 * max(0, it["uses"] - 1)) + it.get("frac", 0); m = int(x); it["frac"] = x - m
            if o["mod"] == "risky": s.hp -= max(1, m // 4)
            if building:
                fams = {FAM.get(x["o"]["payload"][0][0]) for x in s.buildings if hd((x["q"], x["r"]), src) == 1 and x is not building} - {FAM.get(o["payload"][0][0])}
                if fams: m = round(m * (1 + .2 * len(fams))); s.stats["adj_bonus"] += 1
            bonus = 1 + s.dmgb
            if v in ("damage", "drain"):
                for e in s.targets(o, src, lim):
                    b2 = bonus * (s.cfg["weak_bonus"] if (e["weak"] > 0 or e["stun"] > 0) else 1.0); e["hp"] -= m * b2; s.ev("hit", at, (e["q"], e["r"]), kind=v)
                    if v == "drain": s.hp = min(s.max_hp, s.hp + m // 2)
                s.reap()
            elif v == "guard": s.shield = min(40, s.shield + m); s.ev("pop", at, text=f"방어 +{m}", tone="up")
            elif v == "heal": s.hp = min(s.max_hp, s.hp + m); s.ev("pop", at, text=f"회복 +{m}", tone="up")
            elif v == "money": s.gold += m; s.stats["g_money"] += m; s.ev("pop", at, text=f"+{m} 🪙", tone="gain")
            elif v == "steal":
                if s.enemies: s.gold += m; s.stats["g_money"] += m; s.ev("pop", at, text=f"+{m} 🪙", tone="gain")
            elif v in ("harvest", "grow") and mt == "gold": s.gold += m; s.ev("pop", at, text=f"+{m} 🪙", tone="gain")
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
                s.res[mt or "ore"] += got; s.ev("pop", at, text=(f"+{got} {ICON.get(mt or 'ore', '')}" if got else "채집할 곳이 없다"), tone=("gain" if got else "down"))
                if got: s.emit("harvest", res=mt or "ore", n=got)
            elif v == "grow":
                k = min(m, s.land); s.land -= k; s.res[mt or "food"] += k; s.ev("pop", at, text=(f"+{k} {ICON.get(mt or 'food', '')}" if k else "경작지가 없다"), tone=("gain" if k else "down"))
                if k: s.emit("harvest", res=mt or "food", n=k)
            elif v == "process":
                n = 0
                for k in RAW:
                    t = min(m - n, s.res[k]); s.res[k] -= t; n += t
                g = int(n * s.cfg["process_ratio"]); s.gold += g; s.stats["g_process"] += g
                if g: s.ev("pop", at, text=f"가공 +{g} 🪙", tone="gain")
            elif v == "buff":       # 종류별 증폭: m = 퍼센트, mt = 키우는 것(BOOST_KINDS). 같은 구슬은 쌓이지 않고 갱신, 서로 다른 구슬끼리는 더해진다
                st_ = mt if mt in BOOST_KINDS else "dmg"; s.add_mult(building["iid"] if building else -1, o, st_, m, {"instant": 3, "turns": 4}.get(o["life"], 10 ** 6)); s.ev("pop", at, text=f"{BOOST_KO[st_]} +{m}%", tone="up")
            elif v == "burn":       # 화상: m = 중첩 수. 턴마다 중첩×BURN_DMG 피해를 주고 1중첩씩 줄어든다
                for e in s.targets(o, src, lim): e["burn"] = min(BURN_MAX, e.get("burn", 0) + m); s.ev("hit", at, (e["q"], e["r"]), kind="burn")
            elif v == "debuff":
                for e in s.targets(o, src, lim): e["weak"] = max(e["weak"], 3); s.ev("hit", at, (e["q"], e["r"]), kind="debuff")
            elif v == "control":
                n = 1 if o["life"] in ("stage", "run", "forever") else 1 + int(o["B"] // 30)
                for e in s.targets(o, src, lim): e["stun"] = max(e["stun"], 1 if e.get("boss") else n); s.ev("hit", at, (e["q"], e["r"]), kind="control")
            elif v in TURN_V and getattr(s, "ending", False):        # 턴 끝(지속·건물·소환물·자동 구슬)에 생긴 마나·뽑기·되돌림은 다음 턴 시작에 준다(그냥 두면 새 턴이 손패·마나를 덮어써서 버려짐)
                s.pending.append((v, o)); s.ev("pop", at, text={"draw": "다음 턴 +1 뽑기", "recycle": "다음 턴 되돌림", "tempo": "다음 턴 마나 +1", "energy": "다음 턴 마나 +", "peek": "다음 턴 엿보기"}[v], tone="up")
            elif v == "draw": s.drawn(draw_n(o))
            elif v == "recycle":
                if s.disc: s.hand.append(s.disc.pop(s.R.randrange(len(s.disc))))
            elif v == "trash":
                c = [i for i in s.disc if s.inst[i]["o"]["name"] != o["name"]]
                if c: w = c[0]; s.disc.remove(w); s.bag.remove(w); s.log(f"폐기: {s.inst[w]['o']['name']}")
            elif v == "tempo": s.mana += 1; s.drawn(1)                 # 신속: 마나 +1에 구슬 1개 더 — 마나 1짜리가 마나 1만 돌려주면 하는 일이 없다
            elif v == "energy": s.mana += energy_gain(o)
            elif v == "create":
                if mt == "gold": s.gold += 2
                elif mt: s.res[mt] += 2
                else: s.items += 1
            elif v == "amplify": s.amp = 2.0
            elif v == "peek": s.offer_peek(o)
    def reap(s):
        for e in [e for e in s.enemies if e["hp"] <= 0]:
            if e not in s.enemies: continue                       # 반응이 같은 reap 안에서 이미 치웠을 수 있음
            b_ = max(1, round(e["bounty"] * (s.mm("income") + s.mm("bounty") - 1)))      # 골드 수입 증폭과 처치 보상 증폭(런 지속이면 스테이지를 넘어 누적)
            s.enemies.remove(e); s.gold += b_; s.kills += 1; s.stage_kills += 1; s.stats["g_bounty"] += b_; s.log(f"적 #{e['id']} 처치: 골드 +{b_}"); s.emit("kill")
    # ---- end turn
    def end_turn(s):
        if s.phase != "play": return {"error": "플레이 중이 아닙니다"}
        s.events = []; s.pick = None; s.recent = []; s.ending = True; s.pending = []; s.choice = None
        s.amp = 1.0
        if s.items and s.hp < s.max_hp * .5: s.items -= 1; s.hp = min(s.max_hp, s.hp + 15); s.log("아이템 사용: 체력 15")
        if s.res["food"] >= 2 and s.hp < s.max_hp * .6: s.res["food"] -= 2; s.hp = min(s.max_hp, s.hp + 6); s.log("식량을 먹었다: 체력 6")
        # effects
        for f in list(s.fx):
            o = f["o"]
            if f["kind"] == "delay" and s.turn >= f["at"]:
                s.ev("pop", s.pos, text=f"{o['name']} 발동", tone="trig"); s.apply(o, o["payload"]); s.fx.remove(f); s.log(f"{o['name']} 발동")
                if o["life"] != "instant": s.add_dur(f["iid"], o, 3 if o["life"] == "turns" else 10 ** 6, 99)       # 지연된 지속 효과(사전단어 '지연'): 기다린 뒤부터 지속
            elif f["kind"] == "dur":
                if f["left"] <= 0 or f["charges"] <= 0: s.fx.remove(f); continue
                s.apply(o, o["payload"]); f["left"] -= 1; f["charges"] -= 1 if o["bag_only"] else 0
            elif f["kind"] == "mult":
                f["left"] -= 1
                if f["left"] <= 0: s.fx.remove(f); s.log(f"{o['name']}: {BOOST_KO.get(f['stat'], f['stat'])} 증폭이 끝났다")
        for i in s.bag:
            o = s.inst[i]["o"]
            if o["fate"] == "passive" and o["role"] == "cast" and o["trig"] == "none": s.apply(o, o["payload"], PASSIVE_K)
        for b in list(s.buildings):
            b["age"] += 1; o = b["o"]
            if is_plant(o) and b["age"] <= s.cfg["grow_turns"]: continue          # 식물은 자라는 동안 수확 없음
            if o["timing"] == "delayed" and b["age"] <= o["delay"]: continue
            src = (b["q"], b["r"])
            if o["trig"] == "approach":
                if any(hd((e["q"], e["r"]), src) <= 3 for e in s.enemies) and b.get("fired", 0) < 3: s.apply(o, o["payload"], 1.0, src, b); b["fired"] = b.get("fired", 0) + 1; s.ev("pop", src, text=f"{o['name']} 발동", tone="trig")
            elif o["trig"] != "none": continue                     # 반응형 건물: 사건이 일어날 때 emit 이 터뜨린다(매 턴 일하지 않음)
            else: s.apply(o, o["payload"], 1.0, src, b)
        s.estate_work()
        for u in list(s.summons):
            uo = u["o"]; us = (u["q"], u["r"]); u["age"] = u.get("age", 0) + 1
            if uo["timing"] == "delayed" and u["age"] <= uo["delay"]: continue
            if uo["trig"] == "approach":
                if any(hd((e["q"], e["r"]), us) <= 3 for e in s.enemies) and u.get("fired", 0) < 3: s.apply(uo, uo["payload"], 1.0, us, u); u["fired"] = u.get("fired", 0) + 1; s.ev("pop", us, text=f"{uo['name']} 발동", tone="trig")
            elif uo["trig"] != "none": continue
            else: s.apply(uo, uo["payload"], 1.0, us, u)
        s.tick_burn()
        s.enemy_phase()
        for f in s.fx:
            if f["kind"] == "trig" and f["cond"] == "approach" and f["uses"] > 0 and any(hd((e["q"], e["r"]), s.pos) <= 3 for e in s.enemies): s.ev("pop", s.pos, text=f"{f['o']['name']} 발동", tone="trig"); s.apply(f["o"], f["o"]["payload"], f.get("k", 1.0)); f["uses"] -= 1
        s.dmgb *= .75
        if s.hp <= 0:
            for f in s.fx:
                if f["kind"] == "trig" and f["cond"] == "death" and f["uses"] > 0 and s.hp <= 0: s.hp = 1; s.apply(f["o"], f["o"]["payload"], f.get("k", 1.0)); f["uses"] -= 1; s.log(f"{f['o']['name']}: 죽음에서 돌아왔다")
        if s.hp <= 0: s.died = True; return s.finish()
        s.next_turn(); return {"ok": True}
    def tick_burn(s):
        """화상: 중첩×BURN_DMG(×화상·피해 증폭) 피해를 주고 1중첩 줄어든다."""
        for e in list(s.enemies):
            n = e.get("burn", 0)
            if n <= 0 or e not in s.enemies: continue
            d = max(1, round(BURN_DMG * n * s.mm("burn") * (1 + s.dmgb))); e["hp"] -= d; e["burn"] = n - 1; s.stats["burn_dmg"] += d
            s.ev("pop", (e["q"], e["r"]), text=f"🔥 {d}", tone="down")
        s.reap()
    def check_end_of_stage_death(s):
        if s.hp <= 0 and s.phase == "play": s.died = True; s.finish()
    def enemy_phase(s):
        s.enemies.sort(key=lambda e: hd((e["q"], e["r"]), s.pos))
        for e in list(s.enemies):
            if e["hp"] <= 0: continue
            if e["stun"] > 0: e["stun"] -= 1; continue
            pos = (e["q"], e["r"]); atk = max(1, e["atk"] - (3 if e["weak"] > 0 else 0)); e["weak"] = max(0, e["weak"] - 1)
            tg = []
            if hd(pos, s.pos) == 1: tg.append("p")
            tg += [b for b in s.buildings if hd(pos, (b["q"], b["r"])) == 1]; tg += [u for u in s.summons if hd(pos, (u["q"], u["r"])) == 1]
            if tg:
                t = s.R.choice(tg); s.ev("hit", pos, s.pos if t == "p" else (t["q"], t["r"]), kind="enemy")
                if t == "p":
                    d = atk
                    if s.shield: a = min(s.shield, d); s.shield -= a; d -= a
                    s.hp -= d; s.stats["dmg_taken"] += atk
                    s.emit("hit")
                else:
                    t["hp"] -= atk
                    if t["hp"] <= 0: (s.buildings if t in s.buildings else s.summons).remove(t); s.log(f"{josa(t['o']['name'])} 파괴되었다"); s.emit("lost")
                continue
            occ = s.occupied(); opts = [p for p in nb(pos) if p in set(TILES) and p not in occ and p not in s.tiles]
            if opts:
                best = min(hd(p, s.pos) for p in opts)
                if best < hd(pos, s.pos) or True:
                    c = [p for p in opts if hd(p, s.pos) == best]; p = s.R.choice(c)
                    if hd(p, s.pos) < hd(pos, s.pos) or not [x for x in opts if hd(x, s.pos) < hd(pos, s.pos)]: e["q"], e["r"] = p
    # ---- finish
    def finish(s):
        """스테이지 끝. 사망·정산 실패 = 런 종료(처음부터 다시). 통과하면 정산액을 내고(잔액·자원은 이월) 건물·식물은 영지가 되고, 출구를 고른다. 마지막 스테이지를 깨면 런 클리어(남은 자원은 그때 판다)."""
        sold = 0 if s.died else s.sell_for(s.due - s.gold)
        ok = not s.died and s.gold >= s.due
        r = {"pass": bool(ok), "gold": s.gold, "due": s.due, "died": s.died, "kills": s.kills, "stage_kills": s.stage_kills, "turns": min(s.turn, s.cfg["turns"]), "src": dict(s.stats),
             "stage": s.stage_n, "stages": s.cfg["stages"], "boss": s.boss, "run_over": not ok, "clear": False}
        if ok:
            s.gold -= s.due; s.history.append({"stage": s.stage_n, "type": s.stage_type, "due": s.due, "kills": s.stage_kills, "boss": s.boss})
            s.log(f"정산 통과: {s.due} 냄 → 남은 골드 {s.gold}")
            if s.stage_n >= s.cfg["stages"]:
                sale = int(sum(s.res.values()) * SALE_RATE); s.gold += sale; s.res = dict.fromkeys(RAW, 0); s.clear = r["clear"] = True; s.phase = "over"
                s.log(f"런 클리어! 남은 자원을 팔아 골드 +{sale}")
            else:
                s.to_estates(); s.make_exits(); s.phase = "exit"
        else:
            s.phase = "over"; s.log("쓰러졌다 — 런이 끝났다" if s.died else f"정산 실패: 골드 {s.gold} / 낼 돈 {s.due} — 런이 끝났다")
        r["left"] = s.gold; r["sold"] = sold; s.result = r
        return {"ok": True, "over": True}
    def sell_for(s, need):
        """정산 때 골드가 모자라면 **모자란 만큼만** 자원을 판다(1개 = SALE_RATE 골드, 많은 자원부터; 나머지는 이월). 다 팔아도 모자라면 팔지 않는다. 판 개수를 돌려준다."""
        if need <= 0: return 0
        units = math.ceil(need / SALE_RATE - 1e-9)
        if sum(s.res.values()) < units: return 0
        sold = 0
        while sold < units:
            k = max(RAW, key=lambda x: s.res[x]); t = min(s.res[k], units - sold); s.res[k] -= t; sold += t
        g = int(round(sold * SALE_RATE, 6)); s.gold += g; s.log(f"정산: 모자란 골드를 자원 {sold}개로 채움(+{g})"); return sold
    # ---- 런: 영지·출구·다음 스테이지
    def to_estates(s):
        """클리어한 스테이지의 건물·식물은 영지가 되어 이후 스테이지마다 매 턴 생산한다(효율 감소 없음, 자원 칸 고갈 없음, 공격받지 않음). 소환물은 떠난다."""
        for b in s.buildings:
            o = b["o"]; kind = {"wood": "tree", "ore": "ore"}.get(next((p[2] for p in o["payload"] if p[0] == "harvest"), None))
            adj = bool(kind) and any(s.tiles.get(n, {}).get("t") == kind for n in nb((b["q"], b["r"])))
            if any(p[0] in ECO_V for p in o["payload"]) and o["trig"] == "none": s.estates.append({"o": o, "adj": adj, "stage": s.stage_n})
        if s.buildings: s.log(f"영지가 늘었다: {len(s.estates)}곳")
        s.buildings = []; s.summons = []
    def estate_work(s):
        """영지 생산: 경제 동사만(채집·재배·가공·돈). 옆에 자원 칸이 있던 채집 건물은 ×1.5 그대로."""
        g0 = s.gold; r0 = dict(s.res)
        for e in s.estates:
            for v, m, mt in e["o"]["payload"]:
                if v == "money": s.gold += m; s.stats["g_estate"] += m
                elif v in ("harvest", "grow"):
                    if mt == "gold": s.gold += m; s.stats["g_estate"] += m
                    else: k = mt or ("food" if v == "grow" else "ore"); s.res[k] += round(m * (1.5 if e["adj"] else 1))
                elif v == "process":
                    n = 0
                    for k in RAW: t = min(m - n, s.res[k]); s.res[k] -= t; n += t
                    g = int(n * s.cfg["process_ratio"]); s.gold += g; s.stats["g_estate"] += g
        d = {k: s.res[k] - r0[k] for k in RAW if s.res[k] != r0[k]}
        if s.estates and (s.gold != g0 or d): s.log("영지: " + ", ".join(([f"골드 +{s.gold - g0}"] if s.gold != g0 else []) + [f"{ {'wood': '나무', 'ore': '광석', 'food': '식량'}[k]} {v:+d}" for k, v in d.items()]))
    def make_exits(s):
        """출구 2~3곳(맵 가장자리). 속성(지형·보상)은 한두 개만 보인다. 다음이 보스 스테이지면 모든 출구가 보스로 간다."""
        n = s.stage_n + 1; boss = n in tuple(s.cfg["boss_at"]); k = 3 if s.R.random() < .5 else 2
        types = list(STAGE_TYPES); s.R.shuffle(types); spots = [d for d in DIRS]; s.R.shuffle(spots)
        s.exits = []
        for i in range(k):
            t = types[i % len(types)]; tier = s.R.choices([x for x, _ in REWARD_TIERS], [w for _, w in REWARD_TIERS])[0]
            show = {"type": s.R.random() < .5, "reward": s.R.random() < .5}
            if not any(show.values()): show[s.R.choice(list(show))] = True
            d = spots[i]; s.exits.append({"i": i, "q": d[0] * R, "r": d[1] * R, "type": t, "reward": tier, "boss": boss, "show": show})
        s.log(f"출구 {k}곳이 열렸다" + (" — 그 너머에 큰 그림자가 있다(보스)" if boss else ""))
    def exit_view(s, x):
        return {"i": x["i"], "q": x["q"], "r": x["r"], "boss": x["boss"], "type": x["type"] if x["show"]["type"] else None, "type_hint": STAGE_HINT[x["type"]] if x["show"]["type"] else "?",
                "reward": x["reward"] if x["show"]["reward"] else None, "reward_hint": (f"{x['reward']} 빈 구슬" if x["show"]["reward"] else "?")}
    def choose_exit(s, i):
        """출구를 골라 다음 스테이지로: 맵 새로, 체력 조금 회복, 최대 마나·적 레벨·정산액은 스테이지 번호로. 준비 단계(보상 빈 구슬 쓰기)부터 시작."""
        if s.phase != "exit": return {"error": "출구를 고를 단계가 아닙니다"}
        x = next((x for x in s.exits if x["i"] == i), None)
        if not x: return {"error": "없는 출구입니다"}
        s.reward = [x["reward"]] + (["금박"] if s.boss else []); s.stage_n += 1; s.exits = []      # 도착하면 그 출구의 빈 구슬, 보스를 깨고 떠나면 금박 하나 더
        heal = round(s.max_hp * s.cfg["rest_heal"]); s.hp = min(s.max_hp, s.hp + heal)
        s.new_map(x["type"]); s.log(f"{s.stage_n}스테이지({STAGE_TYPES[x['type']]['name']}{', 보스' if s.boss else ''}) 도착 · 휴식으로 체력 +{heal} · 정산액 {s.due}")
        return {"ok": True}
    def demolish(s, bid):
        """철거: 마나 1. 건물·식물을 치우고 재료 비용의 절반을 돌려받는다(다 쓴 채집 건물이 칸 한도를 막지 않게)."""
        if s.phase != "play": return {"error": "플레이 중이 아닙니다"}
        b = next((b for b in s.buildings if b["id"] == bid), None)
        if not b: return {"error": "그런 건물이 없습니다"}
        if s.mana < 1: return {"error": "마나 부족(철거는 마나 1)"}
        s.recent = []; s.mana -= 1; s.buildings.remove(b); bc = b["o"].get("bcost")
        if bc and bc[0] in RAW: s.res[bc[0]] += bc[1] // 2
        s.log(f"철거: {b['o']['name']}" + (f" (재료 {bc[1] // 2} 돌려받음)" if bc and bc[0] in RAW and bc[1] // 2 else "")); return {"ok": True}
    # ---- view
    def view(s):
        playable = []
        for idx, iid in enumerate(s.hand):
            o = s.inst[iid]["o"]; why = s.reason(iid) if s.phase == "play" else "대기"
            vt = s.valid_tiles(iid) if (s.needs_tile(o) and not why) else []
            playable.append({"idx": idx, "iid": iid, "o": o, "why": why, "need_tile": s.needs_tile(o), "need_target": bool(s.needs_target(o) and not why), "target_ids": [e["id"] for e in s.in_range()] if (s.needs_target(o) and not why) else [], "tiles": [list(t) for t in vt], "hint": [list(t) for t in vt if s.tile_hint(o, t)]})
        return {"phase": s.phase, "turn": s.turn, "turns": s.cfg["turns"], "stage_type": s.stage_type, "stage_name": STAGE_TYPES[s.stage_type]["name"], "hp": round(s.hp), "max_hp": s.max_hp, "shield": round(s.shield), "mana": s.mana, "max_mana": s.max_mana,
                "gold": s.gold, "res": s.res, "items": s.items, "due": s.due, "land": s.land, "bag": len(s.bag), "draw": len(s.draw), "disc": len(s.disc), "exh": len(getattr(s, "exh", [])), "dmgb": round(s.dmgb, 2),
                "tiles": [{"q": t[0], "r": t[1], **d} for t, d in s.tiles.items() if d["amt"] > 0], "hand": playable,
                "buildings": [{"id": b["id"], "q": b["q"], "r": b["r"], "hp": round(b["hp"]), "max": b["max"], "name": b["o"]["name"], "fam": FAM.get(b["o"]["payload"][0][0]), "kind": "plant" if is_plant(b["o"]) else "building", "age": b["age"], "mat": b["o"].get("mat"), "text": b["o"]["text"], "verbs": [p[0] for p in b["o"]["payload"]], "rng": b["o"]["rng"], "range": unit_range(b["o"])} for b in s.buildings],
                "summons": [{"id": u["id"], "q": u["q"], "r": u["r"], "hp": round(u["hp"]), "max": u["max"], "name": u["o"]["name"], "text": u["o"]["text"], "verbs": [p[0] for p in u["o"]["payload"]], "rng": u["o"]["rng"], "range": unit_range(u["o"])} for u in s.summons],
                "enemies": [{"id": e["id"], "q": e["q"], "r": e["r"], "hp": round(e["hp"]), "max": round(e["max"]), "lvl": e["lvl"], "boss": bool(e.get("boss")), "stun": e["stun"], "weak": e["weak"], "burn": e.get("burn", 0)} for e in s.enemies],
                "fx": [{"name": f["o"]["name"], "kind": f["kind"], "cond": f.get("cond"), "text": f["o"]["text"], "life": f["o"]["life"], "left": (f["left"] if f.get("left", 10 ** 6) < 1000 else None), "uses": f.get("uses"), "charges": f.get("charges"), "at": f.get("at")} for f in s.fx], "log": s.logs[-14:], "recent": getattr(s, "recent", [])[-20:], "result": s.result, "caps": {"b": getattr(s, "cap_b", s.cfg["cap_b"]), "s": getattr(s, "cap_s", s.cfg["cap_s"]), "p": s.cfg["cap_p"]},
                "buildings_n": sum(1 for b in s.buildings if not is_plant(b["o"])), "plants_n": sum(1 for b in s.buildings if is_plant(b["o"])), "summons_n": len(s.summons), "pos": list(s.pos), "grow_turns": s.cfg["grow_turns"], "cast_range": CAST_RANGE, "waves": [[t, s.wave_size(t)] for t in sorted(WAVES)],
                "stage_n": s.stage_n, "stages": s.cfg["stages"], "boss": s.boss, "lvl": s.lvl, "due_next": due_for(s.stage_n + 1, s.cfg) if s.stage_n < s.cfg["stages"] else None, "boss_at": list(s.cfg["boss_at"]),
                "exits": [s.exit_view(x) for x in s.exits], "estates": [{"name": e["o"]["name"], "stage": e["stage"], "text": e["o"]["text"]} for e in s.estates], "history": s.history, "reward": s.reward, "choice": ({"kind": s.choice["kind"], "src": s.choice["src"], "options": [{"k": k, "name": s.inst[i]["o"]["name"], "mana": s.inst[i]["o"]["mana"], "text": s.inst[i]["o"]["text"]} for k, i in enumerate(s.choice["ids"])]} if getattr(s, "choice", None) else None), "forecast": s.forecast()}
    def forecast(s):
        """정산 예상: 지금 골드 + 남은 턴 × 최근 3턴 평균 골드 증가(자원은 이월되므로 넣지 않음)."""
        h = s.gold_hist[-4:]; per = (h[-1] - h[0]) / (len(h) - 1) if len(h) > 1 else 0
        left = max(0, s.cfg["turns"] - s.turn + (1 if s.phase == "play" else 0))
        return {"per_turn": round(per, 1), "turns_left": left, "gold": round(s.gold + per * left), "due": s.due}

#!/usr/bin/env python3
"""텍스트 테스트 플레이 도구 — 브라우저 없이 셸 명령만으로 한 판을 돌린다(다른 모델·사람의 시험 플레이용). 규칙·Jev 호출은 게임과 똑같다(proto/core.py 를 그대로 부른다).
사용:  python3 proto/playtest.py help          (전체 명령)
상태는 proto/.playtest_state 파일에 저장돼 명령 사이에 이어진다(환경 변수 PLAYTEST_STATE 로 바꿀 수 있음, 판마다 다른 파일을 쓰면 동시에 여러 판 가능).
구슬 만들기(write)는 실제 Jev를 부른다(JEV_API_KEY 또는 클라우드 프록시 필요). 키가 없으면 write 를 건너뛰고 start 해도 시작 구슬 10개로 플레이된다."""
import os, sys, json
os.environ.setdefault("STATE_SECRET", "jev-playtest-local")        # 명령마다 프로세스가 새로 떠도 상태 서명이 맞도록 고정
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core, engine
STATE = os.environ.get("PLAYTEST_STATE") or os.path.join(HERE, ".playtest_state")
ROLE = {"cast": "시전", "build": "건물", "summon": "소환", "move": "이동"}

def load():
    try: return open(STATE, encoding="utf-8").read().strip()
    except OSError: return None
def save(blob): open(STATE, "w", encoding="utf-8").write(blob)
def call(op, **kw):
    code, v = core.handle(dict(op=op, blob=load() or "", **kw))
    if code != 200: sys.exit(f"오류({code}): {v.get('error', v)}")
    if v.get("blob"): save(v["blob"])
    return v
def cur():
    b = load()
    if not b: sys.exit("진행 중인 판이 없습니다. 먼저: python3 proto/playtest.py new [balanced|hostile|rich]")
    return core.view(core.unpack(b))

def kind(o):
    if o["role"] == "build": return "식물" if engine.is_plant(o) else "건물"
    return ROLE.get(o["role"], o["role"])
def fmt_hand(v):
    L = []
    for h in v["hand"]:
        o = h["o"]; cost = f" · 비용 {o['bcost'][0]} {o['bcost'][1]}+골드 {o['bcost'][2]}" if o.get("bcost") and o["role"] in ("build", "summon") and not o.get("hostile") else ""
        L.append(f" [{h['idx']}] {o['name']}  마나 {o['mana']}  {kind(o)}{cost}")
        L.append(f"      {o['text']}")
        if h["why"]: L.append(f"      ✗ 지금은 못 씀: {h['why']}")
        else:
            if h["need_tile"]: L.append(f"      → 놓을 칸 선택 필요: play {h['idx']} q,r   (가능: {' '.join('%d,%d' % tuple(t) for t in h['tiles'][:12])}{' …' if len(h['tiles']) > 12 else ''}; 추천: {' '.join('%d,%d' % tuple(t) for t in h['hint'][:6]) or '없음'})")
            elif h["need_target"]: L.append(f"      → 대상 선택 가능: play {h['idx']} #id   (사거리 안 적: {' '.join('#%d' % i for i in h['target_ids'])}; 생략하면 가장 가까운 적)")
            else: L.append(f"      → play {h['idx']}")
    return L or [" (손패 없음 — end 로 턴을 넘기세요)"]
def render(v):
    if v["phase"] == "setup": return render_setup(v)
    P = tuple(v["pos"]); L = []
    L.append(f"=== {min(v['turn'], v['turns'])}/{v['turns']}턴 · {v['stage_name']} 스테이지 · 골드 {v['gold']}/{v['due']} · 체력 {v['hp']}/{v['max_hp']}" + (f" · 방어 {v['shield']}" if v["shield"] else "") + f" · 마나 {v['mana']}/{v['max_mana']}")
    L.append(f"주머니 {v['bag']} · 뽑을 것 {v['draw']} · 버린 것 {v['disc']}" + (f" · 소멸 {v['exh']}" if v.get("exh") else "") + f" | 자원 나무 {v['res']['wood']} 광석 {v['res']['ore']} 식량 {v['res']['food']} · 경작지 {v['land']} · 아이템 {v['items']} | 내 위치 {P[0]},{P[1]}")
    if v["waves"]: L.append("적 웨이브: " + ", ".join(f"{t}턴 {n}마리" for t, n in v["waves"]) + " (가장자리에서 등장)")
    if v["enemies"]:
        L.append("적: " + " / ".join(f"#{e['id']}({e['q']},{e['r']}) 체력 {e['hp']}/{e['max']} 거리 {engine.hd((e['q'], e['r']), P)}" + (" 기절" if e["stun"] else "") + (" 약화" if e["weak"] else "") + (f" 화상{e['burn']}" if e.get("burn") else "") for e in v["enemies"]))
    else: L.append("적: 없음")
    mine = [f"{b['kind'] == 'plant' and '식물' or '건물'} {b['name']}#{b['id']}({b['q']},{b['r']}) 체력 {b['hp']}/{b['max']}" for b in v["buildings"]] + [f"소환 {u['name']}#{u['id']}({u['q']},{u['r']}) 체력 {u['hp']}/{u['max']}" for u in v["summons"]]
    L.append("내 건물·소환물: " + (" / ".join(mine) if mine else "없음") + f"   (칸 한도: 건물 {v['caps']['b']} 식물 {v['caps']['p']} 소환 {v['caps']['s']})")
    res = [f"{'나무' if t['t'] == 'tree' else '광석'}({t['q']},{t['r']}) {t['amt']}" for t in v["tiles"]]
    if res: L.append("자원 칸: " + " ".join(res))
    if v["fx"]: L.append("작동 중: " + " / ".join(f"{f['name']}({f['kind']}" + (f", {f['left']}턴" if f.get("left") is not None else "") + ")" for f in v["fx"]))
    if v["phase"] == "over":
        r = v["result"]; L.append(f"*** 끝: {'정산 통과' if r['pass'] else '정산 실패'} — 골드 {r['gold']}/{r['due']}, 처치 {r['kills']}, {'쓰러짐(골드·자원 몰수)' if r['died'] else '생존'}"); return "\n".join(L + ["최근 로그: " + " | ".join(v["log"][-6:])])
    L.append("손패:"); L += fmt_hand(v)
    return "\n".join(L)
def render_setup(v):
    L = [f"=== 준비 단계 · {v['stage_name']} 스테이지 · 낼 돈(정산) {v['due']} · 15턴", "가진 구슬: " + ", ".join(v["bag_names"]), "빈 구슬(이름을 쓰면 Jev가 읽어 구슬이 됨; 2개, 건너뛰어도 됨):"]
    for i, b in enumerate(v["blanks"]):
        f = b["frag"]; h = b.get("hint")
        L.append(f" ({i}) {b['tier']} 빈 구슬 · 마나 한계 {b['cap']} · 쓸 수 있는 글자 {b['max_typed']}자" + (f" · 새겨진 말 '{f['t']}'({'앞' if f['pos'] == 'pre' else '뒤'})" if f else " · 새겨진 말 없음"))
        if h: L.append(f"      {'힌트' if h['kind'] == 'hint' else '변환'}: {h['label']} — {h['text']}")
        if b["orb"]: L.append(f"      → 만든 구슬: {b['orb']['name']} · 마나 {b['orb']['mana']} · {b['orb']['text']}")
    L.append("다음: write <0|1> <이름>  (구슬 만들기) … 끝나면 start")
    return "\n".join(L)
def ascii_map(v, hand=None):
    R = 5; P = tuple(v["pos"]); occ = {}
    for t in v["tiles"]: occ[(t["q"], t["r"])] = "T" if t["t"] == "tree" else "O"
    for b in v["buildings"]: occ[(b["q"], b["r"])] = "p" if b["kind"] == "plant" else "B"
    for u in v["summons"]: occ[(u["q"], u["r"])] = "S"
    for e in v["enemies"]: occ[(e["q"], e["r"])] = "E"
    occ[P] = "@"; mark = set()
    if hand is not None:
        h = next((x for x in v["hand"] if x["idx"] == hand), None)
        if h: mark = {tuple(t) for t in h["tiles"]} | {tuple(engine_target(v, i)) for i in h["target_ids"]}
    L = ["지도(@ 나, E 적, B 건물, p 식물, S 소환물, T 나무, O 광석, * 선택한 구슬을 놓을 수 있는 칸/대상). 줄 r=…, 그 줄의 왼쪽 첫 칸이 q=…, 오른쪽으로 갈수록 q+1:"]
    for r in range(-R, R + 1):
        qs = list(range(max(-R, -R - r), min(R, R - r) + 1))
        cells = " ".join("*" if ((q, r) in mark and (q, r) not in occ) or ((q, r) in mark and occ.get((q, r)) == "E") else occ.get((q, r), ".") for q in qs)
        L.append(f"r={r:>2} (q {qs[0]:>2}~{qs[-1]:>2}) " + " " * abs(r) + cells)
    return "\n".join(L)
def engine_target(v, i):
    e = next(e for e in v["enemies"] if e["id"] == i); return (e["q"], e["r"])

def cmd_play(args):
    if not args: sys.exit("사용: play <손패번호|구슬 이름> [q,r] [#적id]")
    if args[0].lstrip("-").isdigit(): kw = {"idx": int(args[0])}
    else:                                # 이름(앞부분)으로 고르기: 구슬을 쓰면 뒤 번호가 당겨지므로 여러 개를 이어 쓸 때 편하다
        h = [x for x in cur()["hand"] if x["o"]["name"].replace(" ", "").startswith(args[0].replace(" ", ""))]
        if not h: sys.exit(f"손패에 '{args[0]}'(으)로 시작하는 구슬이 없습니다")
        kw = {"idx": (next((x for x in h if not x["why"]), h[0]))["idx"]}
    for a in args[1:]:
        if a.startswith("#"): kw["target"] = int(a[1:])
        elif "," in a: q, r = a.split(","); kw["tile"] = [int(q), int(r)]
        else: sys.exit(f"이해할 수 없는 인자: {a} (칸은 q,r  대상은 #id)")
    v = call("play", **kw); r = v.get("action", {})
    print("✗ " + r["error"] if "error" in r else "✓ 사용함" + (" — " + " | ".join(v["recent"]) if v.get("recent") else ""))
    if "error" not in r and v.get("events"): print("  일어난 일: " + " / ".join(e["text"] if e["k"] == "pop" else f"{e.get('kind', '')} 공격" for e in v["events"][:12]))
    print(render(v))
def main():
    a = sys.argv[1:]; c = a[0] if a else "help"
    if c in ("help", "-h", "--help"): print(HELP); return
    if c == "new": v = call("new", stage_type=a[1] if len(a) > 1 else "balanced"); print(render(v))
    elif c in ("state", "s"): print(render(cur()))
    elif c == "write":
        if len(a) < 3: sys.exit("사용: write <0|1> <이름>")
        v = call("write", idx=int(a[1]), text=" ".join(a[2:])); b = v["blanks"][int(a[1])]["orb"]; print(f"만든 구슬: {b['name']} · 마나 {b['mana']} · {b['text']}"); print(render(v))
    elif c == "start": print(render(call("start")))
    elif c == "play": cmd_play(a[1:])
    elif c in ("end", "e"):
        v = call("end_turn"); print("(턴 종료) " + (" | ".join(v.get("recent") or []) or "특별한 일 없음")); print(render(v))
    elif c == "preview":
        v = call("preview"); p = v.get("preview")
        print("턴을 끝내면: " + (f"골드 {p['gold']:+d}, 체력 {p['hp']:+d}, 처치 {p['kills']}, 새 적 {p['spawn']}, 잃는 건물·소환물 {sum(1 for o in p['own'] if o['lost'])}" if p else "(예측 없음)"))
    elif c == "map": print(ascii_map(cur(), int(a[1]) if len(a) > 1 else None))
    elif c == "orb":        # 판 없이 이름 → 구슬(Jev 판정 시험). 사전단어를 시험하려면: orb <쓴 이름> --hint <특성키> | --mod <변환키>
        import orbs
        rest = a[1:]; hint = mod = None
        if "--hint" in rest: i = rest.index("--hint"); hint = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
        if "--mod" in rest: i = rest.index("--mod"); mod = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
        name = " ".join(rest); o = orbs.orb_with_fragment(name, name, hint, mod, None, "ko") if (hint or mod) else orbs.orb_from_jev(name, "ko")
        print(f"{o['name']} · 마나 {o['mana']} · {kind(o)} · {o['text']}"); print("  (원자료) 동사·수치:", [(p[0], p[1], p[2]) for p in o["payload"]], "범위", o["rng"], "지속", o["life"], "반응", o["trig"], "1회용" if o["fate"] == "used_up" else "")
    elif c == "log": print("\n".join(cur()["log"][-(int(a[1]) if len(a) > 1 else 14):]))
    else: sys.exit(f"알 수 없는 명령: {c}\n\n" + HELP)
HELP = """명령 (모두 python3 proto/playtest.py <명령> …)
  new [balanced|hostile|rich]     새 판(균형·적 많음·자원 많음). 빈 구슬 2개와 힌트/사전단어를 보여 준다
  write <0|1> <이름>              빈 구슬에 이름을 써서 구슬 만들기(실제 Jev 호출, 쓴 이름만 읽힘; 글자 수 제한 있음)
  start                           준비를 끝내고 1턴 시작(구슬을 안 만들어도 됨)
  state | s                       지금 상태 다시 보기
  map [손패번호]                  ASCII 지도(손패번호를 주면 그 구슬을 놓을 수 있는 칸/대상을 * 로 표시)
  play <번호|이름> [q,r] [#적id]  손패의 구슬 사용(이름 앞부분으로도 고름: play 화염 #3). 건물·소환·이동은 칸 q,r, 즉발 공격은 대상 #id(생략하면 가장 가까운 적)
  preview                         턴을 끝내면 어떻게 되는지 예측(골드·체력·처치·새 적)
  end | e                         턴 종료(적 행동 → 다음 턴 뽑기). 15턴이 끝나면 정산
  log [n]                         최근 로그
  orb <이름> [--hint 특성|--mod 변환]  판 없이 이름만 Jev에게 읽혀 구슬 보기(사전단어 시험: --hint burn, --mod reverse 등 키는 PLAYTEST.md 부록)
규칙 요약·평가 방법은 PLAYTEST.md 참고."""
if __name__ == "__main__": main()

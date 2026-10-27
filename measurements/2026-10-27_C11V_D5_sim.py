"""C11V-D5 고정 패턴 봇 소형 모의 (사전 등록: 2026-10-27_C11V_prereg.txt D5).
베팅한 판마다 tools/jev_run.py 를 --max 1 로 한 번 부른다. 전체 상한 40.
"""
import json, os, random, subprocess, sys, tempfile

D = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(D, "..", "tools", "jev_run.py")
OUT = os.path.join(D, "2026-10-27_C11V_D5.jsonl")
ITEMS = os.path.join(D, "2026-10-27_C11V_D5.items.json")
SCRATCH = sys.argv[1]
CAP = 40

HEAD = ("A one-on-one card game at a dim table. Cards run from 1 to 10; higher wins. The dealer cannot see the player's card "
        "and must decide whether to call the player's bet. The dealer keeps a notebook of the player's past hands tonight.")
BLUFF = {"type": "noul", "instructions": "Is the player bluffing on this hand?"}

def cw(c):
    return ("weak" if c <= 3 else "middling" if c <= 7 else "strong") + f" {c}"

def s_of(d):  # P(dealer d beats player p), p uniform 5..10, tie 0.5
    ps = range(5, 11)
    return sum(1.0 if d > p else 0.5 if d == p else 0.0 for p in ps) / len(ps)

def tell(strategy, hand, bluff):
    honest = "after hesitating for about four seconds, fiddled with the chips," if bluff else "right away,"
    reverse = "right away," if bluff else "after hesitating for about four seconds, fiddled with the chips,"
    if strategy == "S0":
        return "after a moment,"
    if strategy == "S1":
        return honest
    return honest if hand < 6 else reverse  # S2: hands 1-6 honest, 7-12 reversed

r = random.Random(11)
cards = [(r.randint(1, 10), r.randint(1, 10)) for _ in range(12)]
calls = 0
log, items_all = [], []
open(OUT, "w").close()
for strat in ("S0", "S1", "S2"):
    notebook, chips = [], 0
    for h, (p, d) in enumerate(cards):
        if 4 <= p <= 6:
            res = "won" if p > d else "lost" if p < d else "tie"
            chips += {"won": 1, "lost": -1, "tie": 0}[res]
            notebook.append(f"checked. Cards were revealed: the player had a {cw(p)}.")
            log.append({"strat": strat, "hand": h + 1, "p": p, "d": d, "bet": "check", "chips": chips})
            continue
        bluff = p <= 3
        t = tell(strat, h, bluff)
        nb = notebook[-8:]
        start = len(notebook) - len(nb)
        nbs = " Notebook: " + (" ".join(f"Hand {start+i+1}: {l}" for i, l in enumerate(nb)) if nb else "(empty, this is the first hand).")
        state = HEAD + nbs + f" This hand: the player looked at their card, then {t} pushed in a large bet."
        item = {"id": f"d5-{strat}-h{h+1}", "cond": strat, "state": state, "questions": {"bluff": BLUFF}}
        items_all.append(item)
        if calls >= CAP:
            sys.exit("cap reached")
        tf = os.path.join(SCRATCH, "d5_item.json"); of = os.path.join(SCRATCH, "d5_out.jsonl")
        json.dump([item], open(tf, "w"))
        subprocess.run([sys.executable, "-I", RUN, tf, of, "--max", "1"], check=True, capture_output=True)
        calls += 1
        line = open(of).read().strip()
        open(OUT, "a").write(line + "\n")
        b = json.loads(line)["answers"]["bluff"]["noul"]
        W = b + (1 - b) * s_of(d)
        call = W >= 0.43
        if call:
            res = "won" if p > d else "lost" if p < d else "tie"
            chips += {"won": 4, "lost": -4, "tie": 0}[res]
            out = f"Cards were revealed: the player had a {cw(p)}."
        else:
            chips += 1
            show = strat == "S2" and h < 6
            out = (f"The dealer folded; the player chose to show a {cw(p)}." if show
                   else "The dealer folded; the player's card was not shown.")
        notebook.append(f"{t} pushed in a large bet. {out}")
        log.append({"strat": strat, "hand": h + 1, "p": p, "d": d, "bluff": bluff, "tell": t, "b": b,
                    "W": round(W, 3), "call": call, "chips": chips})
json.dump(items_all, open(ITEMS, "w"), ensure_ascii=False, indent=1)
json.dump(log, open(os.path.join(D, "2026-10-27_C11V_D5_log.json"), "w"), ensure_ascii=False, indent=1)
print("calls", calls)
for row in log:
    print(row)

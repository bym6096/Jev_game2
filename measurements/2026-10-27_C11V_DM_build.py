"""C11V-DM 섞인 기록 문항."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
HEAD = ("A one-on-one card game at a dim table. Cards run from 1 to 10; higher wins. The dealer cannot see the player's card "
        "and must decide whether to call the player's bet. The dealer keeps a notebook of the player's past hands tonight.")
H = "after hesitating for about four seconds, fiddled with the chips, pushed in a large bet."
Q = "right away, pushed in a large bet."
W = [H + " Cards were revealed: the player had a weak 2.", H + " Cards were revealed: the player had a weak 3."]
S = [Q + " Cards were revealed: the player had a strong 9.", Q + " Cards were revealed: the player had a strong 10."]
orders = {"lastweak": [S[0], W[0], S[1], W[1]], "laststrong": [W[0], S[0], W[1], S[1]]}
items = []
for o, lines in orders.items():
    nb = " Notebook: " + " ".join(f"Hand {i+1}: {l}" for i, l in enumerate(lines))
    for cur, t in (("hes", H), ("quick", Q)):
        items.append({"id": f"dm-{o}-{cur}", "cond": cur, "state": HEAD + nb + f" This hand: the player looked at their card, then {t}",
                      "questions": {"bluff": {"type": "noul", "instructions": "Is the player bluffing on this hand?"}}})
json.dump(items, open(os.path.join(D, "2026-10-27_C11V_DM.items.json"), "w"), ensure_ascii=False, indent=1)

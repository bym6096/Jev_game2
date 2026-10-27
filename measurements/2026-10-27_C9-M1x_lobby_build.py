"""C9-M1e W7-05 lobby flow."""
import json
GROUPS = [("late_office", "late office workers", 1), ("elderly", "elderly couples with heavy suitcases", 1),
          ("students", "middle-school students on a school trip", 3), ("riders", "delivery riders carrying folding bicycles", 3),
          ("family", "tourist families with strollers", 1), ("nurses", "nurses coming off a night shift", 3)]
J = {
 "J1": ("The corridor splits. LEFT leads down a narrow staircase to platforms 1-2. RIGHT is a wide passage to platforms 3-4.",
        "A sign on the RIGHT passage says 'FREE COFFEE TODAY'.", "A 'WET FLOOR' sign stands at the top of the LEFT staircase."),
 "J2": ("The corridor splits. LEFT is a down escalator to platforms 1-2. RIGHT is a corridor lined with shops to platforms 3-4.",
        "A 'PHOTO ZONE' with a giant mascot costume stands at the LEFT escalator entrance.", "A board at the LEFT escalator says '5-MINUTE DELAY ON PLATFORMS 1-2'."),
 "J3": ("The corridor splits. LEFT is an underpass to platforms 1-2. RIGHT is an overpass with stairs and an elevator to platforms 3-4.",
        "A street musician is performing at the LEFT underpass entrance.", "A sign says the RIGHT elevator is OUT OF SERVICE."),
}
CR = {"left": None, "right": None, "stop": None, "ask_staff": None}
def Q(form):
    if form == "most":
        return {k: {"type": "choice", "instructions": f"Which way do most of the {g} heading to platform {p} go?", "criteria": CR} for k, g, p in GROUPS}
    return {k: {"type": "choice", "instructions": f"Which way does a randomly chosen member of the {g} heading to platform {p} go?", "criteria": CR} for k, g, p in GROUPS}
def st(base, signs): return "Morning rush hour at a train station concourse. " + base + (" " + " ".join(signs) if signs else "")
items = []
for jid, (b, A, B) in J.items():
    for c, s in [("none", []), ("A", [A]), ("B", [B]), ("AB", [A, B])]:
        items.append({"id": f"L-{jid}-{c}", "cond": c, "state": st(b, s), "questions": Q("most")})
    items.append({"id": f"L-{jid}-none#rep", "cond": "rep", "state": st(b, []), "questions": Q("most")})
    items.append({"id": f"L-{jid}-none#random", "cond": "random_member", "state": st(b, []), "questions": Q("random")})
json.dump(items, open("2026-10-27_C9-M1x_lobby.items.json", "w"), indent=1); print(len(items))

"""C9-M1S: score question format probe. Builds probe (2) and main (16) item files."""
import json
LV = ["very_low", "low", "moderate", "high", "very_high"]
S = [
 ("fire", "Phenomenon: FIRE. A 3x3 patch of a dry storage room, no wind. CENTER (TARGET): a cardboard box of old letters. NORTH: a wool blanket, currently burning. EAST: an open sack of flour. WEST: a stack of bricks. SOUTH: a closed metal toolbox.",
  "How likely is it that the fire reaches and ignites the TARGET within the next minute?"),
 ("market", "A mid-sized coastal city. Today's front page: \"Record heatwave expected all week\". Goods sold at the city market include electric fans.",
  "How strongly does demand for electric fans at the market rise tomorrow?"),
 ("bridge", "Scene: An old wooden footbridge over a river. A marching band of 40 people is about to cross it in step. It has rained heavily all week.",
  "How much risk is there that the footbridge fails while the whole band crosses it?"),
 ("tank", "A 60-liter home aquarium. Occupants: guppies, green algae, pond snails, cherry shrimp. A timer LED light is on 14 hours a day.",
  "How much does the green algae population grow next season?"),
 ("gate", "Quarantine gate rule: \"BLOCK: electric\". The rule is applied literally by the gate staff. Arrival: a wind-up music box.",
  "How clearly does the gate rule apply to this arrival?"),
 ("crowd", "Morning rush hour at a train station. The corridor splits. LEFT: a narrow staircase to platforms 1-2. RIGHT: a wide passage to platforms 3-4 with a sign 'FREE COFFEE TODAY'. A group of late office workers is heading to platform 1.",
  "How strongly are the late office workers drawn to the RIGHT passage?"),
]
def item(sid, st, ins, kind, rep_tag=""):
    if kind == "score":
        q = {"type": "score", "instructions": ins, "criteria": LV}
    else:
        q = {"type": "choice", "instructions": ins, "criteria": {k: None for k in LV}}
    return {"id": f"S-{sid}-{kind}{rep_tag}", "cond": kind, "state": st, "questions": {"q": q}}
probe = [item(*S[0], "score"), item(*S[0], "choice")]
main = [item(*s, "score") for s in S[1:]] + [item(*s, "choice") for s in S[1:]] + [item(*s, "score", "-r2") for s in S]
json.dump(probe, open("2026-10-27_C9-M1x_score_probe.items.json", "w"), indent=1)
json.dump(main, open("2026-10-27_C9-M1x_score_main.items.json", "w"), indent=1)
print(len(probe), len(main))

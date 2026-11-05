"""Same 17 verbs as ONE choice question (probabilities sum to 1) instead of 17 yes/no questions."""
import sys, json
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, names
q = {"verb": {"type": "choice", "instructions": "Which effect would the thing named most naturally have when used in this game?",
              "criteria": dict(axes.PAYLOAD)}}
items = [{"id": f"ko|{n[0]}", "cond": "verbchoice",
          "state": axes.STATE.format(name=n[0]) + axes.LANG_LINE.format(lang="Korean"), "questions": q} for n in names.NAMES]
json.dump(items, open("items_verbchoice.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(items))

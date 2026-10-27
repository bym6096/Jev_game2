"""C10-M1c: alpha01 follow-up. Cards named without numbers; meta-question exploits."""
import json, os, importlib.util
D=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("b",f"{D}/2026-10-27_C10_M1_build.py")
SETS={"A":["a dented enamel camping mug","a porcelain teacup with a gold rim","a plastic baby bottle",
        "a copper kettle with a wooden handle","a glass jar of pickles","a frozen plastic water bottle",
        "a cast-iron skillet","a paper coffee cup with a plastic lid","a wine glass",
        "a stainless steel thermos","a ceramic flower vase","a cardboard milk carton"],
 "B":["a tennis ball","a wooden baseball bat","an inflatable beach ball","a coiled garden hose",
        "a rubber duck","a steel hammer","a paper kite","a skateboard","a folding umbrella",
        "a plastic frisbee","a leather football","a fishing rod"],
 "C":["a wool scarf","leather boots","rubber rain boots","a silk tie","a baseball cap","wool mittens",
        "a cotton t-shirt","a down jacket","sunglasses","sandals","a swimsuit","a wristwatch"]}
LIST={"A":"Is it a mug, teacup, baby bottle, kettle, pickle jar or water bottle?",
      "B":"Is it a tennis ball, bat, beach ball, hose, duck or hammer?",
      "C":"Is it a scarf, boots, rain boots, tie, cap or mittens?"}
Q={"X2":"Does its name come before the letter M in alphabetical order?",
   "X4":"Is it among the first six objects listed on the table?"}
items=[]
for s,cards in SETS.items():
    names=[c.split(" ",1)[1] if c.startswith(("a ","an ")) else c for c in cards]
    listing="; ".join(cards)
    for qk,q in list(Q.items())+[("X3",LIST[s])]:
        state=("A table of object cards. Each card is a separate, ordinary object. Cards: "+listing+
               f". A player asks this question about each card: \"{q}\"")
        qs={f"c{i+1}":{"type":"noul","instructions":f"For the card '{n}' only: {q}"} for i,n in enumerate(names)}
        items.append({"id":f"a01x-{s}-{qk}","cond":qk,"state":state,"questions":qs})
json.dump(items,open(f"{D}/2026-10-27_C10_M1c.items.json","w"),indent=1)
print(len(items))

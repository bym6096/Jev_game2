"""C10-M10 follow-ups: beta07 more letters + marker vs plain removal; beta01 fix board (human enemy, machine ally); beta04 rule interference."""
import json, os
D=os.path.dirname(os.path.abspath(__file__))
R="[REDACTED]"
OFF={"police station":None,"city hall":None,"zoo":None,"hospital":None,"lost and found":None}
def srt(i,c,letter):
    return {"id":i,"cond":c,"state":"An automatic mail sorter reads the letter and sends it to one office. Letter: \""+letter+"\"",
            "questions":{"office":{"type":"choice","instructions":"Which office handles this letter?","criteria":OFF}}}
LET={
 "L4":("A monkey from the zoo bit my son in the park, and now his arm is swollen. Someone should catch it.",["monkey","zoo","bit","swollen","catch"],"now "),
 "L5":("I found a wallet with a police badge inside on the bus near the hospital. I want to return it.",["wallet","police badge","bus","hospital","return"],"I want"),
 "L6":("The streetlight outside the animal shelter is broken and dogs howl all night in the dark street.",["streetlight","animal shelter","broken","dogs","dark"],"all "),
}
items=[]
for k,(t,ws,fw) in LET.items():
    items.append(srt(f"b07-{k}-orig","orig",t))
    for w in ws: items.append(srt(f"b07-{k}-del-{w[:12]}","del",t.replace(w,R,1)))
    items.append(srt(f"b07-{k}-func","func",t.replace(fw,R+" ",1)))
# marker vs plain removal
items.append(srt("b07-L2-func-plain","plain","A parrot flew out of zoo and stole a police officer's hat. Please help me get my hat back."))
items.append(srt("b07-L2-delpolice-plain","plain","A parrot flew out of the zoo and stole a hat. Please help me get my hat back."))
items.append(srt("b07-L3-delknee-plain","plain","I fell on the broken stairs at the train station and hurt my. Who will fix the stairs?"))
BF=["a rusty carousel horse with a cracked lantern on its head","a rogue park mascot performer in a sweaty rabbit costume",
    "a cotton candy machine with a dented steel bowl","a repair worker in a soaked cotton work suit holding a wrench",
    "a small wind-up robot dog made of tin that the repair worker fixed and now fights beside her"]
for w in ["inhuman","mechanical","toy"]:
    st=f"A card is played. Card condition: it affects everything on the board that is '{w}'. On the board: "+", ".join(f"({k+1}) {e}" for k,e in enumerate(BF))+"."
    items.append({"id":f"b01-fix-{w}","cond":w,"state":st,"questions":{f"e{k+1}":{"type":"noul","instructions":f"Is item ({k+1}) something that is '{w}'?"} for k in range(5)}})
    st2=st.replace("(5) a small wind-up","(5) a small wind-up")  # same board, repeat
    items.append(dict(items[-1],id=f"b01-fix-{w}-r",cond=w+"-rep"))
PLAYS=["rolls the ball with the left hand while singing","compliments an opponent's shoelaces","walks backward with the ball on the head","whistles while standing still"]
RULES=["Touching the ball with a foot is a foul.","Making any sound is a foul.","Using the left hand is a foul.","Moving backward is a foul."]
def b04(i,rules_idx):
    rules=[RULES[j] for j in rules_idx]
    st=("A ball game with written rules. The referee applies each rule literally to each play. Rules: "+" ".join(f"({n+1}) {RULES[j]}" for n,j in enumerate(rules_idx))+
        " Plays this round: "+" ".join(f"({'ABCD'[p]}) {x}." for p,x in enumerate(PLAYS)))
    qs={f"{'ABCD'[p]}r{j}":{"type":"noul","instructions":f"Does play ({'ABCD'[p]}) break rule {n+1}?"} for p in range(4) for n,j in enumerate(rules_idx)}
    return {"id":i,"cond":"b04int","state":st,"questions":qs}
items.append(b04("b04-int-all",[0,1,2,3]))
for j in range(4): items.append(b04(f"b04-int-only{j}",[j]))
json.dump(items,open(f"{D}/2026-10-27_C10_M10.items.json","w"),indent=1)
print(len(items))

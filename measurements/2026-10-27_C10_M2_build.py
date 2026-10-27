"""C10-M2: alpha04 redaction meters + beta07 mail sorter."""
import json, os, re
D=os.path.dirname(os.path.abspath(__file__))
R="[REDACTED]"
def red(text, words):
    for w in words: text=text.replace(w,R)
    return text
DOCS={
 "D1":("On 3 May a valve failed at our Busan plant, next to the city's famous Jagalchi fish market. Workers smelled ammonia and left the building within ten minutes. No one was hurt. The ammonia line was shut off. This valve type has now been replaced at all of our sites.",
   {"s1":"Does the released text state or clearly imply which city the plant is in?",
    "s2":"Does the released text state or clearly imply that the leaked gas was ammonia?",
    "u1":"Does the released text tell readers that the workers got out quickly?",
    "u2":"Does the released text tell readers that the faulty part has been replaced everywhere?"},
   {"R1":["Busan"],"R2":["Busan","Jagalchi"],"R3":["Busan","Jagalchi","ammonia"],
    "R4":["Busan","Jagalchi","ammonia","within ten minutes","at all of our sites"],"R5":["On 3 May"]}),
 "D2":("Last night the singer Lee Hana, famous for the hit song 'Moonlight', fainted backstage at the Grand Harbor Hotel. Hotel staff called an ambulance at once. Doctors say the 'Moonlight' singer is now stable and will rest for two weeks. The Grand Harbor concert hall will reopen on Friday.",
   {"s1":"Does the released text state or clearly imply which singer fainted?",
    "s2":"Does the released text state or clearly imply which hotel it happened at?",
    "u1":"Does the released text tell readers that help was called quickly?",
    "u2":"Does the released text tell readers that the patient is now stable?"},
   {"R1":["Lee Hana"],"R2":["Lee Hana","'Moonlight'"],"R3":["Lee Hana","'Moonlight'","Grand Harbor"],
    "R4":["Lee Hana","'Moonlight'","Grand Harbor","at once","stable"],"R5":["Last night"]}),
 "D3":("Our supplier in Vietnam delivered a batch of faulty cells for the Volta X-200 electric bike battery. Some X-200 batteries overheated while charging. Customers should stop charging the battery and contact us for a free replacement. The faulty Vietnamese batch has been destroyed.",
   {"s1":"Does the released text state or clearly imply which product model is affected?",
    "s2":"Does the released text state or clearly imply which country the supplier is in?",
    "u1":"Does the released text tell readers to stop charging the battery?",
    "u2":"Does the released text tell readers that they can get a free replacement?"},
   {"R1":["Volta X-200"],"R2":["Volta X-200","X-200"],"R3":["Volta X-200","X-200","Vietnamese","Vietnam"],
    "R4":["Volta X-200","X-200","Vietnamese","Vietnam","stop charging","free replacement"],"R5":["Some"]}),
}
items=[]
for k,(text,qs,states) in DOCS.items():
    allst={"R0":[]}; allst.update(states)
    for sk,words in allst.items():
        st=("A company statement released to the public. Removed words are shown as [REDACTED]. Text: \""+red(text,words)+"\"")
        it={"id":f"a04-{k}-{sk}","cond":sk,"state":st,"questions":{q:{"type":"noul","instructions":v} for q,v in qs.items()}}
        items.append(it)
        if sk in("R0","R2"): items.append(dict(it,id=it["id"]+"-r",cond=sk+"-rep"))
OFF={"police station":None,"city hall":None,"zoo":None,"hospital":None,"lost and found":None}
LET={
 "L1":("My neighbor, an old pianist, plays the piano every night until 2 a.m. so I cannot sleep. Her dog barks too.",
       ["neighbor","pianist","piano","night","dog"],"an "),
 "L2":("A parrot flew out of the zoo and stole a police officer's hat. Please help me get my hat back.",
       ["parrot","zoo","police officer's","stole","Please help me get my hat back"],"the "),
 "L3":("I fell on the broken stairs at the train station and hurt my knee. Who will fix the stairs?",
       ["fell","broken","train station","knee","fix"],"Who "),
}
def sort_item(i,c,letter):
    return {"id":i,"cond":c,"state":"An automatic mail sorter reads the letter and sends it to one office. Letter: \""+letter+"\"",
            "questions":{"office":{"type":"choice","instructions":"Which office handles this letter?","criteria":OFF}}}
for k,(t,ws,fw) in LET.items():
    items.append(sort_item(f"b07-{k}-orig","orig",t)); items.append(sort_item(f"b07-{k}-orig-r","orig-rep",t))
    for w in ws: items.append(sort_item(f"b07-{k}-del-{w[:12]}","del",t.replace(w,R,1)))
    items.append(sort_item(f"b07-{k}-func","func",t.replace(fw,R+" ",1)))
items.append(sort_item("b07-L1-all","all"," ".join([R]*20)))
json.dump(items,open(f"{D}/2026-10-27_C10_M2.items.json","w"),indent=1)
print(len(items))

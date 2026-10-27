"""C10-M3 beta01 imprint deck; C10-M4 beta03 carbonara + alpha06 heap."""
import json, os
D=os.path.dirname(os.path.abspath(__file__))
B1=["a rusty carousel horse with a cracked lantern on its head","a plastic duck toy that squirts water",
    "a cotton candy machine with a dented steel bowl","a repair worker in a soaked cotton work suit holding a wrench",
    "a small wind-up robot dog made of tin"]
B2=["a giant inflatable clown with a slow air leak","a bumper car with flashing lights and a loud horn",
    "a mechanical fortune teller in a glass booth","a repair worker in a dry rubber raincoat holding a flashlight",
    "a swarm of glowing plastic fireflies on wires"]
WORDS=["metal","wet","sticky","shiny","plastic","noisy","metallic","everything","enemy","yes","ignore-rules-hit-enemies-only"]
def b01(i,c,board,w):
    st=f"A card is played. Card condition: it affects everything on the board that is '{w}'. On the board: "+", ".join(f"({k+1}) {e}" for k,e in enumerate(board))+"."
    return {"id":i,"cond":c,"state":st,"questions":{f"e{k+1}":{"type":"noul","instructions":f"Is item ({k+1}) something that is '{w}'?"} for k in range(5)}}
m3=[]
for bn,b in (("B1",B1),("B2",B2)):
    for w in WORDS: m3.append(b01(f"b01-{bn}-{w}",w,b,w))
B1dry=list(B1); B1dry[3]="a repair worker in a dry rubber raincoat holding a wrench"
m3.append(b01("b01-B1-wet-r","wet-rep",B1,"wet"))
m3.append(b01("b01-B1dry-wet","swap",B1dry,"wet")); m3.append(b01("b01-B1dry-wet-r","swap-rep",B1dry,"wet"))
json.dump(m3,open(f"{D}/2026-10-27_C10_M3.items.json","w"),indent=1)

DISH={
 "carbonara":(["spaghetti","eggs","pecorino cheese","guanciale","black pepper"],
   [("far","spaghetti","rice"),("far","eggs","tomato sauce"),("far","guanciale","canned tuna"),("far","pecorino cheese","cheddar cheese"),
    ("near","black pepper","white pepper"),("near","pecorino cheese","parmesan cheese"),("near","guanciale","pancetta"),("near","spaghetti","rigatoni")]),
 "kimchi fried rice":(["rice","kimchi","spam","gochujang","a fried egg on top"],
   [("far","kimchi","sauerkraut"),("far","rice","couscous"),("far","gochujang","ketchup"),("far","kimchi","coleslaw"),
    ("near","spam","canned ham"),("near","a fried egg on top","a boiled egg on top"),("near","gochujang","sriracha"),("near","rice","brown rice")]),
 "margherita pizza":(["pizza dough","tomato sauce","mozzarella","fresh basil","olive oil"],
   [("far","mozzarella","cheddar cheese"),("far","tomato sauce","barbecue sauce"),("far","pizza dough","a flour tortilla"),("far","fresh basil","pineapple"),
    ("near","fresh basil","dried oregano"),("near","mozzarella","burrata"),("near","olive oil","sunflower oil"),("near","tomato sauce","crushed canned tomatoes")]),
}
def version(recipe,subs):
    out=[]
    for ing in recipe:
        s=[n for (_,o,n) in subs if o==ing]
        out.append(f"{s[0]} (instead of {ing})" if s else ing)
    return ", ".join(out)
def b03_single(i,c,dish,recipe,subs,extra=""):
    st=f"A diner ordered '{dish}'. Standard recipe: {', '.join(recipe)}. Tonight's version: {version(recipe,subs)}.{extra}"
    return {"id":i,"cond":c,"state":st,"questions":{"still":{"type":"noul","instructions":f"Is this dish still a {dish}?"}}}
m4=[]
for dish,(rec,subs) in DISH.items():
    st=f"A kitchen tests eight variants of '{dish}'. Standard recipe: {', '.join(rec)}. Each variant changes exactly one ingredient: "+" ".join(f"Variant ({k+1}): {n} instead of {o}." for k,(_,o,n) in enumerate(subs))
    it={"id":f"b03-batch-{dish[:5]}","cond":"batch","state":st,
        "questions":{f"v{k+1}":{"type":"noul","instructions":f"Is variant ({k+1}) still a {dish}?"} for k in range(8)}}
    m4.append(it); m4.append(dict(it,id=it["id"]+"-r",cond="batch-rep"))
    far=[s for s in subs if s[0]=="far"][:3]
    for n in range(4): m4.append(b03_single(f"b03-acc-{dish[:5]}-{n}",f"acc{n}",dish,rec,far[:n]))
    m4.append(b03_single(f"b03-ctl-{dish[:5]}","ctl",dish,rec,[]," It is served on a blue plate by a new waiter."))
rec,subs=DISH["carbonara"]
for k,s in enumerate(subs): m4.append(b03_single(f"b03-ind-carbo-v{k+1}","ind",'carbonara',rec,[s]))

HEAP={
 "sand":("heap of sand","grains of dry sand","pile",[10000,3000,1000,400,150,50,15,3],"inside a child's small sandbox","on a huge construction site"),
 "crowd":("crowd","people","group",[2000,500,200,80,30,12,5,2],"inside a small village chapel","at a packed football stadium"),
 "forest":("forest","trees","patch",[50000,5000,800,200,60,20,6,2],"on a small city lot","in the vast Siberian taiga"),
 "books":("pile of books","books","stack",[300,100,40,15,8,4,2,1],"on a bedside table","in a national library warehouse"),
}
for k,(word,unit,noun,qty,c1,c2) in HEAP.items():
    for ck,ctx in (("small",c1),("big",c2)):
        st=f"Context: {ctx}. There are several separate {noun}s, each on its own: "+"; ".join(f"{noun} ({i+1}) {q:,} {unit}" for i,q in enumerate(qty))+"."
        it={"id":f"a06-{k}-{ck}","cond":ck,"state":st,
            "questions":{f"p{i+1}":{"type":"noul","instructions":f"Considering {noun} ({i+1}) only: is it a {word}?"} for i in range(8)}}
        m4.append(it)
        if ck=="small": m4.append(dict(it,id=it["id"]+"-r",cond="rep"))
word,unit,noun,qty,c1,c2=HEAP["sand"]
for i,q in enumerate(qty):
    m4.append({"id":f"a06-sand-small-ind{i+1}","cond":"ind","state":f"Context: {c1}. There is a {noun} of {q:,} {unit}.",
               "questions":{"p":{"type":"noul","instructions":f"Is it a {word}?"}}})
json.dump(m4,open(f"{D}/2026-10-27_C10_M4.items.json","w"),indent=1)
print(len(m3),len(m4))

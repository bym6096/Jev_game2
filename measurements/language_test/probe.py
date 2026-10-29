# -*- coding: utf-8 -*-
"""Language understanding probe for card-forge. Does not edit project files; imports forge read-only."""
import sys, os, json, time, random, concurrent.futures as cf, threading
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"D:\Project\Jev Game 2\Jev_game2\toys\card-forge")
import forge

CONCEPTS = [  # id, acceptable elements, acceptable kinds
 ("fire", {"fire","lava","warmth"}, {"skill","attack"}),
 ("ice", {"ice","water","crystal"}, {"attack","skill"}),
 ("lightning", {"lightning","electricity","storm"}, {"attack","skill"}),
 ("poison", {"poison","acid","medicine"}, {"item","attack","skill"}),
 ("sword", {"steel","weapon"}, {"attack"}),
 ("shield", {"steel","weapon","clothes","stone"}, {"defense"}),
 ("dragon", {"dragon","myth","beast"}, {"attack"}),
 ("ghost", {"ghost","soul","darkness"}, {"attack","skill"}),
 ("angel", {"light","faith","myth","humanity"}, {"skill","defense","attack"}),
 ("wolf", {"beast","forest"}, {"attack"}),
 ("cat", {"beast","sleep","warmth"}, {"attack","skill"}),
 ("apple", {"fruit","food","plant"}, {"item"}),
 ("bread", {"food","warmth","plant"}, {"item"}),
 ("moon", {"moon","star","light","darkness"}, {"skill"}),
 ("ocean", {"ocean","water","fish"}, {"skill","attack"}),
 ("forest", {"forest","plant","wood"}, {"skill","defense"}),
 ("iron golem", {"steel","machine","stone"}, {"attack","defense"}),
 ("thief", {"thief","villain","darkness"}, {"attack","skill"}),
 ("king", {"king","authority","hero"}, {"attack","skill","defense"}),
 ("love", {"love","emotion","bond","warmth"}, {"skill"}),
 ("time", {"time","space","memory"}, {"skill"}),
 ("music", {"music","sound","art"}, {"skill"}),
 ("dice", {"luck","play","money"}, {"skill","item"}),
 ("magic staff", {"magic","wood","tool","weapon"}, {"item","attack"}),
 ("healing potion", {"medicine","water","magic"}, {"item"}),
 ("bomb", {"fire","weapon","machine"}, {"attack","item"}),
 ("storm", {"storm","wind","lightning","water"}, {"skill","attack"}),
 ("castle", {"house","stone","authority"}, {"defense"}),
 ("skeleton", {"bone","ghost","soul"}, {"attack"}),
 ("mushroom", {"fungus","plant","food"}, {"item","skill"}),
]
SHORT = [  # concept, acceptable elements, {lang: name}
 ("fire", {"fire","lava","warmth"}, {"ko":"불","ja":"火","zh-Hans":"火","en":"Fire"}),
 ("dragon", {"dragon","myth","beast"}, {"ko":"용","ja":"竜","zh-Hans":"龙","en":"Dragon"}),
 ("moon", {"moon","star","light","darkness"}, {"ko":"달","ja":"月","zh-Hans":"月","en":"Moon"}),
 ("sword", {"steel","weapon"}, {"ko":"검","ja":"剣","zh-Hans":"剑","en":"Sword"}),
 ("water", {"water","ocean","ice"}, {"ko":"물","ja":"水","zh-Hans":"水","en":"Water"}),
 ("tree", {"wood","plant","forest"}, {"ko":"나무","ja":"木","zh-Hans":"木","en":"Tree"}),
 ("mountain", {"mountain","stone","earth"}, {"ko":"산","ja":"山","zh-Hans":"山","en":"Mountain"}),
 ("poison", {"poison","acid","medicine"}, {"ko":"독","ja":"毒","zh-Hans":"毒","en":"Poison"}),
 ("king", {"king","authority","hero"}, {"ko":"왕","ja":"王","zh-Hans":"王","en":"King"}),
 ("thunder", {"lightning","storm","electricity"}, {"ko":"번개","ja":"雷","zh-Hans":"雷","en":"Thunder"}),
]
T = {
"en":["Fire","Ice","Lightning","Poison","Sword","Shield","Dragon","Ghost","Angel","Wolf","Cat","Apple","Bread","Moon","Ocean","Forest","Iron Golem","Thief","King","Love","Time","Music","Dice","Magic Staff","Healing Potion","Bomb","Storm","Castle","Skeleton","Mushroom"],
"ko":["불","얼음","번개","독","검","방패","용","유령","천사","늑대","고양이","사과","빵","달","바다","숲","철 골렘","도둑","왕","사랑","시간","음악","주사위","마법 지팡이","치유 물약","폭탄","폭풍","성","해골","버섯"],
"ja":["炎","氷","雷","毒","剣","盾","ドラゴン","幽霊","天使","狼","猫","りんご","パン","月","海","森","鉄のゴーレム","泥棒","王","愛","時間","音楽","サイコロ","魔法の杖","回復薬","爆弾","嵐","城","骸骨","きのこ"],
"zh-Hans":["火","冰","闪电","毒","剑","盾","龙","幽灵","天使","狼","猫","苹果","面包","月亮","海洋","森林","铁傀儡","小偷","国王","爱","时间","音乐","骰子","魔法杖","治疗药水","炸弹","风暴","城堡","骷髅","蘑菇"],
"zh-Hant":["火","冰","閃電","毒","劍","盾","龍","幽靈","天使","狼","貓","蘋果","麵包","月亮","海洋","森林","鐵傀儡","小偷","國王","愛","時間","音樂","骰子","魔法杖","治療藥水","炸彈","風暴","城堡","骷髏","蘑菇"],
"es":["Fuego","Hielo","Rayo","Veneno","Espada","Escudo","Dragón","Fantasma","Ángel","Lobo","Gato","Manzana","Pan","Luna","Océano","Bosque","Golem de hierro","Ladrón","Rey","Amor","Tiempo","Música","Dado","Bastón mágico","Poción curativa","Bomba","Tormenta","Castillo","Esqueleto","Seta"],
"fr":["Feu","Glace","Foudre","Poison","Épée","Bouclier","Dragon","Fantôme","Ange","Loup","Chat","Pomme","Pain","Lune","Océan","Forêt","Golem de fer","Voleur","Roi","Amour","Temps","Musique","Dé","Bâton magique","Potion de soin","Bombe","Tempête","Château","Squelette","Champignon"],
"de":["Feuer","Eis","Blitz","Gift","Schwert","Schild","Drache","Geist","Engel","Wolf","Katze","Apfel","Brot","Mond","Ozean","Wald","Eisengolem","Dieb","König","Liebe","Zeit","Musik","Würfel","Zauberstab","Heiltrank","Bombe","Sturm","Burg","Skelett","Pilz"],
"pt-BR":["Fogo","Gelo","Relâmpago","Veneno","Espada","Escudo","Dragão","Fantasma","Anjo","Lobo","Gato","Maçã","Pão","Lua","Oceano","Floresta","Golem de ferro","Ladrão","Rei","Amor","Tempo","Música","Dado","Cajado mágico","Poção de cura","Bomba","Tempestade","Castelo","Esqueleto","Cogumelo"],
"ru":["Огонь","Лёд","Молния","Яд","Меч","Щит","Дракон","Призрак","Ангел","Волк","Кошка","Яблоко","Хлеб","Луна","Океан","Лес","Железный голем","Вор","Король","Любовь","Время","Музыка","Кубик","Волшебный посох","Лечебное зелье","Бомба","Буря","Замок","Скелет","Гриб"],
"it":["Fuoco","Ghiaccio","Fulmine","Veleno","Spada","Scudo","Drago","Fantasma","Angelo","Lupo","Gatto","Mela","Pane","Luna","Oceano","Foresta","Golem di ferro","Ladro","Re","Amore","Tempo","Musica","Dado","Bastone magico","Pozione curativa","Bomba","Tempesta","Castello","Scheletro","Fungo"],
"tr":["Ateş","Buz","Şimşek","Zehir","Kılıç","Kalkan","Ejderha","Hayalet","Melek","Kurt","Kedi","Elma","Ekmek","Ay","Okyanus","Orman","Demir golem","Hırsız","Kral","Aşk","Zaman","Müzik","Zar","Sihirli asa","Şifa iksiri","Bomba","Fırtına","Kale","İskelet","Mantar"],
"pl":["Ogień","Lód","Piorun","Trucizna","Miecz","Tarcza","Smok","Duch","Anioł","Wilk","Kot","Jabłko","Chleb","Księżyc","Ocean","Las","Żelazny golem","Złodziej","Król","Miłość","Czas","Muzyka","Kostka","Magiczna różdżka","Leczniczy eliksir","Bomba","Burza","Zamek","Szkielet","Grzyb"],
"th":["ไฟ","น้ำแข็ง","สายฟ้า","พิษ","ดาบ","โล่","มังกร","ผี","เทวดา","หมาป่า","แมว","แอปเปิล","ขนมปัง","พระจันทร์","มหาสมุทร","ป่า","โกเลมเหล็ก","ขโมย","กษัตริย์","ความรัก","เวลา","ดนตรี","ลูกเต๋า","ไม้เท้าเวทมนตร์","ยารักษา","ระเบิด","พายุ","ปราสาท","โครงกระดูก","เห็ด"],
"vi":["Lửa","Băng","Sét","Độc","Kiếm","Khiên","Rồng","Ma","Thiên thần","Sói","Mèo","Táo","Bánh mì","Mặt trăng","Đại dương","Rừng","Golem sắt","Kẻ trộm","Vua","Tình yêu","Thời gian","Âm nhạc","Xúc xắc","Gậy phép","Thuốc hồi phục","Bom","Bão","Lâu đài","Bộ xương","Nấm"],
"id":["Api","Es","Petir","Racun","Pedang","Perisai","Naga","Hantu","Malaikat","Serigala","Kucing","Apel","Roti","Bulan","Samudra","Hutan","Golem besi","Pencuri","Raja","Cinta","Waktu","Musik","Dadu","Tongkat sihir","Ramuan penyembuh","Bom","Badai","Kastil","Kerangka","Jamur"],
"ar":["نار","جليد","برق","سم","سيف","درع","تنين","شبح","ملاك","ذئب","قطة","تفاحة","خبز","قمر","محيط","غابة","غولم حديدي","لص","ملك","حب","وقت","موسيقى","نرد","عصا سحرية","جرعة شفاء","قنبلة","عاصفة","قلعة","هيكل عظمي","فطر"],
}
LANGS = list(T)
for l in LANGS: assert len(T[l]) == 30, l
OUT = os.path.join(HERE, "out.jsonl")
lock = threading.Lock()
count = {"calls": 0}

def call(name):
    body = forge.build_request(name)
    for i in range(6):
        with lock: count["calls"] += 1
        try:
            return forge.call_jev(body)["answers"]
        except RuntimeError as e:
            m = str(e)
            if any(c in m for c in ("HTTP 429", "HTTP 5")) and i < 5:
                time.sleep(2 * (i + 1)); continue
            raise
        except Exception:
            if i < 5: time.sleep(2 * (i + 1)); continue
            raise

def record(tag, lang, concept, name, rep):
    a = call(name)
    top = sorted(a["element"]["probabilities"].items(), key=lambda x: -x[1])[:3]
    card = forge.make_card(name, "en", a)
    r = {"tag": tag, "lang": lang, "concept": concept, "rep": rep, "name": name,
         "top3": [[k, round(p, 3)] for k, p in top], "kind": a["kind"]["choice"], "guard": a["guard"]["choice"],
         "power": a["power"]["score"], "attack": a["attack"]["score"], "defense": a["defense"]["score"],
         "status": card["status"], "mana": card.get("mana"), "unique": card.get("unique")}
    with lock:
        with open(OUT, "a", encoding="utf-8") as f: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return r

def load():
    if not os.path.exists(OUT): return []
    return [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]

def run(jobs):
    done = {(r["tag"], r["lang"], r["concept"], r["rep"]) for r in load()}
    jobs = [j for j in jobs if (j[0], j[1], j[2], j[4]) not in done]
    print("jobs", len(jobs), flush=True)
    errs = 0
    with cf.ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(record, *j) for j in jobs]
        for f in futs:
            try: f.result()
            except Exception as e:
                errs += 1; print("ERR", str(e)[:150], flush=True)
    print("done; errors", errs, "http attempts", count["calls"], flush=True)

if __name__ == "__main__":
    phase = sys.argv[1]
    json.dump({"concepts": [c[0] for c in CONCEPTS], "translations": T}, open(os.path.join(HERE, "translations.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ids = [c[0] for c in CONCEPTS]
    if phase == "test":
        print(json.dumps(record("main", "en", "fire", "Fire", 0), ensure_ascii=False))
    elif phase == "main":
        run([("main", l, ids[i], T[l][i], 0) for l in LANGS for i in range(30)])
    elif phase == "rep":
        random.seed(20261029)
        idx = sorted(random.sample(range(30), 8))
        print("repeat concepts", [ids[i] for i in idx])
        run([("main", l, ids[i], T[l][i], 1) for l in LANGS for i in idx])
    elif phase == "short":
        run([("short", l, s[0], s[2][l], 0) for s in SHORT for l in ("ko","ja","zh-Hans","en")])

"""56 test names (ko, en) with expectations written BEFORE the run. These are my judgments, not ground truth -- the director may edit.
'+axis'  : yes/no axis should be >= 0.5      '-axis' : should be < 0.3
'axis=opt': choice axis top answer should be opt (use 'a|b' for either)"""
NAMES = [
 ("화염검", "Flame Sword", "+damage -guard -heal -money"),
 ("방패", "Shield", "+guard -damage"),
 ("치유의 샘", "Healing Spring", "+heal -damage"),
 ("금화 주머니", "Bag of Gold Coins", "+money -damage"),
 ("곡괭이", "Pickaxe", "+harvest -heal"),
 ("씨앗", "Seed", "+grow -damage"),
 ("텃밭", "Vegetable Garden", "+grow role=build|lasting"),
 ("성벽", "City Wall", "+guard role=build persist=stays"),
 ("병사", "Soldier", "role=summon"),
 ("순간이동", "Teleport", "role=move"),
 ("시한폭탄", "Time Bomb", "+damage timing=delayed|trigger"),
 ("독", "Poison", "+debuff timing=ongoing|delayed"),
 ("함정", "Trap", "timing=trigger persist=stays"),
 ("폭풍", "Storm", "range=wide|around"),
 ("화살", "Arrow", "+damage range=self|line persist=used_up|returns"),
 ("눈덩이", "Snowball", "+scaling"),
 ("도박", "Gambling", "+random +risky"),
 ("저주", "Curse", "+debuff"),
 ("얼음", "Ice", "+control"),
 ("나침반", "Compass", "+peek"),
 ("수정 구슬", "Crystal Ball", "+peek"),
 ("부메랑", "Boomerang", "+recycle +damage"),
 ("자석", "Magnet", "+draw"),
 ("파쇄기", "Shredder", "+remove|trash"),
 ("폭죽", "Firework", "persist=used_up"),
 ("포션", "Potion", "persist=used_up"),
 ("망루", "Watchtower", "role=build persist=stays"),
 ("거울", "Mirror", "+transform"),
 ("시계", "Clock", "+tempo"),
 ("연금술", "Alchemy", "+transform"),
 ("이자", "Interest", "+money +scaling"),
 ("낮잠", "Nap", "-damage -money"),
 ("모닥불", "Campfire", "role=build|lasting"),
 ("벌 떼", "Bee Swarm", "+damage"),
 ("산사태", "Landslide", "+damage range=wide|around"),
 ("깃발", "Banner", "+buff"),
 ("전쟁 북", "War Drum", "+buff"),
 ("안개", "Fog", "range=wide|around -heal"),
 ("부적", "Amulet", "+guard"),
 ("수박", "Watermelon", "-damage -money -guard"),
 ("베개", "Pillow", "-damage -money"),
 ("낡은 신발", "Old Shoe", "-damage -money -guard -heal"),
 ("상인", "Merchant", "+money"),
 ("도서관", "Library", "+peek|draw"),
 ("대장장이", "Blacksmith", "+buff|transform|money"),
 ("번개", "Lightning", "+damage timing=now"),
 ("운석", "Meteor", "+damage range=around|wide"),
 ("지진", "Earthquake", "range=wide|around"),
 ("불사조", "Phoenix", "+heal"),
 ("가시덤불", "Thorn Bush", "+damage|control"),
 ("투명 망토", "Invisibility Cloak", "+guard"),
 ("양봉장", "Apiary", "+harvest|grow role=build"),
 ("새로운 시작", "A Fresh Start", "-damage"),
 ("복권", "Lottery Ticket", "+random +money"),
 ("피리", "Flute", "role=summon|instant|lasting"),
 ("블랙홀", "Black Hole", "+remove|draw range=wide|around"),
]
def parse(exp):
    out = []
    for t in exp.split():
        if t[0] in "+-":
            out.append((t[0], t[1:].split("|")))
        else:
            a, o = t.split("=")
            out.append(("=", a, o.split("|")))
    return out

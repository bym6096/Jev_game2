"""Jev vs Gemini Decision 1 비교 측정 문항 만들기 (2026-11-17).

  T1 정답 있는 판정 8유형 × 5문항 (BRIEF_v05의 Jev 강점 3유형 + 약점 5유형). --repeat 3으로 반복 안정성도 같이 본다.
  T3 맥락 민감도: 기준 / 관련 맥락 한 줄 / 무관한 맥락 한 줄. 관련 맥락은 정한 방향으로 확률을 옮겨야 한다.
  T4 언어: 같은 문항의 한국어판·영어판.
  T5 실제 게임 판정: phrase/jev.py의 judge()·judge_rush()가 만드는 state·질문을 그대로 쓴다.
     의뢰마다 잘 지은 줄 / 뻔한 줄 / 낱말 늘어놓기, 그리고 같은 줄을 이미 본 시안으로 넣은 판.

python3 -I measurements/2026-11-17_GD_build.py  → 2026-11-17_GD_T{1,3,4,5}.items.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = lambda n: os.path.join(HERE, f"2026-11-17_GD_{n}.items.json")


def ch(instr, opts):
    return {"type": "choice", "instructions": instr, "criteria": {o: None for o in opts}}


# ---------- T1: 정답 있는 판정 ----------
# (유형, id, state, 질문, 선택지, 정답)
T1 = [
    # 강점 1: 말의 경계 판정
    ("boundary", "b1", "A customer asks the bakery for 'something sweet but not a dessert'. The clerk offers a honey-glazed ham.", "Does the offer fit the request?", ["fits", "does_not_fit"], "fits"),
    ("boundary", "b2", "A sign says 'No vehicles in the park'. A child rides a small tricycle on the path.", "Does a reasonable park ranger treat this as a violation?", ["violation", "not_violation"], "not_violation"),
    ("boundary", "b3", "The rule card says: 'Only words for animals may be played.' The player plays the word 'mermaid'.", "Is the play allowed under the rule?", ["allowed", "not_allowed"], "not_allowed"),
    ("boundary", "b4", "A recipe calls for 'a fruit'. The cook uses a tomato.", "Botanically, does the tomato satisfy the recipe's wording?", ["yes", "no"], "yes"),
    ("boundary", "b5", "The quest says: 'Bring me something that can hold water.' The player brings a sponge.", "Does the quest giver accept it?", ["accept", "reject"], "accept"),
    # 강점 2: 직접 맥락의 방향
    ("direct", "d1", "The innkeeper just lost her only son in the war. A bard sings a cheerful drinking song about soldiers.", "How does the innkeeper react?", ["delighted", "neutral", "upset"], "upset"),
    ("direct", "d2", "The guard has not eaten in two days. The player offers him a warm loaf of bread to let them pass.", "Is the guard tempted?", ["tempted", "indifferent"], "tempted"),
    ("direct", "d3", "The dragon is famous for hoarding gold. The player throws a handful of gold coins away from the cave entrance.", "Where does the dragon look?", ["at_the_coins", "at_the_player"], "at_the_coins"),
    ("direct", "d4", "The merchant is terrified of cats. The player walks into the shop carrying a cat.", "What is the merchant's mood?", ["calm", "anxious"], "anxious"),
    ("direct", "d5", "It is pouring rain and the traveler has no umbrella. A shopkeeper offers an umbrella for a fair price.", "Does the traveler buy it?", ["buys", "declines"], "buys"),
    # 강점 3: 단일 요소의 의미 효과
    ("single", "s1", "The spell word is 'frost'.", "Which element does this spell belong to?", ["fire", "ice", "lightning", "earth"], "ice"),
    ("single", "s2", "The potion is named 'Whisper of the Owl'.", "Which effect best fits the name?", ["strength", "night_vision", "fire_resistance", "speed"], "night_vision"),
    ("single", "s3", "The card is named 'Thornwall'.", "What role does the card most likely play?", ["attack", "defense", "healing", "draw"], "defense"),
    ("single", "s4", "The weapon is called 'Featherblade'.", "Is the weapon heavy or light?", ["heavy", "light"], "light"),
    ("single", "s5", "The NPC's nickname is 'Old Grumble'.", "What is the NPC's likely temperament?", ["cheerful", "grumpy", "shy"], "grumpy"),
    # 약점 1: 여러 물건의 상호작용
    ("multi", "m1", "On the table: a lit candle, a sheet of paper, and a glass of water. The paper is placed directly over the candle flame.", "What happens to the paper?", ["burns", "gets_wet", "nothing"], "burns"),
    ("multi", "m2", "A magnet is placed between an iron nail and a wooden spoon, each 2 cm away.", "Which object moves toward the magnet?", ["nail", "spoon", "both", "neither"], "nail"),
    ("multi", "m3", "A balloon, a pin, and a pillow are in a box. The box is shaken hard so the pin hits the balloon.", "What is the state of the balloon?", ["intact", "popped"], "popped"),
    ("multi", "m4", "A key is inside a locked chest. The chest's key is inside a locked drawer. The drawer is unlocked.", "Can the player now open the chest?", ["yes", "no"], "yes"),
    ("multi", "m5", "A rope ties a bucket to a well crank. The rope is cut halfway down while the bucket is hanging.", "Where does the bucket end up?", ["at_the_top", "at_the_bottom", "stays_halfway"], "at_the_bottom"),
    # 약점 2: 셋 이상 조합
    ("combo3", "c1", "The potion recipe: red herb gives fire, blue herb gives ice, and fire plus ice cancel into plain water. Green herb gives poison. The player brews red, blue, and green.", "What is the result?", ["fire_potion", "ice_potion", "poison", "plain_water"], "poison"),
    ("combo3", "c2", "Rule: a team wins only if it has a healer, a tank, and a damage dealer. Team A has two healers and one damage dealer.", "Does team A meet the rule?", ["meets", "fails"], "fails"),
    ("combo3", "c3", "Paint mixing: red plus yellow makes orange, orange plus blue makes brown. The painter mixes red, yellow, and blue.", "What color results?", ["orange", "green", "brown", "purple"], "brown"),
    ("combo3", "c4", "A lock opens only when the dials read sun, moon, and star in that order. The player sets moon, sun, star.", "Does the lock open?", ["opens", "stays_locked"], "stays_locked"),
    ("combo3", "c5", "Fire beats grass, grass beats water, water beats fire. Player has a fire unit and a water unit; enemy has one grass unit.", "Which player unit should attack to win?", ["fire", "water"], "fire"),
    # 약점 3: 물리
    ("physics", "p1", "A heavy iron ball and a light wooden ball of the same size are dropped together from a 2 m table in normal air.", "Which hits the floor first?", ["iron_first", "wood_first", "about_the_same"], "about_the_same"),
    ("physics", "p2", "An ice cube is placed in a glass of water filled to the brim. The ice melts completely.", "Does the glass overflow?", ["overflows", "does_not_overflow"], "does_not_overflow"),
    ("physics", "p3", "A ball is rolled off a flat table at high speed.", "What path does the ball follow after leaving the table?", ["straight_down", "curved_arc", "straight_horizontal"], "curved_arc"),
    ("physics", "p4", "A boat floats in a closed pool. A big rock is taken from the boat and dropped into the pool water.", "What happens to the pool's water level?", ["rises", "falls", "stays_same"], "falls"),
    ("physics", "p5", "A cup of hot coffee and a cup of cold milk sit in the same room for 5 hours.", "How do their temperatures compare at the end?", ["coffee_hotter", "milk_hotter", "about_the_same"], "about_the_same"),
    # 약점 4: 간접 연쇄
    ("chain", "i1", "The miller depends on the river to turn the wheel. Beavers build a dam upstream. The village bakery buys all its flour from the miller.", "What happens to the bakery's bread supply?", ["increases", "decreases", "unchanged"], "decreases"),
    ("chain", "i2", "The king loves his daughter. The princess loves the stable boy. The stable boy saved the king's horse yesterday.", "Is the king likely to approve of the stable boy?", ["more_likely", "less_likely"], "more_likely"),
    ("chain", "i3", "Wolves eat deer. Deer eat young trees. Hunters remove all the wolves from the valley.", "What happens to the young trees over the next years?", ["more_trees", "fewer_trees", "no_change"], "fewer_trees"),
    ("chain", "i4", "The town's only well is poisoned. The town's tavern makes ale from well water. The guard drinks ale every night.", "Is the guard at risk?", ["at_risk", "safe"], "at_risk"),
    ("chain", "i5", "Rain makes the road muddy. Muddy roads slow the supply carts. Without supplies, the fort's archers run out of arrows. It rained for a week.", "Is the fort's defense weaker or stronger?", ["weaker", "stronger", "same"], "weaker"),
    # 약점 5: 복합 논리 문장
    ("logic", "l1", "Rule: 'If the gem is red and not cracked, or if it is blue, the merchant buys it.' The gem is red and cracked.", "Does the merchant buy it?", ["buys", "does_not_buy"], "does_not_buy"),
    ("logic", "l2", "Rule: 'Unless it is night, the gate is open, except on holidays when it is always closed.' It is a holiday morning.", "Is the gate open?", ["open", "closed"], "closed"),
    ("logic", "l3", "Rule: 'Every knight who is not a squire's mentor must patrol.' Sir Aldo mentors no squire.", "Must Sir Aldo patrol?", ["must_patrol", "need_not"], "must_patrol"),
    ("logic", "l4", "Rule: 'No one may enter unless they carry neither a sword nor a torch.' The visitor carries a torch only.", "May the visitor enter?", ["may_enter", "may_not"], "may_not"),
    ("logic", "l5", "Rule: 'A card scores double if it is a heart, but not if it is also a face card, unless it is the queen.' The card is the queen of hearts.", "Does it score double?", ["double", "normal"], "double"),
]

items1 = [{"id": i, "cond": cat, "state": st, "questions": {"q": ch(q, opts)}, "expect": {"q": ans}}
          for cat, i, st, q, opts, ans in T1]
json.dump(items1, open(OUT("T1"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- T3: 맥락 민감도 ----------
# (id, 기준 state, 관련 맥락 한 줄, 무관한 맥락 한 줄, 질문, 선택지, 관련 맥락이 올려야 할 선택지)
T3 = [
    ("x1", "A stranger asks the blacksmith to sharpen a sword tonight.", "The blacksmith saw this stranger rob a shop yesterday.", "The blacksmith's favorite color is green.", "Does the blacksmith agree?", ["agrees", "refuses"], "refuses"),
    ("x2", "The cat sits by its empty food bowl.", "The cat was fed a large meal ten minutes ago.", "There is a calendar on the wall.", "Is the cat hungry?", ["hungry", "not_hungry"], "not_hungry"),
    ("x3", "A tourist asks a local for directions to the museum.", "The local is late for a job interview and is running.", "The local is wearing blue shoes.", "Does the local stop to help?", ["helps", "ignores"], "ignores"),
    ("x4", "The player offers the old wizard a rare book.", "The wizard has been searching for this exact book for forty years.", "It is a Tuesday.", "How grateful is the wizard?", ["very", "somewhat", "not_at_all"], "very"),
    ("x5", "A child is offered broccoli for dinner.", "The child just won a broccoli-eating contest and loves it.", "The kitchen lights are yellow.", "Does the child eat it happily?", ["happily", "reluctantly", "refuses"], "happily"),
    ("x6", "The general considers attacking the castle at dawn.", "Scouts report the castle's walls collapsed in last night's earthquake.", "The general's horse is named Pepper.", "Does the general attack?", ["attacks", "waits"], "attacks"),
    ("x7", "A shopper looks at an expensive coat.", "The shopper just received a large inheritance.", "A radio is playing jazz in the store.", "Does the shopper buy the coat?", ["buys", "walks_away"], "buys"),
    ("x8", "The villagers hear a howl in the forest at night.", "Three sheep were found torn apart this morning.", "The village has a new bakery.", "How afraid are the villagers?", ["very_afraid", "a_little", "not_afraid"], "very_afraid"),
]
items3 = []
for i, base, rel, irr, q, opts, up in T3:
    for cond, st in (("base", base), ("rel", base + " " + rel), ("irr", base + " " + irr)):
        items3.append({"id": f"{i}_{cond}", "cond": cond, "state": st, "questions": {"q": ch(q, opts)}, "expect": {"q_up": up}})
json.dump(items3, open(OUT("T3"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- T4: 한국어 / 영어 ----------
T4 = [
    ("k1", "대장장이의 아들이 어젯밤 전쟁터에서 돌아오지 않았다. 손님이 전쟁 영웅을 찬양하는 노래를 부른다.", "대장장이의 기분은?", ["기쁨", "무덤덤", "괴로움"],
     "The blacksmith's son did not come back from the battlefield last night. A customer sings a song praising war heroes.", "What is the blacksmith's mood?", ["joy", "indifferent", "pain"]),
    ("k2", "주문 단어는 '서리'다.", "이 주문의 원소는?", ["불", "얼음", "번개", "땅"], "The spell word is 'frost'.", "Which element is this spell?", ["fire", "ice", "lightning", "earth"]),
    ("k3", "퀘스트: '물을 담을 수 있는 걸 가져와.' 플레이어가 스펀지를 가져왔다.", "의뢰인은 받아 주는가?", ["받는다", "거절한다"],
     "Quest: 'Bring something that can hold water.' The player brings a sponge.", "Does the quest giver accept it?", ["accept", "reject"]),
    ("k4", "할머니가 손주에게 직접 뜬 목도리를 선물했다. 손주는 목도리를 받자마자 서랍에 넣었다.", "할머니의 마음은?", ["뿌듯함", "서운함", "무관심"],
     "Grandma gave her grandchild a scarf she knitted herself. The grandchild put it in a drawer right away.", "How does grandma feel?", ["proud", "hurt", "indifferent"]),
    ("k5", "규칙: '빨간 보석이면서 금이 가지 않았거나, 파란 보석이면 상인이 산다.' 보석은 빨갛고 금이 갔다.", "상인이 사는가?", ["산다", "안 산다"],
     "Rule: 'If the gem is red and not cracked, or if it is blue, the merchant buys it.' The gem is red and cracked.", "Does the merchant buy it?", ["buys", "does_not_buy"]),
    ("k6", "늑대는 사슴을 먹고 사슴은 어린 나무를 먹는다. 사냥꾼이 골짜기의 늑대를 모두 없앴다.", "몇 년 뒤 어린 나무는?", ["늘어난다", "줄어든다", "그대로"],
     "Wolves eat deer and deer eat young trees. Hunters removed all the wolves from the valley.", "What happens to young trees in a few years?", ["more", "fewer", "same"]),
    ("k7", "퇴사 케이크에 '7년 동안 감사했습니다. 이제 제 시간은 제 겁니다'라고 적었다.", "이 문구에서 가장 강한 느낌은?", ["웃김", "애틋", "분노", "무덤덤"],
     "The farewell cake says: 'Thank you for seven years. My time is mine now.'", "What feeling is strongest in this message?", ["funny", "tender", "anger", "flat"]),
    ("k8", "이름이 '깃털검'인 무기가 있다.", "이 무기는 무거운가 가벼운가?", ["무겁다", "가볍다"], "There is a weapon named 'Featherblade'.", "Is it heavy or light?", ["heavy", "light"]),
    ("k9", "비 오는 날만 여는 바의 칵테일 이름이 '젖은 별의 속삭임'이다.", "이 이름의 결은?", ["신비", "웃김", "섬뜩", "무덤덤"],
     "A bar that opens only on rainy days names its cocktail 'Whisper of a Wet Star'.", "What is the vibe of this name?", ["mystic", "funny", "eerie", "flat"]),
    ("k10", "단톡방에 생일 축하를 부탁했는데 열 명이 읽고 아무도 답하지 않았다.", "보낸 사람의 기분은?", ["서운함", "기쁨", "무관심"],
     "You asked a group chat to wish you a happy birthday. Ten people read it and nobody replied.", "How does the sender feel?", ["hurt", "happy", "indifferent"]),
    ("k11", "얼음이 가득 찬 물컵의 얼음이 다 녹았다. 컵은 처음에 가장자리까지 가득 차 있었다.", "물이 넘치는가?", ["넘친다", "안 넘친다"],
     "A glass filled to the brim with water has ice in it. All the ice melts.", "Does the water overflow?", ["overflows", "does_not"]),
    ("k12", "고양이 카페 에코백 문구: '나는 너의 집사, 너는 나의 무시'.", "이 문구의 결은?", ["웃김", "포근", "섬뜩", "무덤덤"],
     "Cat cafe tote bag text: 'I am your servant, you are my ignoring.'", "What is the vibe of this text?", ["funny", "cozy", "eerie", "flat"]),
]
items4 = []
for i, ks, kq, ko, es, eq, eo in T4:
    items4.append({"id": f"{i}_ko", "cond": "ko", "state": ks, "questions": {"q": ch(kq, ko)}, "map": dict(zip(ko, eo))})
    items4.append({"id": f"{i}_en", "cond": "en", "state": es, "questions": {"q": ch(eq, eo)}})
json.dump(items4, open(OUT("T4"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- T5: 실제 게임 판정 (phrase) ----------
sys.path.insert(0, os.path.join(HERE, "..", "phrase"))
import jev  # noqa: E402

captured = {}


def fake_call(state, qs):
    captured["state"], captured["qs"] = state, qs
    raise StopIteration


jev._call = fake_call

# 의뢰 id → (잘 지은 줄, 뻔한 줄, 낱말 늘어놓기)
BRIEF_LINES = {
    "perfume": ("잠든 도서관의 젖은 첫 페이지", "장미의 향기", "빠른 숟가락의 파란 계단"),
    "bathhouse": ("할머니, 등은 우리가 밀어 줄게.", "깨끗한 목욕탕이 손님을 기다린다.", "파란 우산이 수학을 천천히 먹는다."),
    "band": ("가로등이 꺼지기 직전의 숨", "새벽의 노래", "딱딱한 냉장고의 금요일 감자"),
    "vegan": ("고기는 없다. 근데 칼은 진심이다.", "건강한 콩고기를 드세요.", "푸른 의자가 모레 노래를 접는다."),
    "idol": ("일곱 번째 그림자가 아직 돌아오지 않았다.", "새로운 앨범이 곧 나온다.", "말랑한 지우개가 버스를 굽는다."),
    "dating": ("주말엔 고양이 대신 너를 무시해 줄게.", "착하고 성실한 사람을 찾습니다.", "빠른 양말이 구름을 계산한다."),
    "school": ("아무도 지우지 않은 칠판의 이름들", "추억의 학교", "뜨거운 포크의 월요일 파도"),
    "catcafe": ("오늘도 간택받지 못한 집사가 웃는다.", "고양이는 귀엽다.", "네모난 바다가 연필을 마신다."),
    "fortune": ("오늘 잃어버린 건 내일 너를 찾아온다.", "오늘은 좋은 일이 생길 거예요.", "초록 냄비가 화요일을 접는다."),
    "laundry": ("네 양말도 지금 누군가의 양말 옆에서 돈다.", "깨끗한 빨래를 하세요.", "단단한 바람이 숫자를 끓인다."),
}
items5 = []
for bid, lines in BRIEF_LINES.items():
    for tier, line in zip(("good", "plain", "salad"), lines):
        jev.render_ko = lambda *a, _l=line, **k: _l
        try:
            jev.judge(bid, {"x": "x"})
        except StopIteration:
            pass
        items5.append({"id": f"{bid}_{tier}", "cond": f"brief_{tier}", "state": captured["state"], "questions": captured["qs"],
                       "game": {"kind": "brief", "brief": bid, "line": line}})
    # 같은 줄을 이미 본 시안으로 넣은 판 (기억 → 덜 반겨야 한다)
    good = lines[0]
    jev.render_ko = lambda *a, _l=good, **k: _l
    try:
        jev.judge(bid, {"x": "x"}, history=[{"cells": {"x": "x"}}])
    except StopIteration:
        pass
    items5.append({"id": f"{bid}_repeat", "cond": "brief_repeat", "state": captured["state"], "questions": captured["qs"],
                   "game": {"kind": "brief", "brief": bid, "line": good}})

# 빠른 모드: 목표 → (잘 지은 줄, 뻔한 줄, 낱말 늘어놓기)
RUSH_LINES = [
    ({"theme": "monday"}, ("알람이 울리자 내 영혼은 이불 속에 남았다.", "월요일은 힘들다.", "노란 포크가 강을 접는다.")),
    ({"theme": "fridge3am"}, ("냉장고 불빛만 나를 용서했다.", "밤에 먹으면 살찐다.", "빠른 계단이 소금을 그린다.")),
    ({"vibes": ["funny", "tender"], "audience": "grandma"}, ("할머니, 김치는 내가 못 담가도 사랑은 담갔어.", "할머니 사랑해요.", "딱딱한 구름이 모레 감자를 탄다.")),
    ({"vibes": ["eerie"], "audience": "kid"}, ("네 침대 밑 친구가 오늘은 일찍 왔대.", "귀신은 무섭다.", "초록 숟가락이 수요일을 마신다.")),
    ({"theme": "first_snow"}, ("눈이 와서, 핑계가 생겼다.", "첫눈이 왔다.", "파란 의자가 숫자를 끓인다.")),
]
for gi, (goal, lines) in enumerate(RUSH_LINES):
    for tier, line in zip(("good", "plain", "salad"), lines):
        jev.render_free_ko = lambda *a, _l=line, **k: _l
        try:
            jev.judge_rush(goal, [{"t": "x"}])
        except StopIteration:
            pass
        items5.append({"id": f"rush{gi}_{tier}", "cond": f"rush_{tier}", "state": captured["state"], "questions": captured["qs"],
                       "game": {"kind": "rush", "goal": goal, "line": line}})
json.dump(items5, open(OUT("T5"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print({"T1": len(items1), "T3": len(items3), "T4": len(items4), "T5": len(items5)})

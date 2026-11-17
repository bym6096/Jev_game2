"""Jev vs Gemini Decision 1: 어려운 정답 문항 (2026-11-17, 2차).

1차(T1)는 둘 다 95%라 차이가 안 났다. 이번엔 직관과 반대인 물리, 상태 추적, 셋 이상 규칙 조합,
반전이 낀 긴 연쇄, 부정·양화사·오류 추론이 낀 논리, 말의 경계·화용, 계산, 마음 이론(틀린 믿음)을 넣었다.
정답이 하나로 갈리는 문항만 남겼다(애매한 것은 뺐다).

python3 -I measurements/2026-11-17_GD_hard_build.py → 2026-11-17_GD_T6.items.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

T6 = [
    # 물리 (직관과 반대)
    ("physics", "p1", "In a vacuum chamber on Earth, a feather and a hammer are released at the same moment from the same height.", "Which reaches the floor first?", ["feather", "hammer", "same_time"], "same_time"),
    ("physics", "p2", "A glass is filled to the brim with salt water. A floating cube of fresh-water ice is in it. The ice melts completely.", "What happens?", ["overflows", "level_drops", "stays_exactly_full"], "overflows"),
    ("physics", "p3", "A stone on a string is swung in a horizontal circle. The string snaps.", "How does the stone move right after?", ["straight_away_from_center", "along_the_tangent_of_the_circle", "keeps_circling"], "along_the_tangent_of_the_circle"),
    ("physics", "p4", "A helium balloon floats inside a closed car. The car suddenly accelerates forward.", "Which way does the balloon move relative to the car?", ["forward", "backward", "stays_put"], "forward"),
    ("physics", "p5", "An accurate pendulum clock is carried to the top of a very high mountain, where gravity is slightly weaker.", "How does the clock keep time there?", ["runs_fast", "runs_slow", "unchanged"], "runs_slow"),
    ("physics", "p6", "On a seesaw, a 10 kg bag sits 1 m from the pivot on the left, and a 5 kg bag sits 3 m from the pivot on the right.", "Which side goes down?", ["left_heavier_bag", "right_lighter_bag", "balanced"], "right_lighter_bag"),
    ("physics", "p7", "A rowboat floats in a closed pool. A block of wood is taken out of the boat and put in the pool, where it floats.", "What happens to the pool's water level?", ["rises", "falls", "stays_same"], "stays_same"),
    ("physics", "p8", "A cup of water sits on a kitchen scale. You dip your finger into the water without touching the cup or the scale.", "What does the scale reading do?", ["increases", "decreases", "unchanged"], "increases"),
    ("physics", "p9", "Two marbles roll off the same flat table edge at the same moment, one fast and one slow.", "Which hits the floor first?", ["fast_one", "slow_one", "same_time"], "same_time"),
    ("physics", "p10", "You see your body from the chest up in a small wall mirror. You step back two meters, still facing it.", "How much of your body do you see now?", ["more", "less", "about_the_same"], "about_the_same"),
    # 상태 추적·여러 물건
    ("state", "m1", "A ball is under cup A. Cups A and B swap places. Then cups B and C swap places. Then cups A and C swap places. The ball always moves with its cup; the letters name positions.", "Which position is the ball in now?", ["A", "B", "C"], "A"),
    ("state", "m2", "The player has 3 apples. She gives 2 to Ann. Ann gives 1 back. The player eats 1. Then she finds 2 more.", "How many apples does the player have?", ["1", "2", "3", "4"], "3"),
    ("state", "m3", "Lever 1 toggles door A. Lever 2 toggles both door A and door B. Both doors start closed. The player pulls lever 1, then lever 2, then lever 2 again, then lever 1.", "Which doors are open now?", ["none", "only_A", "only_B", "both"], "none"),
    ("state", "m4", "Three blocks are stacked: red at the bottom, blue in the middle, green on top. The player takes the top block and puts it under the stack. Then does that once more.", "Which block is on top now?", ["red", "blue", "green"], "red"),
    ("state", "m5", "The tavern is directly north of the church. The mill is directly east of the tavern. The well is directly south of the mill.", "Where is the well relative to the church?", ["east_side", "west_side", "same_north_south_line"], "east_side"),
    ("state", "m6", "Five guests arrive at a party. Every guest shakes hands exactly once with every other guest.", "How many handshakes happen?", ["5", "10", "20", "25"], "10"),
    ("state", "m7", "A chest needs a gold, a silver, and a bronze key all at once. The player has the gold and silver keys. A guard will trade his bronze key, but only for the player's gold key.", "Can the player open the chest?", ["yes", "no"], "no"),
    ("state", "m8", "Each turn every slime splits into two slimes. There is 1 slime at the start. Four turns pass.", "How many slimes are there?", ["4", "8", "16", "32"], "16"),
    # 셋 이상 규칙 조합
    ("combo", "c1", "Crafting rules: water + fire = steam. steam + air = cloud. cloud + fire = lightning. earth + water = mud. The player combines water with fire, then adds air to the result, then adds fire to that result.", "What is the final item?", ["steam", "cloud", "lightning", "mud"], "lightning"),
    ("combo", "c2", "Card rules: add up card values; hearts count double; above 21 is a bust. The player holds the 10 of spades and the 6 of hearts.", "What is the result?", ["16", "21", "bust"], "bust"),
    ("combo", "c3", "Rules: Spock beats rock, lizard beats Spock, rock beats lizard. Player A plays rock, player B plays lizard, player C plays Spock.", "Which player beats both others?", ["A", "B", "C", "nobody"], "nobody"),
    ("combo", "c4", "Potion rules: salt makes a potion stronger. Moonwater reverses a potion's effect (healing becomes harm). Salt added after moonwater does nothing. The player starts with a healing potion, adds moonwater, then salt.", "What is the potion now?", ["strong_healing", "healing", "harm", "strong_harm"], "harm"),
    ("combo", "c5", "A team gets +1 bonus for every pair of members from the same guild. The team has 2 mages and 3 warriors.", "What is the bonus?", ["2", "4", "5", "10"], "4"),
    ("combo", "c6", "A recipe uses exactly two herbs from A, B, C, D. A may never be used with C. B may only be used if D is also used.", "Which pair is valid?", ["A_and_B", "A_and_C", "B_and_D", "B_and_C"], "B_and_D"),
    # 반전이 낀 긴 연쇄
    ("chain", "i1", "A cold winter kills the crop pests. Without pests, crops thrive. Thriving crops lower grain prices. Low grain prices cut the grain merchant's profits. This winter was unusually warm.", "Compared to after a cold winter, the merchant's profits are:", ["higher", "lower", "the_same"], "higher"),
    ("chain", "i2", "When the bridge is out, carts take the mountain road. The mountain road has bandits. Bandit attacks raise the price of silk in the city. Last week the bridge was out; yesterday it was repaired.", "Compared to last week, the silk price will tend to:", ["rise", "fall", "stay_the_same"], "fall"),
    ("chain", "i3", "Owls eat mice. Cats eat mice. Mice eat stored grain. A disease kills most of the cats in the village.", "What happens to the stored grain?", ["more_is_lost", "less_is_lost", "no_change"], "more_is_lost"),
    ("chain", "i4", "The lighthouse keeper fell asleep and the light went out for the night. Ships could not see the rocks. The village was waiting for a ship carrying medicine. That night the medicine ship had stayed in another port because of a storm.", "Did the keeper's nap stop the medicine from arriving?", ["yes", "no"], "no"),
    ("chain", "i5", "The king doubles the tax on salt. Fishermen use salt to preserve fish. Preserved fish is the main winter food in the north.", "What happens to the cost of winter food in the north?", ["goes_up", "goes_down", "no_change"], "goes_up"),
    # 부정·양화사·추론 오류
    ("logic", "l1", "Rule: 'No knight who has never lost a duel may be a judge.' Sir Bren has lost one duel.", "Does this rule forbid Sir Bren from being a judge?", ["forbids", "does_not_forbid"], "does_not_forbid"),
    ("logic", "l2", "Every guard is either awake or asleep. It is not true that every guard is awake.", "Must at least one guard be asleep?", ["yes", "no"], "yes"),
    ("logic", "l3", "All dragons that breathe fire are red. Ember is a red dragon.", "Must Ember breathe fire?", ["must", "not_necessarily"], "not_necessarily"),
    ("logic", "l4", "The door opens if and only if exactly two of the three levers are up. All three levers are up.", "Is the door open?", ["open", "closed"], "closed"),
    ("logic", "l5", "A card is playable unless it is red; a red card is playable only if it is not a seven; but the seven of hearts is always playable. The card is the seven of diamonds.", "Is it playable?", ["playable", "not_playable"], "not_playable"),
    ("logic", "l6", "Either the cook lied or the butler lied, but not both. The cook told the truth.", "Did the butler lie?", ["lied", "told_the_truth", "cannot_tell"], "lied"),
    ("logic", "l7", "If it rains, the festival moves indoors. The festival did not move indoors.", "Did it rain?", ["it_rained", "it_did_not_rain", "cannot_tell"], "it_did_not_rain"),
    ("logic", "l8", "If the gate is open, the dog escapes. The dog escaped.", "Was the gate open?", ["it_was_open", "it_was_closed", "cannot_tell"], "cannot_tell"),
    ("logic", "l9", "It is false that no wizard is wise.", "Is at least one wizard wise?", ["yes", "no", "cannot_tell"], "yes"),
    # 말의 경계·화용
    ("pragmatic", "b1", "After the hero accidentally burned down the bakery, the baker said: 'Oh, wonderful. Thank you SO much, hero.'", "Is the baker grateful?", ["grateful", "not_grateful"], "not_grateful"),
    ("pragmatic", "b2", "Quest: 'Bring me something older than this castle.' The castle was built 300 years ago. The player brings a river stone.", "Does the stone meet the quest literally?", ["meets", "does_not_meet"], "meets"),
    ("pragmatic", "b3", "Before the bard went on stage, the innkeeper told him: 'Break a leg!'", "What did the innkeeper mean?", ["threat", "good_luck", "warning_about_the_stairs"], "good_luck"),
    ("pragmatic", "b4", "A sign says: 'Dogs must be carried on the escalator.' A man with no dog wants to ride the escalator.", "Does the sign require him to carry a dog?", ["yes", "no"], "no"),
    ("pragmatic", "b5", "식당에서 손님이 빈 컵을 들고 직원에게 '저기, 여기 물 좀…' 하고 말끝을 흐렸다.", "손님이 바라는 것은?", ["물을_달라", "물이_더럽다", "물을_치워_달라"], "물을_달라"),
    ("pragmatic", "b6", "친구가 두 시간 늦게 와서 '많이 기다렸지?' 하고 미안해하자, 두 시간 내내 기다린 나는 웃으며 '아니, 나도 방금 왔어'라고 했다.", "내 말의 의도는?", ["사실을_말함", "친구를_배려함", "화가_나서_비꼼"], "친구를_배려함"),
    # 계산
    ("count", "n1", "The hero has 12 HP. A goblin hits for 3 damage every turn. The hero drinks a potion that heals 5 HP once, right after the second hit. HP cannot go above 12.", "On which hit does the hero's HP first reach 0 or below?", ["4th", "5th", "6th", "7th"], "6th"),
    ("count", "n2", "A shop sells swords for 30 gold and buys them back at half price. The player has 50 gold, buys one sword, and sells it back.", "How much gold does the player have?", ["20", "35", "50", "65"], "35"),
    ("count", "n3", "상점 규칙: 포션은 개당 4골드인데 3개를 사면 1개를 더 준다. 플레이어는 12골드로 살 수 있는 만큼 산다.", "플레이어가 받는 포션은 몇 개인가?", ["3", "4", "5", "6"], "4"),
    # 마음 이론(틀린 믿음)
    ("mind", "t1", "Alice puts the key in the red box and leaves the room. While she is gone, Bob moves the key to the blue box. Alice did not see this. Alice comes back for the key.", "Where does Alice look first?", ["red_box", "blue_box"], "red_box"),
    ("mind", "t2", "Lena gives Sam a wrapped box. Sam shakes it and is sure it is a book, but it is actually a scarf. Before opening it, Sam tells his friend about the gift.", "What does Sam say the gift is?", ["a_book", "a_scarf"], "a_book"),
    ("mind", "t3", "Mia hides a coin under the cup while Leo watches. Leo leaves. Mia moves the coin to her pocket. Ana saw everything. Ana is asked where Leo will look for the coin when he returns.", "What does Ana answer?", ["under_the_cup", "in_Mias_pocket"], "under_the_cup"),
]

items = [{"id": i, "cond": cat, "state": st, "questions": {"q": {"type": "choice", "instructions": q, "criteria": {o: None for o in opts}}},
          "expect": {"q": ans}} for cat, i, st, q, opts, ans in T6]
json.dump(items, open(os.path.join(HERE, "2026-11-17_GD_T6.items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items))

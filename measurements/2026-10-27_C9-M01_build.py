"""C9-M01 item builder: latency by state length (short ~50 words / long ~400 words)
x question count (1 / 5). 2 warm-up items + 4 cells x 7, interleaved.
Each item carries a distinct 'Turn k.' line so no two requests are identical."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

SHORT = ("Persona: Mansu, 60s, the bride's uncle. Has not spoken to the groom's father Dongcheol for 20 years. "
         "Raised the bride like his own daughter. Stubborn.\n"
         "Situation: Village wedding, 5 pm. The photographer calls everyone to the yard for the group photo. "
         "Dongcheol is already in the front row.")

LONG_LINES = [
 "Persona: Mansu, 60s, the bride's uncle. Twenty years ago he lost badly to the groom's father Dongcheol at cards in the guest room, and he has not spoken to him since. He raised the bride like his own daughter after her father died at sea. He insists on pouring the wedding wine himself. He is stubborn, proud, and quick to take offense, but he cries at weddings.",
 "Setting: a village on the south coast in the 1980s. The wedding is held in the yard of the bride's house. The kitchen is run by Mansu's sister Sunja, who never lets anyone else touch the noodle pot. The errand boy Cheol carries messages between the guests and loves candy. The town photographer Mr. Oh must catch the last bus back to town and hates anyone touching his tripod.",
 "Today: at 7 am Mansu tidied the guest room and set out the card mat out of habit.",
 "Today: at 9 am he greeted guests at the gate and did not look at the city cars that brought the groom's family.",
 "Today: at 11 am, during the ceremony, he stood behind the bride and kept his eyes on the ground when Dongcheol bowed.",
 "Today: at noon Dongcheol picked up the speech manuscript Mansu had dropped, bowed, and returned it, saying 'let's let the old thing go for the children.' Mansu took it without a word.",
 "Today: at 1 pm, over the noodles, Mansu poured wine for every guest at the long table except Dongcheol, and Sunja noticed.",
 "Today: at 2 pm the bride came to the kitchen and asked Sunja whether her uncle would be in the family photo.",
 "Today: at 3 pm Mansu sat in the guest room with two old friends and a bottle, and the friends teased him about the cards.",
 "Today: at 4 pm the photographer set up his tripod in the yard and chalked marks on the ground for the front row.",
 "Today: at 4:30 pm Cheol told Mansu that Dongcheol had asked where the bride's uncle would stand.",
 "Situation: Village wedding, 5 pm. The photographer calls everyone to the yard for the group photo. Dongcheol is already standing in the front row, next to the empty chalk mark. The bride is looking toward the guest room door. The light is going, and the photographer says he can take only one picture before his bus.",
]
LONG = "\n".join(LONG_LINES)

Q1 = {"q": {"type": "choice", "instructions": "What does Mansu do at 5 pm?",
            "criteria": {"drink_in_guest_room": None, "stand_front_row_in_photo": None,
                         "stand_at_edge_of_photo": None, "go_look_for_someone": None}}}
Q5 = dict(Q1)
Q5.update({
 "mood": {"type": "choice", "instructions": "What is Mansu's main feeling right now?",
          "criteria": {"pride": None, "resentment": None, "tenderness": None, "embarrassment": None}},
 "speaks": {"type": "noul", "instructions": "Does Mansu speak to Dongcheol in the next minute?"},
 "bride": {"type": "choice", "instructions": "What does the bride do next?",
           "criteria": {"wait_quietly": None, "go_fetch_her_uncle": None, "ask_photographer_to_wait": None}},
 "gossip": {"type": "noul", "instructions": "Will the guests gossip about this photo tomorrow?"},
})

def item(i, cell, base, qs):
    return {"id": f"m01-{i:02d}", "cond": cell, "state": f"Turn {i}.\n{base}", "questions": qs}

cells = [("short_q1", SHORT, Q1), ("short_q5", SHORT, Q5), ("long_q1", LONG, Q1), ("long_q5", LONG, Q5)]
items = [item(0, "warmup", SHORT, Q1), item(1, "warmup", LONG, Q5)]
k = 2
for r in range(7):
    for name, base, qs in (cells if r % 2 == 0 else cells[::-1]):
        items.append(item(k, name, base, qs)); k += 1
json.dump(items, open(os.path.join(HERE, "2026-10-27_C9-M01.items.json"), "w"), ensure_ascii=False, indent=1)
print("short words", len(SHORT.split()), "long words", len(LONG.split()), "items", len(items))

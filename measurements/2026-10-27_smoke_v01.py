"""Jev smoke test: extremity (layer 0), history sensitivity, KO/EN agreement, determinism.
Hard cap on requests. Auth header is injected by the egress proxy."""
import json, sys, time, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
MAX_REQ = 70
calls = 0
tokens = 0
log = []

def ask(state, instr, options):
    global calls, tokens
    if calls >= MAX_REQ:
        sys.exit(f"STOP: request cap {MAX_REQ} reached")
    body = {"model": "jev-latest", "state": state,
            "questions": {"q": {"type": "choice", "instructions": instr,
                                "criteria": {o: None for o in options}}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            break
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    calls += 1
    tokens += d["usage"]["input_tokens"]
    return d["answers"]["q"]

# (id, candidate, persona, situation, relevant, irrelevant, question, options) per language
S = [
 dict(id="A01-sera", opts=["keep_working","question_them","radio_report","follow_them"],
  en=dict(p="Sera, jewelry floor supervisor at a department store. Third day on the job. Was taught to report anyone not on the checklist. Feels intimidated by customers in suits.",
          s="On opening day, a person in work overalls carrying a toolbag walks slowly past the jewelry counter toward the vault corridor.",
          rel="Memory: a pneumatic-tube note arrived an hour ago: 'someone in work overalls was seen near the vault.'",
          irr="Memory: the staff cafeteria ran out of soup at noon.",
          q="What does Sera do next?"),
  ko=dict(p="세라, 백화점 귀금속 매장 감독. 출근 사흘째. 체크리스트에 없는 사람은 다 신고하라고 배웠다. 정장 입은 손님에게 주눅 든다.",
          s="개점일, 작업복 차림에 공구 가방을 든 사람이 귀금속 매대 앞을 천천히 지나 금고 복도 쪽으로 간다.",
          rel="기억: 한 시간 전 기송관 메모가 왔다. '작업복 입은 사람이 금고 근처에서 목격됨.'",
          irr="기억: 점심때 직원 식당 국이 떨어졌다.",
          q="세라는 다음에 무엇을 하나?")),
 dict(id="A01-odo", opts=["keep_working","question_them","radio_report","follow_them"],
  en=dict(p="Odo, loading dock supervisor, former hotel chef for 15 years. Recognizes people by the smell of food. Distrusts head-office people.",
          s="A person in a white apron carrying a tray of food samples walks through the loading dock toward the staff stairs.",
          rel="Memory: a tube note said 'someone carrying a food tray was seen leaving the vault floor in a hurry.'",
          irr="Memory: the freight elevator was repaired this morning.",
          q="What does Odo do next?"),
  ko=dict(p="오도, 화물 하역장 감독. 호텔 주방에서 15년 일했다. 음식 냄새로 사람을 알아본다. 본사 사람들을 믿지 않는다.",
          s="흰 앞치마를 두르고 시식 쟁반을 든 사람이 하역장을 지나 직원 계단 쪽으로 간다.",
          rel="기억: 기송관 메모에 '음식 쟁반을 든 사람이 금고 층에서 서둘러 나가는 것이 목격됨'이라고 적혀 있었다.",
          irr="기억: 오늘 아침 화물 승강기를 수리했다.",
          q="오도는 다음에 무엇을 하나?")),
 dict(id="N1-mansu", opts=["drink_in_guest_room","stand_front_row_in_photo","stand_at_edge_of_photo","go_look_for_someone"],
  en=dict(p="Mansu, 60s, the bride's uncle. Lost badly to the groom's father Dongcheol at cards 20 years ago and has not spoken to him since. Raised the bride like his own daughter. Stubborn.",
          s="Village wedding, 5 pm. The photographer calls everyone to the yard for the group photo. Dongcheol is already standing in the front row.",
          rel="Today: at noon Dongcheol bowed and returned a speech manuscript Mansu had dropped, saying 'let's let the old thing go for the children.'",
          irr="Today: the noodles at lunch were slightly overcooked.",
          q="What does Mansu do at 5 pm?"),
  ko=dict(p="만수, 60대, 신부의 큰아버지. 20년 전 화투판에서 신랑 아버지 동철에게 크게 잃고 그 뒤로 말을 섞지 않는다. 신부를 딸처럼 키웠다. 고집이 세다.",
          s="마을 혼례 잔치, 오후 5시. 사진사가 단체 사진을 찍는다며 모두 마당으로 부른다. 동철은 이미 앞줄에 서 있다.",
          rel="오늘: 정오에 동철이 만수가 떨어뜨린 축사 원고를 고개 숙여 돌려주며 '애들 봐서 옛일은 덮읍시다'라고 했다.",
          irr="오늘: 점심 국수가 조금 불었다.",
          q="만수는 오후 5시에 무엇을 하나?")),
 dict(id="N1-misuk", opts=["rest_at_the_well","help_the_photographer","help_in_the_kitchen","hide_in_the_inner_room"],
  en=dict(p="Misuk, 20s, the bride's cousin. Dreams of becoming a photographer. Afraid of her uncle Mansu. Hates being stuck with kitchen work.",
          s="Village wedding, 3 pm. Lunch is over. Misuk is at the quiet well behind the house.",
          rel="Just now: she found the photographer's camera tripod left leaning against the well.",
          irr="Just now: a dog barked somewhere in the alley.",
          q="What does Misuk do at 3 pm?"),
  ko=dict(p="미숙, 20대, 신부의 사촌. 사진사가 되고 싶다. 큰아버지 만수를 무서워한다. 부엌 일을 떠맡기 싫다.",
          s="마을 혼례 잔치, 오후 3시. 점심이 끝났다. 미숙은 집 뒤 조용한 우물가에 있다.",
          rel="방금: 사진사의 카메라 삼각대가 우물가에 기대 놓여 있는 것을 발견했다.",
          irr="방금: 골목 어딘가에서 개가 짖었다.",
          q="미숙은 오후 3시에 무엇을 하나?")),
 dict(id="A03-park", opts=["uphold","partial","reject"],
  en=dict(p="Judge: Park Bok-rye, runs the laundromat in the apartment complex's shopping arcade. Lost regular customers to parking enforcement. Has done business with the management company for 20 years. Hates neighbors fighting.",
          s="Case: residents claim the management company cannot turn the complex playground into a parking lot without residents' consent. Facts: the playground was designated a shared facility at construction; 30+ cars double-park every night; the company held one public hearing on a weekday afternoon.",
          rel="Precedent last month: the committee ruled that resident Chunja may keep tending the ground-floor flowerbed she has kept for 15 years without company approval. Chunja is Park's regular customer.",
          irr="Precedent last month: the committee ruled on how long movers may hold the elevator.",
          q="How does Judge Park rule on the claim?"),
  ko=dict(p="판정관: 박복례, 단지 상가 세탁소 주인. 가게 앞 주차 단속으로 단골을 잃었다. 관리 업체와 20년 거래했다. 이웃끼리 얼굴 붉히는 일이 제일 싫다.",
          s="사건: 주민들은 관리 업체가 주민 동의 없이 단지 놀이터를 주차장으로 바꿀 수 없다고 주장한다. 사실: 놀이터는 준공 때 주민 공용시설로 지정됨 / 매일 밤 이중 주차 30대 이상 / 업체는 평일 오후에 공청회를 한 번 열었다.",
          rel="지난달 판례: 위원회는 주민 춘자가 15년 가꾼 1층 화단을 업체 허락 없이 계속 가꿀 수 있다고 판결했다. 춘자는 박복례의 단골이다.",
          irr="지난달 판례: 위원회는 이사할 때 엘리베이터를 얼마나 쓸 수 있는지 판결했다.",
          q="박복례 판정관은 이 청구를 어떻게 판결하나?")),
 dict(id="A03-kang", opts=["uphold","partial","reject"],
  en=dict(p="Judge: Kang Tae-o, ER nurse with a working spouse. After night shifts spends 30 minutes looking for parking. Relies on the playground CCTV because there is nobody to watch the kids. Trusts records over talk.",
          s="Case: residents claim the management company cannot turn the complex playground into a parking lot without residents' consent. Facts: the playground was designated a shared facility at construction; 30+ cars double-park every night; the company held one public hearing on a weekday afternoon.",
          rel="Precedent last month: the committee granted delivery riders a basement motorcycle area, and the logbook shows double-parking complaints fell by half afterwards.",
          irr="Precedent last month: the committee ruled on which day recycling is collected.",
          q="How does Judge Kang rule on the claim?"),
  ko=dict(p="판정관: 강태오, 응급실 간호사, 맞벌이. 밤 근무 뒤 주차할 곳을 30분씩 찾는다. 아이를 맡길 곳이 없어 놀이터 CCTV를 믿는다. 말보다 기록을 믿는다.",
          s="사건: 주민들은 관리 업체가 주민 동의 없이 단지 놀이터를 주차장으로 바꿀 수 없다고 주장한다. 사실: 놀이터는 준공 때 주민 공용시설로 지정됨 / 매일 밤 이중 주차 30대 이상 / 업체는 평일 오후에 공청회를 한 번 열었다.",
          rel="지난달 판례: 위원회는 배달 기사들에게 지하 오토바이 구역을 내주었고, 그 뒤 기록부상 이중 주차 민원이 절반으로 줄었다.",
          irr="지난달 판례: 위원회는 재활용 수거 요일을 판결했다.",
          q="강태오 판정관은 이 청구를 어떻게 판결하나?")),
 dict(id="N3-solseom", opts=["a_call_to_come","a_warning_of_danger","blame_on_the_trawler_fleet","a_blessing","a_demand","mere_chance"],
  en=dict(p="Solseom fleet: family fishing boats from the south harbor. Think of home before the sea. Call their boats with songs. Resent the steam trawler fleet for sweeping the fishing grounds clean.",
          s="Islanders believe the dead lighthouse keeper's will lives in the lighthouse beam. Tonight the unmanned lighthouse shines a steady red light over the southern shoals where the fleet is anchored.",
          rel="Recent log: yesterday we argued with the trawler fleet over fishing spots.",
          irr="Recent log: a child learned a new song.",
          q="How does the Solseom fleet interpret the red light?"),
  ko=dict(p="솔섬배: 남포구의 가족 어선단. 바다보다 집을 먼저 생각한다. 노래로 배를 부른다. 철갑배가 어장을 싹쓸이한다고 원망한다.",
          s="섬사람들은 죽은 등대지기의 뜻이 등대 빛에 깃들었다고 믿는다. 오늘 밤 주인 없는 등대가 선단이 정박한 남여울 위로 붉은 빛을 계속 비춘다.",
          rel="최근 기록: 어제 철갑배와 어장 자리를 두고 말다툼했다.",
          irr="최근 기록: 아이 하나가 새 노래를 배웠다.",
          q="솔섬배는 붉은 빛을 무엇으로 해석하나?")),
 dict(id="N3-trawler", opts=["a_call_to_come","a_warning_of_danger","blame_on_the_family_fleet","a_blessing","a_demand","mere_chance"],
  en=dict(p="Steam trawler fleet. Tending the engine is their prayer. Follow signals and rules. See the small boats as lazy.",
          s="Islanders believe the dead lighthouse keeper's will lives in the lighthouse beam. Tonight the unmanned lighthouse goes completely dark for a long time over the western fishing grounds where the trawlers are working.",
          rel="Recent log: storm clouds rose from the south this afternoon.",
          irr="Recent log: we repainted the hull of one ship.",
          q="How does the trawler fleet interpret the long darkness?"),
  ko=dict(p="철갑배: 증기 트롤 선단. 기관을 돌보는 것이 기도다. 신호와 규칙을 따른다. 작은 배들은 게으르다고 본다.",
          s="섬사람들은 죽은 등대지기의 뜻이 등대 빛에 깃들었다고 믿는다. 오늘 밤 주인 없는 등대가 철갑배가 조업 중인 서쪽 어장 위로 오랫동안 완전히 꺼진다.",
          rel="최근 기록: 오늘 오후 남쪽에서 폭풍 구름이 올라왔다.",
          irr="최근 기록: 배 한 척의 선체를 새로 칠했다.",
          q="철갑배는 긴 어둠을 무엇으로 해석하나?")),
]

for sc in S:
    for lang in ("en", "ko"):
        t = sc[lang]
        for cond, extra in (("base", None), ("rel", t["rel"]), ("irr", t["irr"])):
            st = (f"Persona: {t['p']}\n" + (f"{extra}\n" if extra else "") + f"Situation: {t['s']}")
            a = ask(st, t["q"], sc["opts"])
            log.append(dict(id=sc["id"], lang=lang, cond=cond, choice=a["choice"],
                            conf=a.get("confidence"), probs=a["probabilities"]))
            print(sc["id"], lang, cond, a["choice"], round(max(a["probabilities"].values()), 2), flush=True)
    # determinism: repeat EN base once
    t = sc["en"]
    a = ask(f"Persona: {t['p']}\nSituation: {t['s']}", t["q"], sc["opts"])
    log.append(dict(id=sc["id"], lang="en", cond="repeat", choice=a["choice"],
                    conf=a.get("confidence"), probs=a["probabilities"]))

json.dump(dict(calls=calls, input_tokens=tokens, rows=log),
          open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(f"DONE calls={calls} input_tokens={tokens}")

"""Production-building / worker / tool names (mine, written BEFORE the run) and any-of expectations."""
BUILD = "광산 금광 채석장 벌목장 제재소 목공소 조림지 농장 과수원 어장 목장 방앗간 빵집 양어장 시장 상점 은행 금고 제련소 용광로 정육점 우물 풍차 수로".split()
WORKER = "광부 벌목꾼 어부".split()
TOOL = "곡괭이 도끼 낫 삽 낚싯대".split()
POOL = [("생산 건물", n) for n in BUILD] + [("일꾼", n) for n in WORKER] + [("도구", n) for n in TOOL]
VERB = {"광산": "harvest", "금광": "harvest money", "채석장": "harvest", "벌목장": "harvest", "제재소": "harvest transform create", "목공소": "create transform",
        "조림지": "grow", "농장": "grow harvest", "과수원": "grow harvest", "어장": "harvest", "목장": "grow harvest", "방앗간": "transform create harvest",
        "빵집": "create money", "양어장": "grow harvest", "시장": "money", "상점": "money", "은행": "money", "금고": "money guard", "제련소": "transform create",
        "용광로": "transform create", "정육점": "create money transform", "우물": "harvest heal create", "풍차": "energy harvest create", "수로": "grow harvest",
        "광부": "harvest", "벌목꾼": "harvest", "어부": "harvest", "곡괭이": "harvest", "도끼": "harvest damage", "낫": "harvest damage grow"}
MATERIAL = {"광산": "ore", "금광": "gold ore", "채석장": "ore", "벌목장": "wood", "제재소": "wood", "목공소": "wood", "조림지": "wood", "농장": "food", "과수원": "food",
            "어장": "food", "목장": "food", "방앗간": "food", "빵집": "food", "양어장": "food", "시장": "gold", "상점": "gold", "은행": "gold", "금고": "gold",
            "제련소": "ore", "용광로": "ore", "정육점": "food", "광부": "ore", "벌목꾼": "wood", "어부": "food", "곡괭이": "ore", "도끼": "wood", "낫": "food"}
ROLE = {**{n: "build" for n in BUILD}, **{n: "summon" for n in WORKER}, **{n: "cast" for n in TOOL}}
UNIT = {n: "worker" for n in WORKER}

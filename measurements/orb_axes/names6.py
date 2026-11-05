"""Verb-fix test (mine, expectations BEFORE the run). 'new' = names meant to need process/drain/fishing fix; 'reg' = regression names whose v3 verb should not change."""
NEW = {
 "process": "제재소 제련소 용광로 방앗간 빵집 정육점 목공소 대장간 양조장 정미소".split(),
 "drain":   "흡혈 흡혈귀 생명흡수 마나흡수 거머리".split(),
 "fishing": "어장 어부 낚싯대 양어장".split(),
}
EXPECT = {**{n: ["process", "create"] for n in NEW["process"]},          # create is acceptable (making goods)
          **{n: ["drain"] for n in NEW["drain"]},
          **{n: ["harvest", "grow"] for n in NEW["fishing"]}}
EXPECT["흡혈"] = ["drain"]
REG = "자석 그물 갈고리 진공청소기 도서관 광산 벌목장 곡괭이 광부 농장 자원강탈 도적 쥐떼 천사 치유의 샘 화염검 즉사 상점 은행 금화 주머니 연금술 거울 현자의돌 레고블록 억까 뽁뽁이 우로보로스 윤회 데자뷔 부메랑 번개 방패".split()

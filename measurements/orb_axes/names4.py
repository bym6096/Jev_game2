"""Supplement for the lifetime test: names whose effect should last a stage / a few turns / the journey. Written BEFORE the run (mine)."""
SUPP = {"보충·지속": "폭우 가뭄 한파 야영지 진지 포위전 장마 방어진 결계 축제 사기충천 연기 최면 마취 졸음 불길 주문 마을 다리 우물 요새"}
SUPP_POOL = [(b, n) for b, s in SUPP.items() for n in s.split()]
# lifetime expectations (any-of). Includes the v2 ones so the 4 wordings can be compared on the same set.
EXPECT_LIFE = {**{n: ["stage"] for n in "야영지 진지 포위전 방어진 축제".split()},
               **{n: ["stage", "turns"] for n in "폭우 가뭄 한파 장마 결계 사기충천".split()},
               **{n: ["turns"] for n in "연기 최면 마취 졸음 주문".split()}, "불길": ["turns", "stage"],
               **{n: ["run", "forever"] for n in "마을 다리 우물 요새 성벽 오두막 제재소 대장간 망루 텃밭 은행 석상 평생 대대로".split()},
               **{n: ["instant"] for n in "즉사 화살 번개 운석 찰나 일회용".split()},
               **{n: ["forever"] for n in "영원 불멸 영구기관 무한지속".split()}, "영구빙결": ["forever", "run"], "하룻밤": ["turns", "stage"]}

"""Supplement names for the new axes (mine, chosen BEFORE the run) + pre-registered expectations on the new axes (any-of)."""
SUPP = {
 "보충·재료": "통나무 오두막 판자 제재소 참나무 장작 철광석 대장간 보석 갑옷 석상 쇠사슬 빵 사과 스튜 밀밭 닭 물고기 보물상자 은행 월급 상점 분노 용기",
 "보충·소환물": "기사 궁수 농부 일꾼 마을주민 늑대 곰 드래곤 슬라임 고블린 해골 좀비 유령 정령 천사 악마 요정 골렘 로봇 허수아비 수호신 도적 마법사 용사 쥐떼 거미",
 "보충·영구": "영원 불멸 영구기관 영원한불꽃 운명 세계의법칙 무한지속 일회용 찰나 하룻밤 평생 대대로",
}
SUPP_POOL = [(b, n) for b, s in SUPP.items() for n in s.split()]
# axis -> {name: [accepted options]}   (mine, fixed before the run)
EXPECT = {
 "material": {**{n: ["wood"] for n in "통나무 오두막 판자 제재소 참나무 장작".split()},
              **{n: ["ore"] for n in "철광석 대장간 보석 갑옷 석상 쇠사슬 성벽 곡괭이 압정 미스릴 오리하르콘".split()},
              **{n: ["food"] for n in "빵 사과 스튜 밀밭 닭 물고기 텃밭 씨앗 양봉장 든든한국밥".split()},
              **{n: ["gold"] for n in "보물상자 은행 월급 상점 이자 복권 상인 자본주의 골드두배".split()}, "금화 주머니": ["gold"],
              **{n: ["none"] for n in "분노 용기 번개 절망 망각 시간정지 절대영도".split()}},
 "lifetime": {**{n: ["instant"] for n in "즉사 화살 번개 운석 찰나 일회용".split()},
              **{n: ["run", "forever"] for n in "성벽 오두막 제재소 대장간 망루 텃밭 은행 석상 평생 대대로".split()},
              **{n: ["forever"] for n in "영원 불멸 영구기관 무한지속".split()}, "영구빙결": ["forever", "run"], "하룻밤": ["turns", "stage"]},
 "trigger": {"데미지반사": ["hit"], "자동부활": ["death"], "함정": ["approach"], "압정": ["approach"], "가시덤불": ["approach", "hit"], "동귀어진": ["death", "hit"]},
 "bagfate": {**{n: ["used_up"] for n in "폭죽 포션 시한폭탄 자폭 일회용".split()}, **{n: ["passive"] for n in "부적 상태이상면역".split()},
             **{n: ["returns"] for n in "화염검 곡괭이 부메랑 방패".split()}},
 "role": {**{n: ["build"] for n in "성벽 망루 텃밭 오두막 제재소 대장간 은행 모닥불".split()},
          **{n: ["summon"] for n in "병사 상인 기사 궁수 농부 일꾼 마을주민 늑대 곰 드래곤 슬라임 고블린 해골 좀비 유령 정령 천사 악마 요정 골렘 로봇 허수아비 수호신 도적 마법사 용사 쥐떼 거미".split()},
          **{n: ["move"] for n in ["순간이동"]}, **{n: ["cast"] for n in "즉사 화염검 번개 운석 화살".split()}},
 "unit": {**{n: ["soldier"] for n in "병사 기사 궁수 용사".split()}, **{n: ["worker"] for n in "농부 일꾼 마을주민 상인 대장장이".split()},
          **{n: ["beast"] for n in "늑대 곰 드래곤 슬라임 쥐떼 거미 고블린".split()}, **{n: ["spirit"] for n in "유령 정령 천사 악마 요정 수호신".split()},
          **{n: ["construct"] for n in "골렘 로봇 석상 허수아비".split()}},
 "allegiance": {**{n: ["ally"] for n in "병사 기사 궁수 농부 일꾼 마을주민 상인 요정 천사 수호신 용사 대장장이".split()},
                **{n: ["hostile"] for n in "슬라임 고블린 해골 좀비 악마 도적 쥐떼 거미".split()}},
}

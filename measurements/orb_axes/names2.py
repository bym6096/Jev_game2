"""Director-provided name pool (2026-11-05), 200 names in 10 blocks, plus expectations written BEFORE the run (mine; any-of lists)."""
BLOCKS = {
 "과학·물리": "절대영도 플라즈마 초전도체 사건의지평선 진공붕괴 반물질 중성자별 감마선폭발 핵융합 타키온 영점진동 초신성 볼텍스 특이점 방사능누출 암흑물질 쿼크글루온 중력파 극초음속 대전류",
 "모순 어구": "차가운불꽃 마른번개 어두운빛 젖은숯 맹독치유 무거운깃털 뜨거운얼음 조용한폭발 투명한벽돌 느린광속 부드러운칼날 건조한해일 살아있는시체 고요한태풍 눈먼주시자 가벼운납 자비로운참수 메마른눈물 질서있는혼돈 얼어붙은용암",
 "게임 키워드": "즉사 무적 쿨타임0 흡혈 데미지반사 방어무시 무한관통 확정치명타 절대은신 광역도발 자동부활 영구빙결 자원강탈 사거리무한 시간정지 상태이상면역 공격속도상한돌파 골드두배 맵전체타격 장판지속",
 "신화·전설": "흑염룡 엑스칼리버 롱기누스의창 오리하르콘 미스릴 데스노트 마안 현자의돌 우로보로스 네크로노미콘 궁니르 판도라의상자 묠니르 성배 세계수수액 드래곤브레스 묵시록 아포칼립스 영혼수확자 마검",
 "게임 은어·밈": "억까 날먹 극딜 가성비 창렬 혜자 존버 똥겜 갓겜 누킹 물몸 딜찍누 뇌절 든든한국밥 버스승객 막타 떡상 떡락 민트초코",
 "추상·감정": "침묵의나선 엔트로피 인과율 허무 절망 질투 탐욕 나태 열등감 자본주의 공리주의 데자뷔 망각 고독 트라우마 아이러니 우울 광기 희생 카타르시스 윤회",
 "일상 사물": "바나나껍질 레고블록 젖은수건 USB메모리 압정 커피머신 뽁뽁이 진공청소기 지우개 박스테이프 각설탕 이태리타월 모기향 파리채 젖은신문지 종이비행기 고무줄 이쑤시개 돋보기 형광펜",
 "의학·신체": "아드레날린 파상풍 동맥경화 카페인쇼크 편두통 젖산축적 저혈당 복합골절 뇌진탕 급성위염 면역결핍 호르몬폭주 동상 탈수 과호흡 환각 심실세동 세포괴사 신경마비 도파민과다",
 "위험·희생": "자폭 동귀어진 폭주 엔진과열 유리대포 시한폭탄 흡혈역류 영혼저당 생명력제물 피아식별불가 오버클럭 방사능오염 저주받은피 부메랑 잔탄소진 누전 역풍 자해공갈 파멸의계약 붕괴위험",
 "장난·한계": "냥냥펀치 쌉가능 어둠의다크 운명의데스티니 폭발폭발폭발 불얼음번개독 이것은구슬이다 아무것도아님 테스트용구슬1호 123456789 물음표느낌표 무지개빛총공격 내일월요일 칼퇴근 기가차드 최후의만찬 갓난아기주먹 핵폭탄급방귀 제로수렴 무한대발산",
}
POOL = [(b, n) for b, s in BLOCKS.items() for n in s.split()]
# any-of expectations on the verb choice (selected set must contain at least one). Mine, fixed before the run.
EXPECT = {
 "절대영도": "control damage debuff", "초신성": "damage", "핵융합": "damage energy", "방사능누출": "debuff damage",
 "마른번개": "damage", "맹독치유": "heal debuff", "자비로운참수": "damage remove", "뜨거운얼음": "control damage debuff",
 "즉사": "damage remove", "무적": "guard", "쿨타임0": "tempo", "흡혈": "heal damage steal", "데미지반사": "guard damage",
 "방어무시": "damage debuff", "무한관통": "damage", "확정치명타": "damage", "절대은신": "guard", "광역도발": "control guard debuff",
 "자동부활": "heal", "영구빙결": "control", "자원강탈": "steal harvest money", "시간정지": "control tempo", "상태이상면역": "guard",
 "공격속도상한돌파": "tempo buff", "골드두배": "money amplify", "맵전체타격": "damage",
 "데스노트": "damage remove", "현자의돌": "transform money heal", "우로보로스": "recycle heal grow", "성배": "heal",
 "세계수수액": "heal grow energy", "드래곤브레스": "damage", "엑스칼리버": "damage", "묠니르": "damage", "영혼수확자": "damage remove steal",
 "마안": "control debuff peek", "극딜": "damage", "가성비": "money", "누킹": "damage", "막타": "damage", "떡상": "money grow buff",
 "떡락": "money debuff", "존버": "guard", "든든한국밥": "heal energy buff", "망각": "trash remove", "윤회": "recycle",
 "탐욕": "money steal", "자본주의": "money", "절망": "debuff", "우울": "debuff", "광기": "debuff buff", "카타르시스": "heal remove",
 "데자뷔": "recycle peek", "지우개": "trash remove", "진공청소기": "draw", "돋보기": "peek", "파리채": "damage", "커피머신": "energy create buff",
 "바나나껍질": "control debuff", "아드레날린": "buff tempo energy", "파상풍": "debuff damage", "저혈당": "debuff", "복합골절": "debuff damage",
 "뇌진탕": "control debuff damage", "동상": "debuff control damage", "탈수": "debuff", "환각": "debuff control", "심실세동": "damage debuff",
 "세포괴사": "damage debuff remove", "신경마비": "control", "면역결핍": "debuff", "자폭": "damage", "동귀어진": "damage", "오버클럭": "buff tempo energy",
 "시한폭탄": "damage", "부메랑": "recycle damage", "방사능오염": "debuff damage", "누전": "damage debuff", "칼퇴근": "tempo energy heal",
 "냥냥펀치": "damage", "핵폭탄급방귀": "damage debuff", "갓난아기주먹": "damage", "폭발폭발폭발": "damage", "불얼음번개독": "damage",
}
EXPECT = {k: v.split() for k, v in EXPECT.items()}

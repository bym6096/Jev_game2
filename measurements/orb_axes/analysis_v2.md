## 1. 안정성 (3번 반복, 전체 318개)
| 축 | 1순위가 3번 중 바뀐 이름 (전체) | 분명한 이름(191) 중 | 애매한 이름(93) 중 |
|---|---|---|---|
| guard | 0/318 | 0 | 0 |
| role | 9/318 | 5 | 3 |
| timing | 6/318 | 3 | 2 |
| trigger | 6/318 | 5 | 0 |
| range | 25/318 | 16 | 6 |
| material | 11/318 | 6 | 4 |
| lifetime | 37/318 | 16 | 17 |
| bagfate | 12/318 | 7 | 4 |
| verb | 27/318 | 0 | 22 |
| unit | 17/318 | 13 | 3 |
| allegiance | 9/318 | 3 | 2 |

## 2. 미리 적은 기대값과 일치 (3번 평균의 1순위)
| 축 | 일치 | 어긋난 것 (이름: 실제 1순위 확률 / 기대) |
|---|---|---|
| material | 43/44 | 제재소: gold 0.32 / wood |
| lifetime | 22/22 | — |
| trigger | 5/6 | 동귀어진: none 0.65 / death|hit |
| bagfate | 10/11 | 부적: used_up 0.43 / passive |
| role | 41/42 | 마법사: cast 0.52 / summon |
| unit | 26/26 | — |
| allegiance | 20/20 | — |

**전체: 167/171 = 98%**

## 3. 분포 (보충 제외, 기존 이름 256개의 1순위)
- role: {'cast': 201, 'build': 29, 'move': 13, 'summon': 13}
- timing: {'now': 206, 'repeating': 22, 'trigger': 14, 'delayed': 14}
- trigger: {'none': 233, 'approach': 8, 'turn': 8, 'death': 4, 'hit': 3}
- range: {'self': 71, 'one': 69, 'around': 60, 'wide': 40, 'line': 16}
- material: {'none': 181, 'ore': 34, 'food': 16, 'wood': 13, 'gold': 12}
- lifetime: {'instant': 75, 'forever': 71, 'turns': 54, 'run': 53, 'stage': 3}
- bagfate: {'returns': 236, 'used_up': 17, 'passive': 3}
- unit: {'spirit': 128, 'beast': 40, 'construct': 35, 'soldier': 30, 'worker': 23}
- allegiance: {'ally': 148, 'hostile': 108}
- lifetime=forever인 이름: 절대영도(0.86), 초전도체(0.53), 사건의지평선(0.84), 중성자별(0.82), 핵융합(0.33), 타키온(0.36), 영점진동(0.31), 특이점(0.70), 암흑물질(0.85), 쿼크글루온(0.63), 어두운빛(0.36), 무거운깃털(0.27), 뜨거운얼음(0.36), 살아있는시체(0.39), 눈먼주시자(0.53), 가벼운납(0.30), 질서있는혼돈(0.70), 얼어붙은용암(0.48), 무적(0.74), 무한관통(0.60), 절대은신(0.69), 자동부활(0.38), 영구빙결(1.00), 사거리무한(0.91), 상태이상면역(0.70), 공격속도상한돌파(0.46), 흑염룡(0.39), 엑스칼리버(0.69), 롱기누스의창(0.53), 오리하르콘(0.64), 미스릴(0.52), 데스노트(0.66), 현자의돌(0.53), 우로보로스(0.92), 네크로노미콘(0.58), 궁니르(0.49), 판도라의상자(0.52), 묠니르(0.51), 성배(0.50), 묵시록(0.71), 아포칼립스(0.69), 가성비(0.34), 갓겜(0.29), 물몸(0.39), 엔트로피(0.90), 인과율(0.99), 허무(0.53), 절망(0.45), 탐욕(0.63), 자본주의(0.87), 공리주의(0.90), 망각(0.72), 트라우마(0.75), 아이러니(0.44), 윤회(0.90), 동맥경화(0.65), 면역결핍(0.47), 동귀어진(0.50), 영혼저당(0.60), 피아식별불가(0.39), 방사능오염(0.52), 저주받은피(0.74), 어둠의다크(0.57), 운명의데스티니(0.92), 이것은구슬이다(0.57), 제로수렴(0.49), 무한대발산(0.86), 저주(0.62), 얼음(0.40), 불사조(0.68), 블랙홀(0.74)
- lifetime=run인 이름: 방사능누출, 투명한벽돌, 부드러운칼날, 마안, 세계수수액, 마검, 창렬, 혜자, 똥겜, 침묵의나선, 레고블록, USB메모리, 압정, 커피머신, 진공청소기, 박스테이프, 이태리타월, 파리채, 고무줄, 돋보기, 형광펜, 파상풍, 동상, 유리대포, 파멸의계약, 테스트용구슬1호, 기가차드, 화염검, 방패, 치유의 샘, 금화 주머니, 곡괭이, 씨앗, 텃밭, 성벽, 눈덩이, 나침반, 수정 구슬, 자석, 망루, 거울, 시계, 연금술, 깃발, 수박, 베개, 낡은 신발, 상인, 도서관, 대장장이, 가시덤불, 양봉장, 피리
- trigger 조건이 none이 아닌데 시점이 trigger가 아닌 이름: 쿨타임0(turn 0.68, 시점 delayed), 흡혈(hit 0.80, 시점 now), 확정치명타(hit 0.54, 시점 now), 사거리무한(approach 0.44, 시점 repeating), 장판지속(turn 0.53, 시점 repeating), 영혼수확자(death 0.84, 시점 now), 윤회(death 0.70, 시점 repeating), 압정(approach 0.48, 시점 now), 시한폭탄(turn 0.76, 시점 delayed), 내일월요일(turn 0.87, 시점 delayed), 칼퇴근(turn 0.54, 시점 now), 시한폭탄(turn 0.74, 시점 delayed), 자석(approach 0.50, 시점 now), 망루(approach 0.62, 시점 now), 시계(turn 0.81, 시점 delayed), 새로운 시작(turn 0.50, 시점 now)

## 4. 판 깨기: 영구 지속을 이름으로 부를 수 있나 (보충·영구 12개)
- 영원: forever 1.00 / instant 0.00 / turns 0.00 | 힘 3.6
- 불멸: forever 0.99 / run 0.01 / instant 0.00 | 힘 3.9
- 영구기관: forever 0.97 / run 0.03 / instant 0.00 | 힘 3.9
- 영원한불꽃: forever 0.96 / turns 0.03 / run 0.01 | 힘 3.5
- 운명: forever 0.97 / run 0.02 / instant 0.01 | 힘 3.7
- 세계의법칙: forever 1.00 / run 0.00 / instant 0.00 | 힘 4.6
- 무한지속: forever 0.98 / turns 0.01 / run 0.01 | 힘 3.4
- 일회용: instant 0.97 / turns 0.02 / stage 0.01 | 힘 0.5
- 찰나: instant 0.98 / turns 0.02 / stage 0.00 | 힘 1.5
- 하룻밤: turns 0.49 / stage 0.40 / instant 0.08 | 힘 0.9
- 평생: forever 0.66 / run 0.34 / instant 0.00 | 힘 1.9
- 대대로: forever 0.67 / run 0.29 / turns 0.02 | 힘 1.7

## 5. 축끼리 모순 (기존 이름 256개)
모순이 하나라도 있는 이름: 22/256 = 9% (v1에서는 31/256 = 12%)
- 조건이 있는데 시점이 트리거 아님: 13개 (예: 쿨타임0, 흡혈, 확정치명타, 장판지속, 영혼수확자, 윤회)
- 건물인데 지속이 짧음: 3개 (예: 장판지속, 함정, 모닥불)
- 시점=트리거인데 조건 없음: 7개 (예: 인과율, 저혈당, 누전, 역풍, 붕괴위험, 방패)

## 6. 소환 역할인 이름의 소환물 종류·아군/적대 (보충 포함)
role=summon으로 읽힌 이름 40개
- 살아있는시체: beast 0.57, hostile 0.94, 동사 recycle 0.40
- 흑염룡: beast 0.79, hostile 0.61, 동사 damage 0.84
- 네크로노미콘: spirit 0.86, hostile 0.82, 동사 damage 0.40
- 궁니르: spirit 0.57, hostile 0.58, 동사 damage 0.24
- 창렬: soldier 0.45, ally 0.84, 동사 buff 0.24
- 혜자: spirit 0.45, ally 0.89, 동사 money 0.25
- 버스승객: worker 1.00, ally 0.84, 동사 money 0.34
- 기가차드: soldier 0.33, ally 0.58, 동사 money 0.38
- 병사: soldier 1.00, ally 0.95, 동사 damage 0.51
- 벌 떼: beast 0.99, hostile 0.73, 동사 damage 0.70
- 상인: worker 1.00, ally 0.98, 동사 money 1.00
- 대장장이: worker 0.99, ally 0.98, 동사 create 0.91
- 불사조: beast 0.51, ally 0.88, 동사 recycle 0.93
- 닭: beast 0.99, ally 0.59, 동사 grow 0.53
- 물고기: beast 1.00, ally 0.65, 동사 harvest 0.49
- 기사: soldier 1.00, ally 0.95, 동사 damage 0.38
- 궁수: soldier 1.00, ally 0.93, 동사 damage 0.85
- 농부: worker 1.00, ally 0.99, 동사 grow 0.49
- 일꾼: worker 1.00, ally 1.00, 동사 harvest 0.41
- 마을주민: worker 1.00, ally 0.96, 동사 money 0.28
- 늑대: beast 1.00, hostile 0.82, 동사 damage 0.76
- 곰: beast 1.00, hostile 0.79, 동사 damage 0.33
- 드래곤: beast 0.99, hostile 0.67, 동사 damage 0.79
- 슬라임: beast 1.00, hostile 0.79, 동사 control 0.23
- 고블린: beast 0.85, hostile 0.89, 동사 steal 0.27
- 해골: spirit 0.65, hostile 0.94, 동사 damage 0.77
- 좀비: beast 0.92, hostile 0.97, 동사 recycle 0.44
- 유령: spirit 1.00, hostile 0.82, 동사 recycle 0.25
- 정령: spirit 1.00, ally 0.86, 동사 create 0.31
- 천사: spirit 1.00, ally 0.97, 동사 heal 0.62
- 악마: spirit 0.51, hostile 0.99, 동사 damage 0.77
- 요정: spirit 0.98, ally 0.85, 동사 buff 0.29
- 골렘: construct 1.00, ally 0.67, 동사 guard 0.48
- 로봇: construct 1.00, ally 0.86, 동사 create 0.24
- 허수아비: construct 0.71, ally 0.66, 동사 guard 0.41
- 수호신: spirit 0.99, ally 0.99, 동사 guard 0.97
- 도적: soldier 0.63, hostile 0.80, 동사 steal 0.96
- 용사: soldier 0.99, ally 0.99, 동사 buff 0.43
- 쥐떼: beast 1.00, hostile 0.81, 동사 steal 0.30
- 거미: beast 1.00, hostile 0.91, 동사 control 0.84

## 7. 동사 create가 소환과 겹치나 (고친 문구)
- role=summon인데 1순위 동사가 create: ['대장장이', '정령', '로봇']
- 병사: [('damage', 0.51), ('guard', 0.21), ('create', 0.16)] (v1: create 0.45 / damage 0.34)

## 8. 재료: 자원 동사가 뽑힌 이름의 재료
- 동사 harvest (2개): {'ore': 1, 'food': 1}
- 동사 grow (3개): {'food': 3}
- 동사 money (27개): {'none': 11, 'gold': 10, 'food': 4, 'ore': 2}
- 동사 create (8개): {'ore': 6, 'none': 2}
## 1. 안정성 (3번 반복)
- guard: 1순위가 3번 중 달라진 이름 0/256
- role: 1순위가 3번 중 달라진 이름 17/256
- timing: 1순위가 3번 중 달라진 이름 13/256
- range: 1순위가 3번 중 달라진 이름 22/256
- side: 1순위가 3번 중 달라진 이름 21/256
- persist: 1순위가 3번 중 달라진 이름 15/256
- pay: 1순위가 3번 중 달라진 이름 1/256
- verb: 1순위가 3번 중 달라진 이름 22/256
- 예/아니오(5개) 0.5선 넘나듦 29/1280

## 2. 동사 선택 (1순위 + 1순위 40% 이상, 최대 3개)
개수 분포(새 이름 200개): {1: 111, 2: 51, 3: 38} 평균 1.64
1순위 동사 사용 분포: {'damage': 60, 'debuff': 25, 'money': 22, 'control': 14, 'recycle': 14, 'tempo': 7, 'steal': 7, 'energy': 6, 'heal': 6, 'guard': 6, 'trash': 6, 'amplify': 5, 'transform': 5, 'create': 5, 'peek': 5, 'remove': 4, 'buff': 3}
한 번도 1순위가 안 된 동사: ['harvest', 'grow', 'draw']
블록별 1순위 확률 평균 / 0.4 미만 비율 / 평균 개수 / 힘 평균
- 과학·물리: 0.67 / 5/20 / 1.3 / 3.3
- 모순 어구: 0.54 / 8/20 / 1.9 / 2.0
- 게임 키워드: 0.73 / 1/20 / 1.4 / 2.7
- 신화·전설: 0.63 / 7/20 / 1.5 / 3.4
- 게임 은어·밈: 0.43 / 13/19 / 2.2 / 1.4
- 추상·감정: 0.61 / 5/21 / 1.4 / 1.9
- 일상 사물: 0.47 / 11/20 / 1.9 / 0.5
- 의학·신체: 0.53 / 5/20 / 1.8 / 1.5
- 위험·희생: 0.58 / 5/20 / 1.7 / 2.0
- 장난·한계: 0.57 / 7/20 / 1.5 / 1.7
1순위 확률 0.4 미만(애매한 이름) 67/200: 젖은숯(0.15 energy), 잔탄소진(0.17 damage), 뽁뽁이(0.18 money), 제로수렴(0.19 remove), 쌉가능(0.2 money), 가벼운납(0.21 tempo), 뇌절(0.21 recycle), 특이점(0.22 amplify), 물몸(0.22 heal), 과호흡(0.22 energy), 궁니르(0.23 damage), 창렬(0.23 buff), 떡락(0.23 damage), 칼퇴근(0.24 money), 엔트로피(0.25 transform), 이태리타월(0.25 heal), 최후의만찬(0.25 damage), 어두운빛(0.26 debuff), 질서있는혼돈(0.26 transform), 날먹(0.26 money), 혜자(0.26 money), 딜찍누(0.26 money), 메마른눈물(0.27 debuff), 민트초코(0.27 money), 동귀어진(0.28 recycle), 영혼저당(0.28 steal), 피아식별불가(0.28 transform), 판도라의상자(0.29 debuff), 커피머신(0.29 energy), 생명력제물(0.29 heal), 미스릴(0.3 create), 마안(0.3 money), 영점진동(0.31 recycle), 건조한해일(0.31 damage), 억까(0.31 money), 든든한국밥(0.32 heal), 버스승객(0.32 money), 희생(0.32 damage), 이쑤시개(0.32 damage), 심실세동(0.32 debuff), 테스트용구슬1호(0.32 create), 123456789(0.32 money), 뜨거운얼음(0.33 transform), 오리하르콘(0.33 money), 카페인쇼크(0.33 energy), 암흑물질(0.34 damage), 각설탕(0.34 money), 형광펜(0.34 peek), 호르몬폭주(0.34 buff), 네크로노미콘(0.35 damage), 존버(0.35 guard), 고독(0.35 debuff), 모기향(0.35 debuff), 세계수수액(0.36 money), 박스테이프(0.36 create), 기가차드(0.36 money), 쿼크글루온(0.37 damage), 파상풍(0.37 damage), 살아있는시체(0.38 recycle), 인과율(0.38 recycle), 아이러니(0.38 recycle), 바나나껍질(0.38 debuff), 대전류(0.39 damage), 장판지속(0.39 recycle), 떡상(0.39 amplify), USB메모리(0.39 money), 진공청소기(0.4 trash)

## 3. 미리 적은 기대값 (새 이름 중 기대가 있는 것)
- 1순위만: 72/84
- 상대 규칙(40%, 최대 3): 79/84
- 상위 2개: 80/84
상대 규칙에서 어긋난 것 (이름: 실제 상위3 / 기대):
  - 쿨타임0: recycle,tempo,energy / tempo
  - 마안: money,guard,damage / control,debuff,peek
  - 세계수수액: money,harvest,grow / heal,grow,energy
  - 탈수: steal,remove,debuff / debuff
  - 동귀어진: recycle,transform,amplify / damage

## 4. 기존 56개를 v1로 다시 (v0 선택질문 17개 때와 비교)
- 있어야 하는 동사 포함 35/39 (v0 선택질문: 36/39), 없어야 하는 동사 섞임 0/21 (v0: 0/21), 평균 개수 1.43 (v0: 1.5)
- 금화 주머니: ['money'] | 곡괭이: ['harvest'] | 도박: ['money'] | 파쇄기: ['damage'] | 블랙홀: ['control', 'draw']

## 5. 지시문 판정(guard)
지시로 읽힌 확률 상위: 123456789 0.24, 쌉가능 0.07, 쿨타임0 0.06, 억까 0.04, 딜찍누 0.04, 물음표느낌표 0.04

## 6. 돈 시점(pay): 동사에 money가 뽑힌 이름 / 그 외
money 선택 33개: 골드두배→now, 오리하르콘→none, 마안→none, 현자의돌→none, 궁니르→none, 세계수수액→none, 억까→none, 날먹→none, 가성비→none, 창렬→none, 혜자→none, 존버→none, 갓겜→none, 딜찍누→none, 든든한국밥→none, 버스승객→none, 떡상→none, 떡락→none, 민트초코→none, 탐욕→none, 자본주의→none, 공리주의→none, USB메모리→none, 커피머신→none, 뽁뽁이→none, 각설탕→none, 영혼저당→none, 잔탄소진→none, 쌉가능→none, 이것은구슬이다→none, 123456789→none, 칼퇴근→payday, 기가차드→none
money가 아닌 이름의 pay 분포: {'none': 165, 'now': 1, 'steady': 1}

## 7. 선택 축 분포 (새 이름 200개, 1순위)
- role: {'instant': 119, 'lasting': 54, 'build': 13, 'summon': 8, 'move': 6}
- timing: {'now': 152, 'ongoing': 28, 'trigger': 10, 'delayed': 10}
- range: {'self': 57, 'one': 55, 'wide': 38, 'around': 38, 'line': 12}
- side: {'all': 78, 'ally': 52, 'enemy': 41, 'land': 29}
- persist: {'returns': 180, 'used_up': 12, 'stays': 6, 'passive': 2}
- pay: {'none': 196, 'now': 2, 'steady': 1, 'payday': 1}
- 덧붙는 성질(0.6 이상 중 최고 하나): {'(없음)': 153, 'risky': 24, 'conditional': 10, 'random': 7, 'scaling': 4, 'network': 2}

## 8. 전체 표 (새 이름 200개)
이름 | 역할/시점/범위/대상/지속 | 동사(확률) | 성질 | 힘 | 비고

### 과학·물리
- 절대영도 | lasting/now/wide/all/returns | control 0.75 | — | 4.4 | 
- 플라즈마 | instant/now/around/all/returns | damage 0.90 | — | 2.7 | 
- 초전도체 | lasting/now/wide/land/returns | energy 0.71 | conditional | 2.3 | 
- 사건의지평선 | lasting/trigger/around/all/returns | control 0.71 | — | 3.8 | 
- 진공붕괴 | instant/now/around/all/returns | damage 0.84 | — | 3.9 | 
- 반물질 | instant/now/around/all/returns | damage 0.92 | — | 3.6 | 
- 중성자별 | build/now/around/all/returns | damage 0.68 | — | 3.6 | 
- 감마선폭발 | instant/now/around/all/returns | damage 0.99 | — | 3.0 | 
- 핵융합 | instant/now/wide/all/returns | energy 0.74 | conditional | 3.6 | 
- 타키온 | move/now/line/all/returns | tempo 0.62 | — | 2.7 | 
- 영점진동 | lasting/ongoing/around/all/returns | recycle 0.31, remove 0.15 | — | 2.6 | 애매
- 초신성 | instant/now/around/all/used_up | damage 0.93 | — | 3.7 | 
- 볼텍스 | lasting/now/around/all/returns | control 0.70 | — | 2.9 | 
- 특이점 | instant/now/wide/all/returns | amplify 0.22, control 0.15, damage 0.14 | — | 4.5 | 애매
- 방사능누출 | lasting/ongoing/around/all/used_up | debuff 0.72 | risky | 2.4 | 
- 암흑물질 | instant/now/wide/all/returns | damage 0.34, energy 0.20 | — | 3.6 | 애매
- 쿼크글루온 | instant/now/wide/all/returns | damage 0.37, energy 0.19 | — | 2.8 | 애매
- 중력파 | instant/now/around/all/returns | damage 0.69, control 0.29 | — | 3.4 | 
- 극초음속 | instant/now/line/all/returns | tempo 0.89 | — | 2.7 | 
- 대전류 | lasting/ongoing/line/all/returns | damage 0.39 | — | 2.8 | 애매

### 모순 어구
- 차가운불꽃 | instant/now/around/all/returns | damage 0.52, control 0.40 | — | 2.3 | 
- 마른번개 | instant/now/line/all/returns | damage 0.85 | — | 2.0 | 
- 어두운빛 | instant/now/around/all/returns | debuff 0.26, damage 0.25, energy 0.14 | — | 2.0 | 애매
- 젖은숯 | instant/now/one/land/returns | energy 0.15, trash 0.14, debuff 0.13 | — | 0.7 | 애매
- 맹독치유 | instant/now/one/ally/returns | heal 0.81 | — | 2.3 | 
- 무거운깃털 | move/now/one/ally/returns | debuff 0.52 | — | 1.0 | 
- 뜨거운얼음 | instant/now/around/land/returns | transform 0.33, damage 0.24, control 0.24 | — | 1.7 | 애매
- 조용한폭발 | instant/delayed/around/all/returns | damage 0.94 | — | 2.4 | 
- 투명한벽돌 | build/now/one/land/stays | guard 0.74 | — | 0.8 | 
- 느린광속 | lasting/delayed/line/all/returns | debuff 0.72 | — | 2.0 | 
- 부드러운칼날 | instant/now/one/enemy/returns | damage 0.95 | — | 1.4 | 
- 건조한해일 | lasting/now/wide/land/returns | damage 0.31, debuff 0.23 | — | 2.4 | 애매
- 살아있는시체 | summon/now/one/enemy/returns | recycle 0.38, damage 0.18 | — | 2.0 | 애매
- 고요한태풍 | lasting/now/around/all/returns | control 0.44, damage 0.35 | — | 3.0 | 
- 눈먼주시자 | lasting/ongoing/wide/enemy/returns | debuff 0.51, peek 0.31 | — | 3.3 | 
- 가벼운납 | build/now/one/land/returns | tempo 0.21, create 0.18, buff 0.12 | — | 0.8 | 애매
- 자비로운참수 | instant/now/one/enemy/returns | damage 0.93 | — | 2.5 | 
- 메마른눈물 | instant/now/one/land/returns | debuff 0.27, remove 0.15, heal 0.14 | — | 1.5 | 애매
- 질서있는혼돈 | lasting/now/wide/all/returns | transform 0.26, control 0.21, recycle 0.16 | random | 2.8 | 애매
- 얼어붙은용암 | lasting/now/around/land/returns | control 0.76 | — | 2.6 | 

### 게임 키워드
- 즉사 | instant/now/one/enemy/returns | damage 0.93 | — | 2.9 | 
- 무적 | lasting/ongoing/self/ally/returns | guard 0.86 | — | 3.9 | 
- 쿨타임0 | instant/delayed/self/ally/returns | recycle 0.73 | — | 0.6 | 규칙상 입력 불가 기대와 다름
- 흡혈 | instant/now/one/enemy/returns | steal 0.74 | risky | 2.1 | 
- 데미지반사 | lasting/trigger/self/enemy/passive | guard 0.43, damage 0.36 | conditional | 2.0 | 
- 방어무시 | instant/now/one/enemy/returns | damage 0.59 | — | 2.6 | 
- 무한관통 | instant/now/line/all/returns | damage 0.95 | — | 3.8 | 
- 확정치명타 | instant/now/one/enemy/returns | damage 0.79 | conditional | 2.8 | 
- 절대은신 | lasting/ongoing/self/ally/returns | guard 0.61 | — | 3.8 | 
- 광역도발 | lasting/now/around/enemy/returns | control 0.68 | network | 2.4 | 
- 자동부활 | lasting/trigger/self/ally/returns | recycle 0.65, heal 0.35 | — | 3.1 | 
- 영구빙결 | lasting/now/one/all/returns | control 1.00 | — | 3.3 | 
- 자원강탈 | instant/now/one/enemy/returns | steal 0.98 | — | 2.5 | 
- 사거리무한 | lasting/ongoing/wide/all/returns | recycle 0.52, amplify 0.26 | — | 3.3 | 
- 시간정지 | lasting/now/wide/all/returns | control 0.99 | — | 3.7 | 
- 상태이상면역 | lasting/ongoing/self/ally/passive | guard 0.44, buff 0.28, remove 0.26 | — | 2.5 | 
- 공격속도상한돌파 | lasting/ongoing/self/ally/returns | tempo 0.77 | — | 2.4 | 
- 골드두배 | instant/now/self/ally/returns | amplify 0.53, money 0.47 | scaling | 1.9 | 
- 맵전체타격 | instant/now/wide/all/returns | damage 0.98 | — | 3.5 | 
- 장판지속 | lasting/ongoing/around/land/stays | recycle 0.39, amplify 0.19 | — | 1.6 | 애매

### 신화·전설
- 흑염룡 | summon/now/around/enemy/returns | damage 0.84 | — | 3.7 | 
- 엑스칼리버 | instant/now/one/enemy/returns | damage 0.94 | — | 4.0 | 
- 롱기누스의창 | instant/now/one/enemy/returns | damage 0.95 | — | 3.9 | 
- 오리하르콘 | build/now/self/land/returns | money 0.33, create 0.30 | — | 3.8 | 애매
- 미스릴 | build/now/one/land/returns | create 0.30, harvest 0.21, guard 0.20 | — | 2.9 | 애매
- 데스노트 | instant/now/one/enemy/returns | damage 0.79 | risky, conditional | 3.9 | 
- 마안 | build/now/one/land/returns | money 0.30, guard 0.24 | — | 1.7 | 애매 기대와 다름
- 현자의돌 | instant/now/wide/ally/returns | money 0.60 | — | 3.7 | 
- 우로보로스 | lasting/ongoing/around/all/returns | recycle 0.99 | — | 3.9 | 
- 네크로노미콘 | summon/now/wide/enemy/returns | damage 0.35, recycle 0.17 | risky | 3.9 | 애매
- 궁니르 | instant/now/wide/ally/returns | damage 0.23, money 0.13, recycle 0.13 | — | 3.3 | 애매
- 판도라의상자 | summon/now/wide/all/used_up | debuff 0.29, create 0.21 | risky, random | 3.8 | 애매
- 묠니르 | instant/now/one/all/returns | damage 0.95 | — | 3.9 | 
- 성배 | build/now/wide/ally/returns | heal 0.58 | — | 3.9 | 
- 세계수수액 | instant/now/wide/land/returns | money 0.36, harvest 0.25 | — | 1.8 | 애매 기대와 다름
- 드래곤브레스 | instant/now/line/all/returns | damage 0.98 | — | 2.9 | 
- 묵시록 | instant/delayed/wide/all/returns | damage 0.45, peek 0.43 | — | 3.8 | 
- 아포칼립스 | instant/now/wide/all/returns | damage 0.96 | risky | 4.1 | 
- 영혼수확자 | instant/now/one/enemy/returns | steal 0.45 | risky | 3.1 | 
- 마검 | instant/now/one/enemy/returns | damage 0.93 | — | 2.6 | 

### 게임 은어·밈
- 억까 | instant/now/self/enemy/returns | money 0.31, steal 0.14, damage 0.13 | — | 1.2 | 애매
- 날먹 | instant/now/self/ally/used_up | money 0.26, tempo 0.13 | — | 1.0 | 애매
- 극딜 | instant/now/one/enemy/returns | damage 0.95 | conditional | 2.3 | 
- 가성비 | instant/now/self/ally/returns | money 0.76 | — | 0.7 | 
- 창렬 | summon/now/one/ally/returns | buff 0.23, money 0.19, damage 0.14 | — | 2.2 | 애매
- 혜자 | summon/now/self/ally/returns | money 0.26, heal 0.18, buff 0.17 | — | 1.6 | 애매
- 존버 | lasting/ongoing/self/ally/returns | guard 0.35, control 0.19, money 0.15 | — | 0.9 | 애매
- 똥겜 | instant/now/self/all/returns | trash 0.59 | — | 0.4 | 
- 갓겜 | instant/now/wide/ally/returns | money 0.47 | — | 2.7 | 
- 누킹 | instant/now/around/all/returns | damage 0.97 | — | 3.0 | 
- 물몸 | lasting/now/self/ally/returns | heal 0.22, guard 0.20, buff 0.12 | conditional | 1.6 | 애매
- 딜찍누 | instant/now/one/enemy/returns | money 0.26, peek 0.15, steal 0.13 | — | 1.2 | 애매
- 뇌절 | instant/now/self/ally/returns | recycle 0.21, trash 0.17, debuff 0.13 | — | 0.6 | 애매
- 든든한국밥 | instant/now/self/ally/returns | heal 0.32, money 0.20, buff 0.17 | — | 0.8 | 애매
- 버스승객 | summon/now/one/all/returns | money 0.32, draw 0.19, control 0.19 | — | 0.7 | 애매
- 막타 | instant/now/one/enemy/returns | damage 0.72 | — | 2.0 | 
- 떡상 | instant/now/self/ally/returns | amplify 0.39, money 0.19 | scaling | 1.8 | 애매
- 떡락 | instant/now/one/enemy/returns | damage 0.23, money 0.20 | random | 1.1 | 애매
- 민트초코 | instant/now/self/ally/returns | money 0.27, create 0.17, heal 0.12 | — | 0.5 | 애매

### 추상·감정
- 침묵의나선 | lasting/ongoing/around/all/returns | control 0.63 | — | 2.5 | 
- 엔트로피 | lasting/ongoing/wide/all/returns | transform 0.25, trash 0.23, debuff 0.16 | random | 3.3 | 애매
- 인과율 | instant/trigger/wide/all/returns | recycle 0.38, amplify 0.34 | network | 3.8 | 애매
- 허무 | instant/now/wide/all/returns | trash 0.50, remove 0.38 | — | 1.3 | 
- 절망 | lasting/now/wide/all/returns | debuff 0.79 | — | 2.0 | 
- 질투 | lasting/now/self/enemy/returns | steal 0.48, debuff 0.21 | — | 1.3 | 
- 탐욕 | lasting/ongoing/self/ally/returns | money 0.61, steal 0.33 | — | 1.7 | 
- 나태 | lasting/delayed/self/ally/returns | debuff 0.67 | — | 0.7 | 
- 열등감 | lasting/now/self/ally/returns | debuff 0.70 | — | 0.5 | 
- 자본주의 | lasting/ongoing/wide/all/returns | money 0.98 | scaling | 3.0 | 
- 공리주의 | instant/now/wide/all/returns | money 0.43 | — | 1.7 | 
- 데자뷔 | instant/now/self/ally/returns | recycle 0.90 | — | 1.5 | 
- 망각 | instant/now/wide/enemy/returns | trash 0.82 | — | 2.9 | 
- 고독 | lasting/now/self/ally/returns | debuff 0.35 | — | 1.1 | 애매
- 트라우마 | lasting/now/self/enemy/returns | debuff 0.71 | risky | 1.2 | 
- 아이러니 | instant/now/self/all/returns | recycle 0.38, transform 0.35 | — | 0.7 | 애매
- 우울 | lasting/ongoing/self/all/returns | debuff 0.84 | — | 0.8 | 
- 광기 | lasting/now/wide/all/returns | debuff 0.46 | random | 2.2 | 
- 희생 | instant/now/self/ally/used_up | damage 0.32, trash 0.19 | risky | 1.8 | 애매
- 카타르시스 | instant/now/self/ally/returns | remove 0.64 | — | 2.6 | 
- 윤회 | move/ongoing/wide/all/returns | recycle 1.00 | — | 3.2 | 

### 일상 사물
- 바나나껍질 | lasting/trigger/one/all/used_up | debuff 0.38, control 0.35, trash 0.18 | — | 0.1 | 애매
- 레고블록 | build/now/one/land/returns | create 0.79 | — | 0.7 | 
- 젖은수건 | instant/now/self/land/returns | remove 0.40 | — | 0.2 | 
- USB메모리 | build/now/self/ally/returns | money 0.39, transform 0.19 | — | 0.7 | 애매 규칙상 입력 불가
- 압정 | build/now/one/land/stays | control 0.69 | — | 0.2 | 
- 커피머신 | build/now/self/ally/returns | energy 0.29, money 0.26, create 0.21 | — | 0.8 | 애매
- 뽁뽁이 | instant/now/one/ally/returns | money 0.18, create 0.11, amplify 0.11 | — | 0.6 | 애매
- 진공청소기 | instant/now/around/land/returns | trash 0.40, draw 0.33, remove 0.19 | — | 0.8 | 애매
- 지우개 | instant/now/one/land/returns | remove 0.98 | — | 0.4 | 
- 박스테이프 | build/now/one/land/returns | create 0.36, control 0.20, guard 0.15 | — | 0.7 | 애매
- 각설탕 | instant/now/one/ally/used_up | money 0.34, create 0.14 | — | 0.6 | 애매
- 이태리타월 | instant/now/self/land/returns | heal 0.25, remove 0.14, create 0.13 | — | 0.8 | 애매
- 모기향 | lasting/ongoing/around/enemy/stays | debuff 0.35, damage 0.21 | — | 0.5 | 애매
- 파리채 | instant/now/one/enemy/returns | damage 0.49, control 0.22 | — | 0.3 | 
- 젖은신문지 | instant/now/one/land/used_up | trash 0.43 | — | 0.2 | 
- 종이비행기 | move/now/line/ally/returns | tempo 0.43 | — | 0.2 | 
- 고무줄 | move/now/line/all/returns | control 0.55 | — | 0.3 | 
- 이쑤시개 | instant/now/one/enemy/returns | damage 0.32 | — | 1.3 | 애매
- 돋보기 | instant/now/one/land/returns | peek 0.94 | — | 0.6 | 
- 형광펜 | lasting/now/line/land/returns | peek 0.34, amplify 0.17 | — | 0.4 | 애매

### 의학·신체
- 아드레날린 | instant/now/self/ally/returns | buff 0.55, tempo 0.37 | conditional | 1.2 | 
- 파상풍 | instant/trigger/self/all/returns | damage 0.37, debuff 0.35 | — | 1.4 | 애매
- 동맥경화 | lasting/delayed/wide/enemy/returns | debuff 0.80 | risky | 1.2 | 
- 카페인쇼크 | instant/now/self/ally/returns | energy 0.33, tempo 0.30, buff 0.17 | — | 1.8 | 애매
- 편두통 | instant/ongoing/self/enemy/returns | debuff 0.56, damage 0.35 | risky | 0.6 | 
- 젖산축적 | lasting/delayed/self/ally/returns | debuff 0.63 | — | 0.9 | 
- 저혈당 | instant/trigger/self/ally/returns | debuff 0.51 | conditional | 0.7 | 
- 복합골절 | instant/now/one/enemy/returns | damage 0.66 | — | 1.3 | 
- 뇌진탕 | instant/now/around/all/returns | damage 0.55, debuff 0.27 | risky | 2.4 | 
- 급성위염 | instant/now/self/ally/returns | debuff 0.46, damage 0.31 | — | 0.7 | 
- 면역결핍 | lasting/ongoing/one/enemy/returns | debuff 0.91 | risky | 1.8 | 
- 호르몬폭주 | instant/now/self/all/returns | buff 0.34, amplify 0.30 | random | 2.6 | 애매
- 동상 | build/now/one/land/stays | control 0.49, create 0.20 | — | 1.5 | 
- 탈수 | instant/now/one/land/returns | steal 0.47 | — | 1.6 | 기대와 다름
- 과호흡 | instant/ongoing/self/ally/returns | energy 0.22, debuff 0.21, tempo 0.13 | — | 0.9 | 애매
- 환각 | lasting/now/self/enemy/returns | transform 0.42, debuff 0.30, control 0.18 | — | 2.0 | 
- 심실세동 | instant/ongoing/self/all/returns | debuff 0.32, damage 0.25 | — | 1.5 | 애매
- 세포괴사 | instant/now/one/enemy/returns | damage 0.90 | risky | 1.9 | 
- 신경마비 | lasting/now/one/enemy/returns | control 0.78 | — | 2.0 | 
- 도파민과다 | lasting/ongoing/self/ally/returns | amplify 0.42, buff 0.23 | — | 1.6 | 

### 위험·희생
- 자폭 | instant/now/around/all/used_up | damage 0.97 | risky | 2.0 | 
- 동귀어진 | move/now/wide/all/returns | recycle 0.28, transform 0.20, amplify 0.14 | — | 2.5 | 애매 기대와 다름
- 폭주 | instant/now/around/all/returns | tempo 0.59 | random | 2.5 | 
- 엔진과열 | instant/now/self/ally/returns | damage 0.43, debuff 0.36 | — | 1.1 | 
- 유리대포 | instant/now/line/enemy/returns | damage 0.96 | — | 2.3 | 
- 시한폭탄 | instant/delayed/around/all/used_up | damage 0.96 | risky | 2.2 | 
- 흡혈역류 | lasting/ongoing/around/all/returns | steal 0.71 | risky | 2.7 | 
- 영혼저당 | instant/now/one/ally/returns | steal 0.28, money 0.22, control 0.16 | risky | 2.8 | 애매
- 생명력제물 | instant/now/one/ally/used_up | heal 0.29, steal 0.22, damage 0.18 | risky | 2.0 | 애매
- 피아식별불가 | instant/now/self/all/returns | transform 0.28, peek 0.21, remove 0.13 | — | 1.4 | 애매
- 오버클럭 | lasting/now/self/ally/returns | tempo 0.59 | conditional | 2.0 | 
- 방사능오염 | lasting/ongoing/around/land/stays | debuff 0.85 | risky | 2.3 | 
- 저주받은피 | lasting/ongoing/one/enemy/returns | debuff 0.80 | risky | 2.0 | 
- 부메랑 | instant/now/line/enemy/returns | recycle 0.66, damage 0.30 | — | 1.1 | 
- 잔탄소진 | instant/now/around/land/returns | damage 0.17, trash 0.13, money 0.11 | — | 2.1 | 애매
- 누전 | instant/trigger/around/all/returns | damage 0.56 | — | 1.0 | 
- 역풍 | instant/trigger/around/all/returns | control 0.45, debuff 0.20 | conditional | 2.0 | 
- 자해공갈 | instant/now/self/ally/returns | damage 0.41, debuff 0.17 | risky | 0.9 | 
- 파멸의계약 | lasting/now/one/all/returns | damage 0.74 | risky | 3.5 | 
- 붕괴위험 | instant/trigger/around/land/returns | damage 0.71 | — | 2.2 | 

### 장난·한계
- 냥냥펀치 | instant/now/one/enemy/returns | damage 0.97 | — | 0.7 | 
- 쌉가능 | instant/now/self/ally/returns | money 0.20, remove 0.11, trash 0.10 | — | 1.0 | 애매
- 어둠의다크 | instant/now/wide/enemy/returns | damage 0.50, debuff 0.24 | — | 2.3 | 
- 운명의데스티니 | instant/now/wide/all/returns | peek 0.65 | random | 3.6 | 
- 폭발폭발폭발 | instant/now/around/all/returns | damage 0.95 | — | 2.4 | 
- 불얼음번개독 | instant/now/around/all/returns | damage 0.81 | — | 3.0 | 
- 이것은구슬이다 | instant/now/self/land/returns | create 0.51, money 0.21 | — | 0.4 | 
- 아무것도아님 | instant/now/self/all/returns | trash 0.61, remove 0.32 | — | 0.1 | 
- 테스트용구슬1호 | instant/now/self/ally/returns | create 0.32, trash 0.16 | — | 0.2 | 애매 규칙상 입력 불가
- 123456789 | instant/now/one/all/returns | money 0.32 | — | 0.6 | 애매 규칙상 입력 불가
- 물음표느낌표 | instant/now/one/all/returns | peek 0.55 | — | 0.3 | 
- 무지개빛총공격 | instant/now/wide/all/returns | damage 0.99 | — | 3.2 | 
- 내일월요일 | instant/delayed/self/all/returns | peek 0.70 | — | 0.4 | 
- 칼퇴근 | instant/now/self/ally/returns | money 0.24, tempo 0.24, control 0.14 | — | 0.7 | 애매
- 기가차드 | summon/now/one/ally/returns | money 0.36 | — | 2.1 | 애매
- 최후의만찬 | instant/now/wide/all/returns | damage 0.25 | risky, network | 3.1 | 애매
- 갓난아기주먹 | instant/now/one/ally/returns | damage 0.88 | — | 0.5 | 
- 핵폭탄급방귀 | instant/now/around/all/used_up | damage 0.75 | — | 3.0 | 
- 제로수렴 | instant/delayed/wide/all/returns | remove 0.19, recycle 0.16, control 0.12 | — | 2.5 | 애매
- 무한대발산 | lasting/ongoing/wide/all/returns | amplify 0.72 | scaling | 4.0 | 
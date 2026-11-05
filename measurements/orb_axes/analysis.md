## A. 같은 입력 3번 (한국어)
| 축 | 평균 흔들림(최대-최소) | 흔들림 0.15↑ 비율 | 0.5선을 넘나든 비율 |
|---|---|---|---|
| damage | 0.018 | 0% | 0% |
| guard | 0.013 | 0% | 2% |
| heal | 0.010 | 0% | 0% |
| money | 0.011 | 0% | 0% |
| harvest | 0.010 | 0% | 0% |
| grow | 0.009 | 0% | 0% |
| buff | 0.013 | 0% | 2% |
| debuff | 0.017 | 0% | 0% |
| control | 0.018 | 0% | 2% |
| remove | 0.013 | 0% | 2% |
| transform | 0.012 | 0% | 0% |
| draw | 0.012 | 0% | 0% |
| recycle | 0.014 | 0% | 0% |
| trash | 0.009 | 0% | 0% |
| peek | 0.012 | 0% | 0% |
| tempo | 0.009 | 0% | 0% |
| energy | 0.009 | 0% | 0% |
| scaling | 0.018 | 0% | 2% |
| risky | 0.011 | 0% | 0% |
| random | 0.016 | 0% | 0% |
| network | 0.016 | 0% | 0% |
noul 전체 0.5선 넘나듦: 5/1176 = 0.4%

| 선택 축 | 1순위가 3번 중 달라진 이름 수 | 평균 1순위 확률 |
|---|---|---|
| role | 1/56 | 0.68 |
| timing | 2/56 | 0.72 |
| range | 2/56 | 0.69 |
| side | 4/56 | 0.75 |
| persist | 4/56 | 0.71 |

## B. 미리 적어 둔 기대값과 일치 (한국어 3회 평균 / 영어)
| 기대 | 한국어 일치 | 영어 일치 |
|---|---|---|
| +buff | 1/3 | 3/3 |
| +control | 1/1 | 1/1 |
| +damage | 9/9 | 8/9 |
| +debuff | 2/2 | 2/2 |
| +draw | 1/1 | 1/1 |
| +grow | 2/2 | 2/2 |
| +guard | 4/4 | 3/4 |
| +harvest | 2/2 | 2/2 |
| +heal | 2/2 | 2/2 |
| +money | 4/4 | 4/4 |
| +peek | 0/3 | 2/3 |
| +random | 2/2 | 2/2 |
| +recycle | 1/1 | 1/1 |
| +remove | 2/2 | 2/2 |
| +risky | 1/1 | 1/1 |
| +scaling | 2/2 | 2/2 |
| +tempo | 0/1 | 1/1 |
| +transform | 2/2 | 2/2 |
| -damage | 9/9 | 9/9 |
| -guard | 3/3 | 3/3 |
| -heal | 4/4 | 4/4 |
| -money | 5/5 | 5/5 |
| =persist | 6/6 | 6/6 |
| =range | 7/7 | 6/7 |
| =role | 8/8 | 8/8 |
| =timing | 3/4 | 4/4 |
**전체: 한국어 83/90 = 92%, 영어 86/90 = 96%**

한국어에서 어긋난 것:
- 독 (Poison) =timing=ongoing|delayed → 실제 now
- 나침반 (Compass) +peek → 실제 0.44
- 수정 구슬 (Crystal Ball) +peek → 실제 0.43
- 시계 (Clock) +tempo → 실제 0.41
- 깃발 (Banner) +buff → 실제 0.33
- 도서관 (Library) +peek|draw → 실제 0.17
- 대장장이 (Blacksmith) +buff|transform|money → 실제 0.45

## C. 이름마다 켜진 동사 수 (0.5 이상, 한국어 평균)
개수별 이름 수: {0: 10, 1: 13, 2: 25, 3: 5, 4: 2, 5: 1}
동사가 하나도 안 켜진 이름: 순간이동, 나침반, 수정 구슬, 모닥불, 깃발, 낡은 신발, 도서관, 대장장이, 새로운 시작, 피리
4개 이상 켜진 이름: 함정(damage,guard,debuff,control); 가시덤불(damage,guard,grow,debuff,control); 블랙홀(damage,control,remove,draw)
동사 1순위 확률 평균 0.74, 중앙값 0.82, 0.3 미만 3개

## D. 서로 겹치는 축 (이름 56개에서 상관 0.6 이상)
- heal ~ energy: 0.76
- damage ~ remove: 0.74
- harvest ~ grow: 0.74
- risky ~ random: 0.66
- heal ~ buff: 0.57
- debuff ~ control: 0.57
- grow ~ scaling: 0.55
- remove ~ trash: 0.46

선택 축 분포 (한국어 1순위)
- role: {'instant': 25, 'lasting': 10, 'build': 12, 'summon': 5, 'move': 4}
- timing: {'now': 38, 'trigger': 5, 'ongoing': 10, 'delayed': 3}
- range: {'line': 5, 'self': 30, 'around': 20, 'wide': 1}
- side: {'enemy': 12, 'ally': 20, 'land': 24}
- persist: {'returns': 38, 'stays': 11, 'used_up': 7}

## E. 한국어 vs 영어 판정 일치 (이름×축, 0.5 기준)
noul 평균 일치: 98.0% | 가장 낮은 축: damage 95%, buff 96%, draw 96%, recycle 96%
- role 1순위 일치: 50/56
- timing 1순위 일치: 51/56
- range 1순위 일치: 47/56
- side 1순위 일치: 45/56
- persist 1순위 일치: 52/56
평균 절대차(ko 3회평균 vs en): 0.037

## F. noul 값 분포 (전체 이름×축)
0~.2 / .2~.4 / .4~.6 / .6~.8 / .8~1 : [897, 147, 48, 42, 42]

## 이름별 결과 (한국어 3회 평균): 켜진 동사(≥0.35) | 역할/시점/범위/대상/지속 | 힘
- 화염검 (Flame Sword): damage 0.91, remove 0.48 | instant/now/line/enemy/returns | 힘 2.4
- 방패 (Shield): guard 0.98, control 0.47 | lasting/trigger/self/ally/returns | 힘 1.1
- 치유의 샘 (Healing Spring): heal 0.98, energy 0.85, buff 0.55 | lasting/ongoing/around/ally/returns | 힘 2.1
- 금화 주머니 (Bag of Gold Coins): money 0.96, draw 0.55, scaling 0.37 | instant/ongoing/self/ally/returns | 힘 1.0
- 곡괭이 (Pickaxe): harvest 0.88, draw 0.56 | instant/now/self/land/returns | 힘 0.9
- 씨앗 (Seed): grow 0.97, scaling 0.76, harvest 0.69, recycle 0.42 | build/delayed/self/land/stays | 힘 0.7
- 텃밭 (Vegetable Garden): grow 0.96, harvest 0.81, scaling 0.37 | build/ongoing/around/land/stays | 힘 0.7
- 성벽 (City Wall): guard 0.98, control 0.62 | build/now/line/land/stays | 힘 2.0
- 병사 (Soldier): damage 0.79, guard 0.61 | summon/now/self/ally/returns | 힘 0.9
- 순간이동 (Teleport): — | move/now/self/ally/returns | 힘 2.5
- 시한폭탄 (Time Bomb): damage 0.88, remove 0.74, risky 0.73, random 0.44 | instant/delayed/around/land/used_up | 힘 2.1
- 독 (Poison): debuff 0.84, damage 0.75, risky 0.47 | instant/now/self/enemy/returns | 힘 1.4
- 함정 (Trap): control 0.92, damage 0.72, guard 0.64, debuff 0.58, risky 0.48 | build/trigger/around/enemy/stays | 힘 0.9
- 폭풍 (Storm): damage 0.71, random 0.58, control 0.42, remove 0.37 | instant/now/around/land/returns | 힘 2.8
- 화살 (Arrow): damage 0.85 | instant/now/line/enemy/returns | 힘 0.9
- 눈덩이 (Snowball): control 0.75, scaling 0.71, debuff 0.54 | build/now/self/enemy/returns | 힘 0.8
- 도박 (Gambling): random 0.96, risky 0.92, money 0.52 | instant/now/self/ally/returns | 힘 0.9
- 저주 (Curse): debuff 0.95, risky 0.92, damage 0.61 | lasting/ongoing/self/enemy/returns | 힘 1.9
- 얼음 (Ice): control 0.91, debuff 0.76, guard 0.48, damage 0.39 | instant/now/around/land/returns | 힘 1.3
- 나침반 (Compass): peek 0.44 | move/now/self/ally/returns | 힘 1.1
- 수정 구슬 (Crystal Ball): peek 0.43 | instant/now/self/land/returns | 힘 1.5
- 부메랑 (Boomerang): recycle 0.97, damage 0.69, draw 0.68 | instant/now/line/enemy/returns | 힘 1.1
- 자석 (Magnet): draw 0.93, control 0.59 | move/ongoing/around/land/returns | 힘 1.2
- 파쇄기 (Shredder): remove 0.91, damage 0.91, trash 0.40 | instant/now/around/land/returns | 힘 2.6
- 폭죽 (Firework): damage 0.69, random 0.58, remove 0.35 | instant/now/around/enemy/used_up | 힘 1.5
- 포션 (Potion): energy 0.87, heal 0.84, buff 0.73 | instant/now/self/ally/used_up | 힘 1.0
- 망루 (Watchtower): guard 0.90, peek 0.54 | build/ongoing/around/land/stays | 힘 1.4
- 거울 (Mirror): transform 0.82, peek 0.57, recycle 0.38 | instant/now/self/enemy/returns | 힘 1.6
- 시계 (Clock): recycle 0.52, tempo 0.41, control 0.37 | lasting/delayed/wide/land/returns | 힘 1.2
- 연금술 (Alchemy): transform 0.93, scaling 0.37, debuff 0.35 | instant/now/self/land/returns | 힘 2.4
- 이자 (Interest): scaling 0.85, money 0.78, grow 0.54, recycle 0.38 | lasting/ongoing/self/ally/returns | 힘 0.9
- 낮잠 (Nap): energy 0.83, control 0.71 | lasting/now/self/ally/returns | 힘 0.4
- 모닥불 (Campfire): damage 0.38 | build/ongoing/around/land/stays | 힘 0.8
- 벌 떼 (Bee Swarm): network 0.76, scaling 0.62, damage 0.60, grow 0.56 | summon/now/around/enemy/returns | 힘 1.8
- 산사태 (Landslide): damage 0.72, random 0.61, control 0.58, remove 0.55, scaling 0.37, debuff 0.35 | instant/now/around/land/returns | 힘 2.5
- 깃발 (Banner): — | build/now/self/land/stays | 힘 1.0
- 전쟁 북 (War Drum): damage 0.67, buff 0.66 | instant/now/around/enemy/returns | 힘 1.8
- 안개 (Fog): debuff 0.67, guard 0.54 | lasting/now/around/land/returns | 힘 1.3
- 부적 (Amulet): guard 0.80, random 0.54, buff 0.50 | lasting/trigger/self/ally/used_up | 힘 1.4
- 수박 (Watermelon): grow 0.75, harvest 0.43 | instant/now/self/land/stays | 힘 0.7
- 베개 (Pillow): energy 0.66, control 0.63 | build/now/self/ally/returns | 힘 0.4
- 낡은 신발 (Old Shoe): recycle 0.47 | move/now/self/ally/returns | 힘 0.3
- 상인 (Merchant): money 0.95, scaling 0.43, draw 0.43 | summon/now/self/ally/returns | 힘 1.0
- 도서관 (Library): — | build/now/self/land/stays | 힘 1.5
- 대장장이 (Blacksmith): transform 0.45, buff 0.45, damage 0.40 | summon/now/self/ally/returns | 힘 1.3
- 번개 (Lightning): damage 0.79 | instant/now/line/enemy/returns | 힘 2.3
- 운석 (Meteor): damage 0.84, remove 0.58, random 0.56 | instant/now/around/land/used_up | 힘 2.8
- 지진 (Earthquake): damage 0.83, random 0.62, remove 0.61, control 0.42 | instant/now/around/land/returns | 힘 2.9
- 불사조 (Phoenix): recycle 0.91, heal 0.87, damage 0.47, scaling 0.45, risky 0.36 | summon/trigger/self/ally/returns | 힘 3.8
- 가시덤불 (Thorn Bush): guard 0.84, control 0.69, debuff 0.63, damage 0.62, grow 0.53 | build/trigger/around/land/stays | 힘 1.0
- 투명 망토 (Invisibility Cloak): guard 0.52 | lasting/ongoing/self/ally/returns | 힘 1.7
- 양봉장 (Apiary): grow 0.85, scaling 0.61, harvest 0.59, draw 0.51, money 0.39 | build/ongoing/self/land/stays | 힘 1.2
- 새로운 시작 (A Fresh Start): — | instant/now/self/ally/used_up | 힘 0.9
- 복권 (Lottery Ticket): random 0.97, risky 0.92, money 0.68 | instant/now/self/ally/used_up | 힘 1.0
- 피리 (Flute): buff 0.40 | instant/now/around/ally/returns | 힘 0.8
- 블랙홀 (Black Hole): draw 0.94, control 0.81, remove 0.77, damage 0.73, scaling 0.49, debuff 0.40 | lasting/now/around/land/returns | 힘 4.0
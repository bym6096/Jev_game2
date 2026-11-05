## 1. 안정성 (3번 반복, 339개)
| 축 | 1순위가 바뀐 이름 | (v2 같은 축) |
|---|---|---|
| role | 10/339 | 9/318 |
| timing | 7/339 | 6/318 |
| trigger | 2/339 | 6/318 |
| range | 17/339 | 25/318 |
| material | 10/339 | 11/318 |
| bagfate | 6/339 | 12/318 |
| bagfate2 | 7/339 | —/318 |
| verb | 28/339 | 27/318 |
| 지속 기간 v2 | 35/339 | 37/318 |
| 지속 기간 A | 31/339 | — |
| 지속 기간 B | 42/339 | — |
| 지속 기간 S | 34/339 | — |

## 2. 지속 기간 문구 4가지 비교
| 문구 | 전체 일치 | 스테이지 기대 | 몇 턴 기대 | 즉시 기대 | 런/영구 기대(건물 등) | 영구 기대 | 기존256 중 스테이지 | 영구 | 런 | 시전(cast)인데 런·영구 |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 | 39/43 | 7/11 | 7/7 | 6/6 | 14/14 | 4/4 | 4 (2%) | 68 (27%) | 55 | 78/200 (39%) |
| A | 41/43 | 9/11 | 7/7 | 6/6 | 14/14 | 4/4 | 4 (2%) | 8 (3%) | 13 | 6/200 (3%) |
| B | 21/43 | 9/11 | 5/7 | 6/6 | 1/14 | 0/4 | 58 (23%) | 3 (1%) | 0 | 1/200 (0%) |
| S | 33/43 | 7/11 | 6/7 | 4/6 | 11/14 | 4/4 | 107 (42%) | 1 (0%) | 39 | 24/200 (12%) |

분포 (기존 256개):
- v2: {'forever': 68, 'turns': 55, 'instant': 74, 'run': 55, 'stage': 4}
- A: {'forever': 8, 'instant': 158, 'turns': 73, 'run': 13, 'stage': 4}
- B: {'stage': 58, 'instant': 156, 'turns': 39, 'forever': 3}
- S: {'run': 39, 'turns': 95, 'stage': 107, 'instant': 14, 'forever': 1}

스테이지 기대 이름별 (v2 / A / B / S):
- 야영지 (기대 stage): stage 0.85 / stage 0.90 / stage 0.60 / run 2.8
- 진지 (기대 stage): run 0.61 / stage 0.56 / stage 0.57 / run 2.7
- 포위전 (기대 stage): stage 0.93 / stage 0.90 / stage 0.49 / stage 1.8
- 방어진 (기대 stage): run 0.55 / run 0.35 / stage 0.40 / stage 2.4
- 축제 (기대 stage): stage 0.44 / stage 0.37 / stage 0.39 / turns 1.5
- 폭우 (기대 stage|turns): stage 0.69 / stage 0.57 / instant 0.51 / turns 1.2
- 가뭄 (기대 stage|turns): stage 0.63 / stage 0.59 / stage 0.52 / stage 2.1
- 한파 (기대 stage|turns): stage 0.69 / stage 0.54 / turns 0.57 / stage 1.5
- 장마 (기대 stage|turns): stage 0.77 / stage 0.78 / turns 0.50 / stage 1.6
- 결계 (기대 stage|turns): run 0.43 / stage 0.41 / stage 0.60 / run 2.7
- 사기충천 (기대 stage|turns): instant 0.39 / instant 0.54 / instant 0.43 / stage 1.5
- 폭우 (기대 stage|turns): stage 0.69 / stage 0.57 / instant 0.51 / turns 1.2
- 가뭄 (기대 stage|turns): stage 0.63 / stage 0.59 / stage 0.52 / stage 2.1
- 한파 (기대 stage|turns): stage 0.69 / stage 0.54 / turns 0.57 / stage 1.5
- 장마 (기대 stage|turns): stage 0.77 / stage 0.78 / turns 0.50 / stage 1.6
- 결계 (기대 stage|turns): run 0.43 / stage 0.41 / stage 0.60 / run 2.7
- 사기충천 (기대 stage|turns): instant 0.39 / instant 0.54 / instant 0.43 / stage 1.5

어긋난 것 (각 문구):
- v2: 진지→run(기대 stage); 방어진→run(기대 stage); 결계→run(기대 stage|turns); 사기충천→instant(기대 stage|turns)
- A: 방어진→run(기대 stage); 사기충천→instant(기대 stage|turns)
- B: 폭우→instant(기대 stage|turns); 사기충천→instant(기대 stage|turns); 주문→instant(기대 turns); 불길→instant(기대 turns|stage); 마을→stage(기대 run|forever); 다리→instant(기대 run|forever); 우물→stage(기대 run|forever); 요새→stage(기대 run|forever); 성벽→stage(기대 run|forever); 오두막→stage(기대 run|forever); 제재소→stage(기대 run|forever); 대장간→stage(기대 run|forever); 망루→stage(기대 run|forever); 텃밭→stage(기대 run|forever); 은행→instant(기대 run|forever); 석상→stage(기대 run|forever); 평생→stage(기대 run|forever); 영원→stage(기대 forever); 불멸→stage(기대 forever); 영구기관→stage(기대 forever); 무한지속→stage(기대 forever); 영구빙결→stage(기대 forever|run)
- S: 야영지→run(기대 stage); 진지→run(기대 stage); 축제→turns(기대 stage); 결계→run(기대 stage|turns); 최면→stage(기대 turns); 다리→stage(기대 run|forever); 제재소→stage(기대 run|forever); 은행→stage(기대 run|forever); 즉사→turns(기대 instant); 운석→turns(기대 instant)

## 3. 발동 조건·시점 (합친 구조)
- trigger 분포(기존 256): {'none': 245, 'hit': 4, 'death': 4, 'approach': 3}
- timing 분포: {'now': 215, 'repeating': 24, 'delayed': 17}
- 조건이 있는(≥0.5) 이름: 흡혈→hit 0.82, 데미지반사→hit 0.99, 확정치명타→hit 0.52, 자동부활→death 0.97, 영혼수확자→death 0.77, 윤회→death 0.63, 바나나껍질→approach 0.74, 방패→hit 0.56, 함정→approach 0.98, 불사조→death 0.66, 가시덤불→approach 0.70
- 사전 기대 6개: 데미지반사→hit 0.99(기대 hit) ✓, 자동부활→death 0.97(기대 death) ✓, 함정→approach 0.98(기대 approach) ✓, 압정→none 0.51(기대 approach) ✗, 가시덤불→approach 0.70(기대 approach|hit) ✓, 동귀어진→none 0.77(기대 death|hit) ✗

## 4. 범위 (자신+하나 → 단일)
- 바뀐 이름 17/339 (v2: 25/318). 그중 대상이 원래 자기 자신인 동사 5개 → 실질 영향 12개
- 분포(기존 256): {'single': 165, 'around': 44, 'wide': 35, 'line': 12}

## 5. 구슬의 운명: 기존 문구 vs 자동 문구 재작성
- bagfate: 사전 기대 11/11 | 분포(기존 256) {'returns': 236, 'used_up': 16, 'passive': 4} | passive 이름: 데미지반사, 상태이상면역, 부적, 투명 망토
  - 부적 passive 0.44 | 상태이상면역 passive 0.77
- bagfate2: 사전 기대 11/11 | 분포(기존 256) {'returns': 230, 'used_up': 17, 'passive': 9} | passive 이름: 무적, 데미지반사, 자동부활, 상태이상면역, 공격속도상한돌파, 열등감, 젖산축적, 운명의데스티니, 부적
  - 부적 passive 0.66 | 상태이상면역 passive 0.83

## 6. 회귀 확인: v2에서 맞던 축이 그대로인가 (사전 기대)
- material: 43/44 (v2: 43/44)
- role: 41/42 (v2: 41/42)
- trigger: 4/6 (v2: 5/6)
- bagfate: 11/11 (v2: 10/11)
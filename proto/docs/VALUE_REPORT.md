# 가격 이상치 보고서

`python proto/value_report.py` 가 만든 파일(직접 고치지 않음). 모델 설명은 `proto/value.py` 머리말.

## 1. 환산율(엔진 상수에서 계산)

| 항목 | 값 | 뜻 |
|---|---|---|
| 적 체력 / 공격 / 현상금 | 33.0 / 2.5 / 6 | `CFG`의 ehp·eatk·bounty |
| 적 하나 처치 값 | 8.81 | 현상금 + 덜 맞는 체력 |
| 체력 1 | 0.38 | 정산액 × SAFETY ÷ 최대 체력 |
| 자원 1 | 0.60 | 판매율 0.3와 가공율 1.5의 혼합 |
| **마나 1당 표준 값어치(VPM)** | **2.00** | 정산액 ÷ (마나×턴) × 여유 1.2 |
| 처치 가치 상한 | 90.2 | 스테이지 평균 적 12.8마리 × 처치 값 × .8 |

## 2. 기대 사건 횟수(반응 구슬의 신뢰도)

| 사건 | 남은 기간 기대 횟수 |
|---|---|
| orb | 33.0 |
| orb_attack | 9.9 |
| orb_eco | 9.9 |
| orb_plant | 2.0 |
| orb_build | 4.0 |
| orb_summon | 2.6 |
| orb_defense | 3.3 |
| kill | 7.5 |
| harvest | 22.0 |
| hit | 4.4 |
| death | 1.5 |
| approach | 5.5 |

## 3. 풀 전체 분포

측정된 이름 364개. 놀이형 215 · 슬롯형 149.

| 판정 | 개수 | 비율 |
|---|---|---|
| 싸다(약한 가격) | 10 | 3% |
| 표준 | 258 | 71% |
| 비싸다 | 37 | 10% |

배율 중앙값 0.90, 10% 0.32, 90% 1.39, 최대 2.40.

## 4. 동사별 배율(첫 동사 기준 중앙값)

| 동사 | 개수 | 중앙값 | 최대 |
|---|---|---|---|
| drain | 1 | 1.25 | 1.25 |
| process | 8 | 1.19 | 1.52 |
| grow | 11 | 1.13 | 1.30 |
| control | 33 | 1.06 | 2.25 |
| harvest | 17 | 1.05 | 1.26 |
| damage | 89 | 1.03 | 2.25 |
| debuff | 30 | 1.03 | 2.40 |
| amplify | 6 | 0.95 | 1.20 |
| buff | 5 | 0.94 | 1.10 |
| tempo | 12 | 0.80 | 1.52 |
| energy | 7 | 0.80 | 1.12 |
| steal | 10 | 0.77 | 1.55 |
| create | 13 | 0.67 | 1.41 |
| heal | 10 | 0.62 | 1.35 |
| draw | 2 | 0.60 | 0.60 |
| recycle | 25 | 0.55 | 1.53 |
| money | 38 | 0.54 | 1.25 |
| guard | 22 | 0.38 | 1.20 |
| trash | 7 | 0.25 | 0.33 |
| peek | 8 | 0.15 | 0.60 |
| transform | 6 | 0.00 | 0.72 |
| remove | 4 | 0.00 | 0.00 |

## 5. 가장 싼 구슬(너무 센 후보) 상위

| 이름 | 역할 | 지속 | 동사 | 마나 | 값어치 | 배율 | 판정 |
|---|---|---|---|---|---|---|---|
| 가뭄 | cast | stage | debuff+damage | 4 | 57.7 | 2.40 | 싸다(약한 가격) |
| 고요한태풍 | cast | stage | control+damage | 4 | 53.9 | 2.25 | 싸다(약한 가격) |
| 어둠의다크 | cast | stage | damage+debuff | 4 | 53.9 | 2.25 | 싸다(약한 가격) |
| 차가운불꽃 | cast | stage | damage+control | 4 | 53.9 | 2.25 | 싸다(약한 가격) |
| 블랙홀 | cast | stage | control+draw | 4 | 47.8 | 1.99 | 싸다(약한 가격) |
| 불얼음번개독 | cast | stage | damage | 4 | 46.5 | 1.94 | 싸다(약한 가격) |
| 폭우 | cast | stage | damage | 4 | 46.5 | 1.94 | 싸다(약한 가격) |
| 폭풍 | cast | stage | damage | 4 | 46.5 | 1.94 | 싸다(약한 가격) |
| 건조한해일 | cast | stage | damage | 3 | 31.7 | 1.76 | 싸다(약한 가격) |
| 네크로노미콘 | cast | stage | damage | 3 | 31.7 | 1.76 | 싸다(약한 가격) |
| 영혼수확자 | cast·death | instant | steal | 5 | 15.5 | 1.55 | 표준 |
| 영원한불꽃 | cast | stage | recycle+damage | 4 | 36.7 | 1.53 | 표준 |
| 연금술 | cast | instant | process | 6 | 18.3 | 1.52 | 표준 |
| 오버클럭 | cast | stage | tempo+buff | 4 | 36.4 | 1.52 | 표준 |
| 중력파 | cast | instant | damage+control | 6 | 18.0 | 1.50 | 표준 |

## 6. 가장 비싼 구슬 하위

| 이름 | 역할 | 지속 | 동사 | 마나 | 값어치 | 배율 | 판정 |
|---|---|---|---|---|---|---|---|
| 데미지반사 | cast·hit | stage | guard+damage | 1 | 0.0 | 0.00 | 최소 가격 |
| 뜨거운얼음 | cast | turns | transform | 1 | 0.0 | 0.00 | 최소 가격 |
| 무적 | cast | stage | guard | 1 | 0.0 | 0.00 | 최소 가격 |
| 무한지속 | build | run | recycle | 1 | 0.0 | 0.00 | 최소 가격 |
| 부적 | cast | turns | guard | 1 | 0.0 | 0.00 | 최소 가격 |
| 상태이상면역 | cast | stage | guard+buff+remove | 1 | 0.0 | 0.00 | 최소 가격 |
| 세계의법칙 | cast | run | transform | 1 | 0.0 | 0.00 | 최소 가격 |
| 수호신 | summon | stage | guard | 1 | 0.0 | 0.00 | 최소 가격 |
| 용기 | cast | run | buff | 1 | 0.0 | 0.00 | 최소 가격 |
| 자동부활 | cast·death | run | recycle+heal | 1 | 0.0 | 0.00 | 최소 가격 |
| 젖은수건 | cast | instant | remove | 1 | 0.0 | 0.00 | 최소 가격 |
| 제로수렴 | cast | instant | remove | 1 | 0.0 | 0.00 | 최소 가격 |
| 지우개 | cast | instant | remove | 1 | 0.0 | 0.00 | 최소 가격 |
| 질서있는혼돈 | cast | stage | transform | 1 | 0.0 | 0.00 | 최소 가격 |
| 카타르시스 | cast | instant | remove | 1 | 0.0 | 0.00 | 최소 가격 |

## 7. 마나로 못 갚는 놀이형(마나 최대 8에 눌림)

| 이름 | 동사 | 마나 | 값어치 | 못 갚은 몫(골드) |
|---|---|---|---|---|
| 연금술 | process | 6 | 18.3 | 6.3 |
| 중력파 | damage+control | 6 | 18.0 | 6.0 |
| 영혼수확자 | steal | 5 | 15.5 | 5.5 |
| 무한관통 | damage | 5 | 12.7 | 2.7 |
| 뇌진탕 | damage+debuff | 5 | 12.5 | 2.5 |
| 도파민과다 | amplify | 5 | 12.0 | 2.0 |
| 아포칼립스 | damage | 4 | 9.7 | 1.7 |
| 눈먼주시자 | debuff+peek | 4 | 9.7 | 1.7 |
| 진공붕괴 | damage | 4 | 9.6 | 1.6 |
| 절망 | debuff | 4 | 9.4 | 1.4 |
| 반물질 | damage | 5 | 11.2 | 1.2 |
| 중성자별 | damage | 5 | 11.2 | 1.2 |
| 장작 | energy+harvest | 5 | 11.2 | 1.2 |
| 가시덤불 | control+guard | 4 | 9.0 | 1.0 |
| 현자의돌 | money | 2 | 5.0 | 1.0 |

## 8. 시너지 견본(손으로 만든 구슬)

| 이름 | 역할 | 지속 | 동사 | 마나 | 값어치 | 배율 | 판정 |
|---|---|---|---|---|---|---|---|
| 공격 반응(스테이지) | cast·orb_attack | stage | money | 3 | 29.7 | 1.65 | 싸다(약한 가격) |
| 처치 보상(스테이지) | cast·kill | stage | money | 3 | 30.0 | 1.67 | 싸다(약한 가격) |
| 수확 보너스(스테이지) | cast·harvest | stage | harvest | 3 | 26.4 | 1.47 | 표준 |
| 공격 반응(즉발 2회) | cast·orb_attack | instant | damage | 4 | 8.1 | 1.02 | 표준 |
| 식물 깃발(건물) | build·orb_plant | run | money | 2 | 12.9 | 0.72 | 표준 |
| 복수의 탑(피격 반응 건물) | build·hit | run | damage | 3 | 15.4 | 0.63 | 표준 |
| 불꽃(화상 3) | cast | instant | burn | 1 | 2.5 | 1.25 | 표준 |
| 화염병(화상, 3턴) | cast | turns | burn | 4 | 7.8 | 0.97 | 표준 |
| 불쏘시개(화상 +18%) | cast | stage | buff | 1 | 1.5 | 0.25 | 최소 가격 |
| 황금 장갑(수입 +18%) | cast | stage | buff | 3 | 15.8 | 0.88 | 표준 |
| 함성(피해 +24%, 3턴) | cast | instant | buff | 2 | 4.3 | 1.08 | 표준 |
| 마법사의 탑(건물 +22%) | build | run | buff | 1 | 4.8 | 0.38 | 최소 가격 |
| 부활의 부적(죽음 반응) | cast·death | instant | heal | 5 | 15.4 | 1.54 | 표준 |

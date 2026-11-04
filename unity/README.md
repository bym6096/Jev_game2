# 빈 구슬 공방 — 유니티 이식

웹 장난감(`toys/card-forge/`)을 유니티로 옮긴 것입니다. 규칙과 Jev 호출은 그대로 두고(서버가 맡음), **화면과 입력만 유니티로 다시 만들었습니다.**
구슬은 RG Poly / EmaceArt **Creator Bundle** 같은 로우폴리 에셋과 한 장면에 놓이도록 만들었습니다(아래 "에셋과 어우러지게").

```
unity/
  README.md                      이 문서
  JevOrbs/                       유니티 프로젝트 (Unity 2022.3 LTS 기준, Unity 6에서도 열림)
    Packages/manifest.json       URP · Newtonsoft.Json · uGUI
    Assets/JevOrbs/              ← 이 폴더만 떼어서 다른 프로젝트에 넣어도 됩니다
      Scripts/Runtime/           게임 코드 (JevOrbs.Runtime)
      Scripts/URP/               URP 후처리 (URP가 있을 때만 컴파일, JevOrbs.URP)
      Scripts/Editor/            Jev > Setup 메뉴 (JevOrbs.Editor)
      Resources/JevRules.json    규칙 표 (파이썬에서 뽑은 것, 손으로 고치지 않음)
      Resources/JevSamples.json  견본 구슬 44개 (서버 없이도 볼 수 있음)
```

## 시작하기

### 방법 A — 새 프로젝트에 넣기 (추천: 에셋 번들과 같은 프로젝트에서 쓸 때)
1. Unity Hub에서 **Universal 3D** 템플릿으로 새 프로젝트를 만듭니다.
2. `Window > Package Manager > + > Add package by name` → `com.unity.nuget.newtonsoft-json` (이미 있으면 건너뜀).
3. 이 저장소의 `unity/JevOrbs/Assets/JevOrbs` 폴더를 새 프로젝트의 `Assets/` 아래로 복사합니다.
4. 잠시 컴파일을 기다리면 `Jev > Setup`이 저절로 한 번 돌아 장면 `Assets/JevOrbs/Scenes/JevOrbs.unity`를 만듭니다. 그 장면을 열고 ▶.

### 방법 B — 이 프로젝트를 그대로 열기
1. Unity Hub → Add → `unity/JevOrbs` 폴더 선택 (2022.3 LTS 이상).
2. 처음엔 URP 에셋이 없어서 기본 셰이더로 보입니다. 메뉴 **Jev > Setup**을 누르면 안내 창이 뜹니다:
   `Project 창 우클릭 > Create > Rendering > URP Asset (with Universal Renderer)` → `Edit > Project Settings > Graphics`와 `Quality`에 그 에셋을 지정 → `Jev > Setup` 한 번 더.
3. `Jev > 장면 열기` → ▶.

### 서버 켜기 (구슬을 실제로 새기려면)
Jev 키는 게임 안에 넣지 않습니다. 웹 장난감과 **같은 서버**를 씁니다.
```bash
cd toys/card-forge
export JEV_API_KEY=여기에_키      # Windows PowerShell: $env:JEV_API_KEY="여기에_키"
python3 server.py                 # Windows: python server.py
```
유니티 화면 오른쪽 아래 칸의 서버 주소가 `http://localhost:8000`인지 확인합니다. Vercel에 배포했다면 그 주소를 넣으면 되고, `ACCESS_CODE`를 걸었다면 옆 칸에 코드를 넣습니다.
서버가 없으면 견본 44개를 이름으로 불러볼 수 있는 상태로 돌아갑니다(웹과 같은 동작).

## 무엇이 옮겨졌나
| 웹 | 유니티 |
|---|---|
| 규칙 표 (`forge.py`, `fragments.py`) | `export_unity.py` → `JevRules.json` → `Rules` (표는 한 곳에서만 고침) |
| 이름 규칙 `checkName` | `NameRules.Check` (13개 언어, 숫자·기호 금지, 글자 수) |
| `onBlank`·`maybeVariant`·`cleanCard` | `CardRules.OnBlank`·`MaybeVariant`·`Clean` (마나 재계산, 파손, 12% 가챠, 저장 데이터 정리) |
| `fetch("forge")`, `fetch("hero")` | `ForgeClient` (UnityWebRequest) |
| localStorage | `SaveStore` (파일, WebGL은 PlayerPrefs) |
| CSS 구슬 | `OrbView` + `OrbMeshFactory` (3D 구슬) |
| 이름 새기기 `engrave()` | `Engraving` (두 줄 나눔, 구슬 표면을 따라 글자를 감음, 빈 카드가 미리 적은 말은 흐리게) |
| 호버 팝업 | `JevGame`의 툴팁 (터치는 무대의 큰 구슬을 누르면 열림) |
| 덱 → 주인공 | `JevGame` 오른쪽 패널 (`/hero`, 같은 덱은 다시 묻지 않음) |

구슬 표현은 웹과 같은 규칙입니다: **색**=Jev가 정한 색, **크기**=마나, **재질**=빈 구슬 등급(낡은=거친 돌, 평범한=유리, 깨끗한=수정, 금박=금빛 띠), **안쪽 무늬**=속성 계열 7가지, **파손**=금이 가서 벌어진 구슬과 붉게 빛나는 속, **수상한 낙서**=회색 구슬+물결 취소선, **덱에 든 구슬**=노란 고리.

## 에셋과 어우러지게
로우폴리 팩들(Creator Bundle 포함)은 대체로 **URP + 납작한 면(플랫 셰이딩) + 채도 높은 중간 밝기 색 + 따뜻한 햇빛**으로 보여 줍니다. 구슬이 그 안에서 겉돌지 않도록 한 곳(`LowPolyStyle`)에서 처리합니다.

- **면이 각진 구슬**: 20면체를 한 번 쪼갠 80면 구슬을 면마다 법선을 따로 줘서(플랫 셰이딩) 만들고, 이름마다 꼭짓점을 조금씩 흔들어 구슬마다 다른 원석처럼 보이게 했습니다. 낡은 구슬은 많이 울퉁불퉁, 유리·수정·금박은 깔끔하게.
- **색 보정** `LowPolyStyle.Harmonize`: Jev가 정한 색의 색조는 그대로 두고 채도 0.34~0.90, 명도 0.40~0.96 범위로 당겨, 어두운 "밤" 구슬과 밝은 "해" 구슬이 같은 팔레트 안에 들어오게 합니다. (글자 색 결정은 보정 전 색의 밝기로 합니다.)
- **재질**: URP/Lit(없으면 Standard) 하나로 통일. 미세한 텍스처 대신 아주 약한 무늬(128×64)만 곱합니다. 금박은 금속+금 띠, 수정은 은은한 발광.
- **조명**: 따뜻한 햇빛+차가운 하늘빛 트라이라이트, 부드러운 그림자, 옅은 안개 (`LowPolyStyle.BuildLighting`). 장면에 있던 기본 Directional Light는 꺼집니다.
- **후처리** (URP일 때 자동): 약한 블룸, ACES 톤맵, 채도 +12, 비네트 (`Scripts/URP/JevUrpPostFx.cs`).
- **무대 배경(Diorama)**: 팩을 들이기 전에도 장면이 비지 않도록 둔 임시 바닥·언덕·받침대·선반입니다.

### 팩을 실제로 쓰기
1. 번들의 `.unitypackage`를 `Assets > Import Package > Custom Package`로 가져옵니다. 팩이 URP용이 아니라면 `Edit > Rendering > Materials > Convert Selected Built-in Materials to URP`.
2. **배경 바꾸기**: 장면의 `JevGame > JevWorld > Diorama` 아래 임시 바닥·언덕을 지우고, 팩의 지형/소품을 그 자리에 놓습니다. 구슬 무대는 월드 좌표 (−2.2, 0.45, 0), 선반은 (−2.2, −1.85) 아래로 두 줄(코드의 `StagePos`, `ShelfY`)입니다. 카메라는 가로 15.6칸이 항상 보이게 맞춰집니다.
3. **테마 소품 꽂기**: `Assets/JevOrbs/Resources/JevThemeDecor`(Jev > Setup이 만듦)를 열면 테마 10개의 빈 칸이 있습니다. 카드의 첫 번째 테마와 같은 칸의 프리팹이 무대 구슬 옆에 서고, 높이는 자동으로 맞춰집니다(`scale`, `euler`로 보정). 비어 있으면 간단한 임시 모양이 나옵니다. 번들에서 이렇게 짝지으면 어울립니다(제안일 뿐, 내용물은 직접 확인하세요):

| 테마 | 어울리는 팩 |
|---|---|
| 바다 | Pirate Island, Raft on the Desert |
| 기계 | Sci-Fi Arena 시리즈, Time Paradox Engine |
| 숲 | NatureForge, LumaGrove, TerraToon, Low Poly Tiny Forest |
| 죽음 | NecroPOLY, Gravefield, Graves Kit, Cemetery Statues |
| 신성 | Medieval Megapack, Low Poly Asia Pack, Free Fantasy Medieval Houses |
| 축제 | Cute Park Pack, Cartoon City |
| 일상 | Kitchen/Restaurant Megapack, Cute Dungeon Megapack |
| 우주 | CosmoKit (행성) |
| 음식 | Low Poly Food & Packaging, Food Pack |
| 추억 | Analog Memory / Rewind Memory (80~90년대 방) |

4. 구슬만 팩의 장면에 넣고 싶다면 `OrbView.Create(card, parent, localPos, small)`로 어디서든 구슬을 만들 수 있습니다(`JevGame`은 하나의 예시 장면일 뿐입니다).

## 글꼴
이름은 프로필 언어마다 다른 글꼴로 새깁니다. 우선순위: `Resources/JevFonts/<언어코드>.ttf`(예: `ko.ttf`, `ja.ttf`, `th.ttf`) → 컴퓨터에 깔린 글꼴.
데스크톱에서는 깔린 글꼴로 바로 보이지만, **모바일·WebGL에는 쓸 만한 시스템 글꼴이 없으니 TTF를 넣어야 합니다.** 웹 버전과 같은 글꼴(모두 Google Fonts, OFL):
ko Song Myung · en/es/fr/de/pt-BR IM Fell English · ja Shippori Mincho · zh-Hans ZCOOL XiaoWei · zh-Hant Noto Serif TC · vi EB Garamond · ru Cormorant Garamond · th Noto Serif Thai · ar Amiri. 화면 글씨(UI)는 `JevFonts/ui.ttf`가 있으면 그것을 씁니다. 글꼴 파일은 `Dynamic` 모드로 가져옵니다(기본값).

## 알려진 한계 (솔직하게)
- **이 환경에서는 유니티를 돌려 보지 못했습니다.** 코드는 문법 검사와 눈으로 읽는 검토만 했고, 첫 실행에서 컴파일 오류나 화면 어긋남이 나올 수 있습니다. 오류가 나면 Console 내용을 그대로 알려 주세요.
- 아랍어는 글자 연결·오른쪽→왼쪽 처리(shaping)를 하지 않아 모양이 깨집니다. 쓰려면 TextMeshPro + RTL 플러그인으로 `Engraving`을 바꿔야 합니다. 태국어는 글자를 하나씩 쪼개지 않고 한 줄로 새깁니다(겹쳐 쓰는 모음 때문).
- 글자는 레거시 `TextMesh`/`UI.Text`입니다(TextMeshPro 의존을 피하려고). 글자가 흐릿하면 `Engraving.FontPx`를 키우거나 TMP로 옮기세요.
- 구슬이 한 번에 많으면(진열장 300개) 느릴 수 있어 선반은 한 번에 16개씩 쪽 넘김으로 보입니다. 구슬마다 메시와 재질을 따로 만듭니다.
- 화면 배치는 16:9 가로 기준입니다(세로 화면은 비율만 맞춥니다).
- 새 Input System만 켠 프로젝트에서는 `InputSystemUIInputModule`을 자동으로 붙이는데, 직접 확인하지 못했습니다.
- 소리·진동·구슬 속성별 움직임은 아직 없습니다 (웹에도 없는 "다음 후보"였던 것).

## 규칙을 고친 뒤에는
파이썬 쪽(`forge.py`, `template.html`, `fragments.py`)이 기준입니다. 고친 뒤:
```bash
cd toys/card-forge
python3 export_unity.py          # JevRules.json / JevSamples.json 다시 만들기
python3 test_unity_export.py     # 웹과 어긋난 곳이 없는지 확인
python3 make_unity_metas.py      # 새 파일의 .meta 만들기 (이미 있는 것은 건드리지 않음)
```
`.meta` 파일은 **꼭 같이 커밋**하세요(GUID가 바뀌면 장면·에셋 연결이 끊깁니다).

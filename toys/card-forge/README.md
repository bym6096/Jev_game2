# 빈 카드 공방 (카드 만들기 장난감)

빈 카드에 이름을 쓰면 Jev가 이름을 읽고 한 번의 요청으로 카드를 만든다.

- 판정: 속성 40종(5계열 × 8) / 특수효과 64종(8계열 × 8) / 종류(공격·방어·기술) / 공격력·방어력(척도) / 힘의 크기 → 마나 / 테마 10종 중 최대 2개
- 속성(40개)과 효과(64개)는 각각 choice 질문 하나로 묻고 가장 높은 확률의 답을 쓴다. 계열은 카드 색 구분에만 쓴다(질문 17개를 한 요청에)
- 이름 규칙: 한 가지 언어만. 한국어 8자, 영어 14자, 중국어 4자, 일본어 6자(한중일은 공백 제외). 숫자·공백은 허용
- 사기 차단: 빈 카드의 마나 한계는 8. 힘이 너무 크면 마나가 넘쳐 "과부하·파손"
- 조작 차단: 이름이 명령이면 검문소 질문에 걸려 "수상한 낙서"
- 같은 이름은 같은 카드(서버가 저장해 재사용)

## PC에서 실행 (Windows PowerShell)
```
cd toys\card-forge
$env:JEV_API_KEY="여기에_키"
python server.py
```
그리고 브라우저에서 http://localhost:8000 을 연다. (macOS/Linux: `export JEV_API_KEY=...`)

키는 서버에만 있고 브라우저로 가지 않는다. 브라우저에서 Jev를 직접 부르면 CORS로 막힌다.

## 파일
- `forge.py`: Jev 요청 만들기와 카드 규칙
- `server.py`: 페이지 제공 + `POST /forge`
- `make_samples.py`, `samples.json`: 견본 30장 (서버 없이 열면 이것만 보임)
- `template.html` → `assemble.py` → `index.html`

## 인터넷에 배포 (Vercel, GitHub 연결)
1. https://vercel.com 에 GitHub 계정으로 가입
2. Add New → Project → `Jev_game2` 저장소 선택
3. **Root Directory**를 `toys/card-forge`로 지정
4. Environment Variables에 `JEV_API_KEY` = 키 입력. 남이 키를 쓰지 못하게 하려면 `ACCESS_CODE` = 원하는 암호도 추가
5. Deploy. 이후 GitHub에 push할 때마다 자동 재배포

페이지는 `/`, 카드 만들기는 `/forge`(= `/api/forge`). ACCESS_CODE를 넣었다면 처음 새길 때 한 번 묻고 브라우저에 기억한다.

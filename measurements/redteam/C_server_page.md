# 레드팀 C: 서버 / API / 페이지 악용 점검

대상: toys/card-forge (server.py, api/forge.py, api/hero.py, forge.py, template.html)
방법: 내 인스턴스(포트 8001, 가짜 call_jev)와 api 핸들러(포트 8002, 가짜 call_jev)를 따로 띄워 테스트.
실제 Jev 호출은 0회 (한도 150회 중). 기존 8000 서버에는 아무것도 보내지 않았다. .env.local은 열지 않았다.
프로젝트 파일은 수정하지 않았다. 테스트 서버 두 개는 내가 종료했다.

## 한 줄 요약

- 큰 문제는 세 가지다.
  1. 호출 제한이 없고, 이름 변형으로 캐시를 쉽게 피한다.
  2. 서버가 잘못된 요청에 응답 없이 연결을 끊고, 동시 요청에서 캐시 저장이 깨진다.
  3. 페이지가 숫자/색 필드를 esc() 없이 innerHTML에 넣어서, 저장된 카드가 오염되면 스크립트가 실행된다.
- 파일 읽기(경로 탐색), ACCESS_CODE 비교, 이름 문자 검사(프롬프트 주입 차단)는 잘 막혀 있다.

## 발견 표

| id | 심각도 | 무엇 | 재현 (한 줄) | 영향 |
|---|---|---|---|---|
| C1 | High | 요청 횟수 제한 없음. 이름 변형으로 캐시를 쉽게 피함 | `{"name":"화염검"}`, `"화 염 검"`, `"화  염  검"`, NFD로 쪼갠 "화염검", `Sword/sword/SWORD/sWord/swo-rd`를 차례로 보내면 모두 별도 Jev 호출 (10개 변형 = 호출 10번) | 반복문 하나로 Jev 비용을 무한히 쓰게 할 수 있음. 영어 14자는 대소문자만으로 2^14 변형, 한국어는 공백 개수만 바꿔도 무한 변형. `--lan` 이거나 Vercel 배포(캐시 자체가 없음)면 외부인이 키 비용을 씀 |
| C2 | High | 동시 요청 시 캐시 저장 경쟁. json.dump가 도는 중 dict가 바뀜 | 서로 다른 새 이름 40~80개를 동시에 POST. 서버 로그에 `RuntimeError: dictionary changed size during iteration` 79건, 80개 중 66개가 응답 없이 연결 끊김 | Jev 비용은 이미 나갔는데 사용자는 응답을 못 받음. 파일을 "w"로 먼저 열어 비운 뒤 dump하므로, 실패 직후 서버가 꺼지면 forged_cache.json이 잘린 채 남고, 다음 시작에서 `except Exception: CACHE = {}` 로 캐시 전체가 조용히 사라짐. hero 캐시도 같은 구조 |
| C3 | High | XSS: 숫자·색 필드가 esc() 없이 innerHTML에 들어감 | localStorage `forge-collection-v3`에 `color:'red"><img src=x onerror=...>'` 카드를 넣고 새로고침하면 코드가 실행됨(확인: 탭 제목이 바뀜). `mana`, `attack`, `defense`, `effects[].value`에 `<img onerror>`를 넣어도 실행(확인) | 서버 JSON이나 localStorage가 오염되면 임의 JS 실행. 지금 서버가 만드는 값은 숫자/hex라 평소엔 안전. 하지만 `--lan`(http, 암호화 없음) 중간자, 배포 서버 침해, 다른 XSS로 저장된 카드는 영구히 남는다(300장 저장). 같은 출처의 `forge-code`(입장 코드)도 읽힘. 위치: cardHTML의 `--el:${color}`, `${c.mana}`, `${c.attack}`, `${c.defense}`, effectsHTML의 `${e.value}`, `${cap}`, `t${c.tier}` 클래스, heroHTML의 `${h.cards}` |
| C4 | Medium | 저장된 카드 하나가 이상하면 페이지 전체가 죽음 | localStorage 카드에 `tier:"x"`(또는 2.5), `themes` 없음, `effects`가 문자열/null 원소 → 새로고침하면 `cardHTML`에서 TypeError, 진열장 0장, 그 아래 코드(덱, 영웅 판정)도 실행 안 됨 | 복구 UI가 없어서 사용자가 개발자도구로 localStorage를 지워야 함. 로드 시 JSON.parse만 try/catch이고 카드 모양 검증이 없음 |
| C5 | Medium | 서버가 잘못된 요청에 응답 없이 연결을 끊음 (예외가 핸들러 밖으로) | `/forge`에 `{"name":null}`, `{"name":123}`, `{"name":["a"]}`, `[]`, `null`, 깨진 JSON, 잘못된 UTF-8 → 모두 `RemoteDisconnected`, 서버 콘솔에 traceback. `/hero`도 body가 리스트면 동일 | 400이 아니라 빈 응답. 페이지는 이를 "서버 없음"(online=false)으로 보고 오프라인 모드로 떨어질 수 있음. traceback은 서버 콘솔에만 나가고 클라이언트에는 안 나감(경로 유출 없음). api/forge.py, api/hero.py도 body가 dict가 아니면 같은 문제(Vercel은 500) |
| C6 | Medium | Content-Length 처리 허술: 음수/부족하면 연결이 매달림 | `Content-Length: -1` 또는 `100`인데 본문 5바이트만 보내고 대기 → 6초 넘게 응답 없음. `abc` → ValueError 후 끊김. `10^12` → MemoryError 후 끊김. 60MB 본문은 그대로 읽고 처리(0.1초, 200 OK) | ThreadingHTTPServer라 스레드 무제한. 소켓을 열어 두기만 해도 스레드/메모리 고갈(slowloris). 본문 크기 상한 없음 |
| C7 | Medium | 다른 웹사이트가 브라우저를 통해 몰래 호출 가능 (CSRF/DNS rebinding) | `Content-Type: text/plain`으로 `{"name":"..."}`를 보내도 200 (서버가 헤더를 안 봄). Origin/Host 검사 없음 | 로컬 서버(8000)를 켜 둔 채 악성 웹페이지를 열면, 그 페이지가 단순 요청으로 `localhost:8000/forge`를 계속 쏴 Jev 비용을 쓰게 함. 응답은 못 읽지만(CORS 헤더 없음) 비용은 발생 |
| C8 | Medium | 같은 새 이름이 동시에 오면 Jev를 여러 번 부르고 결과가 달라질 수 있음 | 같은 이름을 15개 동시 POST → 모두 200, Jev 호출 3번(가짜는 빨라서 3번. 실제는 지연이 길어 더 많을 것) | 비용 낭비. Jev가 같은 이름에 약간 다르게 답하면 두 응답이 다른 카드이고 마지막 것이 캐시를 덮어씀 → "같은 이름 같은 카드" 약속이 깨질 수 있음. 두 탭이나 더블클릭으로도 발생 |
| C9 | Medium | 캐시가 끝없이 커지고, 새 이름마다 파일 전체를 다시 씀. 공백으로 길이 제한 우회 | 공백만 다른 이름 300개 + 임의 이름 → 캐시 파일 113KB → 683KB. `"화"+" "*50000+"염"` 이 통과해 5만 자 키로 저장됨 | 디스크/CPU 증가가 O(n)씩 누적. 글자 수 검사가 공백을 세지 않아 한국어·중국어·일본어 길이 제한이 공백으로 우회됨. 본문 상한이 없으니 키 하나가 수 MB도 가능 |
| C10 | Low | api/forge.py 401 힌트가 키 끝 4자리와 길이를 응답에 실음 | Jev가 401을 돌려주게 하면(가짜로 확인) `(키가 거절됨. 서버가 받은 키 길이 29자, 끝 4자리 …WXYZ)` 출력 | ACCESS_CODE를 안 켜면 누구나 볼 수 있음. 키 일부 유출(4자리라 위험은 낮음). 502 경로는 Jev 응답 본문 200자도 그대로 전달 |
| C11 | Low | 입장 코드 시도 횟수 제한 없음, 비교가 상수시간 아님 | `body.get("code") != code` 로 비교, 반복 시도 가능 | 짧은 코드는 무차별 대입 가능. 타이밍 공격은 네트워크 지연 때문에 현실성 낮음. 유형 혼동은 안전 |
| C12 | Low | 숫자+스탯 단어 규칙이 영어에서 우회됨 | `attack2`, `mana5`, `hp99` 는 통과(`\b` 때문). 한국어 `공격5`는 막힘 | 카드 이름이 능력치처럼 읽혀 Jev 판정이 흔들릴 수 있음. 서버/JS 규칙은 같아서 서로 어긋나지는 않음 |
| C13 | Low | 이름이 아닌 값이 문자열로 바뀌어 통과 | api/forge.py: `{"name":null}` → "None", `{"name":true}` → "True" 카드가 만들어짐. 덱 `{"names":[null]}`, `[true]` 도 200 | 의도하지 않은 이름. 비용은 1회분. server.py는 `.strip()`에서 죽어서 이 문제는 없음(대신 C5) |
| C14 | Low | NFC/NFD 한글이 다른 카드로 처리됨 | NFD "화염검"(자모 8개)은 검사를 통과하고 별도 Jev 호출 | C1의 일부. 자모 길이로 세어 8자 제한에 걸려 쓸 수 있는 음절 수는 줄지만 변형은 가능. 유니코드 정규화 없음 |
| C15 | Low | 안전 헤더 없음 (CSP, nosniff, X-Frame-Options) | 응답 헤더 확인 | C3가 있을 때 CSP가 마지막 방어선이 될 텐데 없음. 클릭재킹도 막지 않음 |
| C16 | Low | 덱에 같은 카드 20장 허용, /hero 캐시 키에 중복 포함 | `{"names":["화염검"]*20}` → 200, 키가 다른 덱으로 취급됨 | 페이지는 중복을 못 넣지만 API는 가능. 호출 1번이라 증폭은 아님. 캐시 항목만 늘어남 |
| C17 | Low | 배포 시 정적 파일 노출 가능성 (확인 못 함, 점검 필요) | .vercelignore에 forged_cache.json, hero_cache.json, samples.json이 없음. Vercel이 루트 파일을 정적으로 서빙하면 내려받을 수 있음 | 비밀은 없음(.env.local은 제외됨). 캐시 내용이 공개될 수 있음 |
| C18 | Low | 서버 JSON이 이상하면 UI가 "새기는 중"에 멈춤 | fetch를 가짜로 바꿔 `{}`, `[1,2]`, `themes` 없음, `effects:"abc"`, `{error:{}}` 응답 → onBlank/show에서 TypeError, 무대와 상태줄이 "새기는 중"인 채 버튼만 다시 켜짐 | 영구 손상은 아님(재시도 가능). 사용자에게 오류 문구가 안 보임. `mana:"5"` 같은 문자열 숫자는 그대로 동작 |
| C19 | Low | 영웅 판정은 403(입장 코드 필요)을 처리하지 않음 | judgeHero가 403이면 서버 메시지만 보여 주고 코드를 묻지 않음 | ACCESS_CODE를 켠 배포에서 코드 입력은 카드 만들기에서만 가능. 처음 방문 때 저장된 덱이 있으면 영웅이 계속 오류로 보임 |

## 구체적 고치기 (구현은 안 함)

1. 비용 방어 (C1, C7, C8, C9, C14)
   - 이름을 캐시 키로 쓰기 전에 정규화: NFC 변환, 공백 연속은 하나로, 영어는 casefold. 같은 이름은 같은 키가 되게.
   - 공백 때문에 길이 제한이 새니, 정규화 뒤 전체 길이(예: 40자)에도 상한을 둔다.
   - IP별/전역 분당 호출 제한(예: IP당 분당 10건). Vercel은 캐시도 없으니 저장소(KV 등)나 최소한 Jev 쪽 예산 상한을 켠다.
   - 같은 이름의 진행 중 호출을 하나로 합치기(이름별 락 또는 in-flight dict).
   - Origin/Host 검사: 로컬은 Host가 localhost:8000 / 127.0.0.1:8000 이고 Origin이 없거나 같은 출처일 때만 허용. Content-Type이 application/json이 아니면 415.
2. 요청 파싱 (C5, C6, C13)
   - do_POST 전체를 try/except로 감싸고 잘못된 입력은 400. name/names/code는 isinstance(str) 검사. body가 dict가 아니면 400.
   - Content-Length는 0 이상 ~4KB 같은 상한으로 검사하고 아니면 411/413. 핸들러에 소켓 timeout(예: 10초).
   - `str(body.get("name",""))` 대신 문자열이 아니면 거절.
3. 캐시 저장 (C2, C9)
   - threading.Lock으로 CACHE 변경과 저장을 감싸고, 임시 파일에 쓴 뒤 os.replace로 교체(원자적). 저장 실패를 로그로 남긴다.
   - 캐시 항목 수 상한(예: 5000) 또는 LRU.
   - 시작 시 JSON이 깨졌으면 .bak으로 옮기고 알린다(지금은 조용히 `{}`).
4. 페이지 (C3, C4, C15, C18)
   - 숫자 필드는 Number()를 거쳐 정수일 때만 쓰고, color는 `/^#[0-9a-f]{6}$/i` 검사 후 아니면 기본색. tier는 0..3 정수만. 남는 `${...}`는 전부 esc() 또는 textContent.
   - localStorage 카드를 읽을 때 모양 검증 함수(sanitizeCard)를 두고, 실패한 카드는 버린다. renderGallery는 카드별 try/catch.
   - CSP 메타/헤더와 X-Content-Type-Options: nosniff 추가 (인라인 핸들러까지 막진 못하니 위 검증이 우선).
   - forgeName 전체를 try/catch로 감싸 오류 문구를 표시.
5. API (C10, C11, C12, C17, C19)
   - 401 힌트에서 키 길이/끝 4자리를 빼고, 502 메시지에서 Jev 응답 본문을 지운다(로그에만 남김).
   - 입장 코드는 hmac.compare_digest로 비교(둘 다 str일 때만). 시도 횟수 제한.
   - 영어 규칙에서 `\b` 대신 앞뒤가 영문자가 아닌지로 검사하면 `attack2`도 막힘.
   - .vercelignore에 forged_cache.json, hero_cache.json, samples.json 추가. 배포 URL에서 /forge.py, /forged_cache.json이 열리는지 확인.
   - judgeHero에 403 처리(코드 묻기) 추가.

## 제대로 막혀 있던 것

- 경로 처리: `GET /../server.py`, `/%2e%2e/server.py`, `/..%2fserver.py`, `/.env.local`, `/server.py`, `/forge.py`, `/forged_cache.json`, `/index.html?x=1`, 널 바이트 등 모두 404. do_GET은 `/`와 `/index.html`만 정확히 허용(요청에서 파일 이름을 만들지 않음). `GET /forge`, `GET /hero`는 404. PUT/DELETE/OPTIONS/HEAD는 501. CORS 헤더는 아예 없어서 다른 출처가 응답을 읽을 수 없음.
- 이름 문자 검사: 영문, 한글, 한자, 가나, 숫자, 공백, `-`, `'` 외에는 모두 거절. 그래서 `<`, `>`, 따옴표, 줄바꿈, 탭, 제로폭 문자, 전각 문자, 이모지, 결합 악센트, NBSP, 전각 공백, 널 문자는 모두 400. 프롬프트의 `<<<...>>>`와 `<<...>>` 경계를 이름이 깰 수 없음. /hero 캐시 키(`"\n".join(sorted(names))`)도 이름에 개행이 못 들어가서 충돌 불가(개행 이름은 400 확인).
- 앞뒤 공백/탭/개행 변형(`"화염검 "`, `" 화염검"`, `"화염검\t"`)은 strip()으로 같은 이름이 되어 캐시에 맞음(Jev 추가 호출 없음). 내부 공백, 대소문자, NFD는 C1 참조.
- 덱: 21장은 400, 빈 덱/문자열/dict/None은 400, 숫자·리스트·dict 원소는 이름 검사에서 400. 순서만 다른 덱은 같은 캐시 키(재호출 0번). 덱 하나는 Jev 호출 1번이라 증폭이 없음(20장이어도 1번).
- ACCESS_CODE(api/forge.py, api/hero.py): 없음/빈 문자열/대소문자 다름/뒤에 공백/널 문자/리스트/dict/0/False/True 전부 403. 정확히 일치할 때만 200. 코드는 이름 검사보다 먼저 확인됨. (ACCESS_CODE가 비어 있으면 검사 자체를 안 함은 의도된 동작.)
- 응답에 파일 경로나 키가 새지 않음: server.py 502는 `Jev 호출 실패: {e}`만 있고 traceback은 서버 콘솔에만. call_jev는 Authorization 헤더를 오류에 넣지 않음(본문 200자만).
- 페이지: 카드 이름, 요소, 종류, 테마, 효과 이름/설명/출처, 낙서 이유, 덱 칩, 영웅 제목/기질/패시브는 esc()를 거쳐 안전(`<img onerror>`를 넣어도 실행 안 됨, 속성 삽입도 안 됨). 덱 localStorage는 typeof string 필터 + esc로 안전. 상태줄은 textContent. nameHTML의 `$` 치환 패턴은 frag가 상수라 문제 없음.
- 이상 JSON 일부: `mana:"5"` 같은 문자열 숫자, 모르는 status, 서버가 null을 주는 경우는 오류 없이 처리하거나 "미리 만든 카드에 없습니다"로 떨어짐.
- 서버 카드 색은 서버가 hex로만 만들고, 이름은 검사 때문에 HTML 특수문자가 없어서, 지금 정상 서버 응답만으로는 XSS가 일어나지 않음 (C3는 오염된 데이터 전제).

## 참고: 테스트 범위와 한계

- Jev 응답 모양은 코드(make_card가 읽는 필드)를 따라 가짜로 만들었다. 실제 Jev 호출은 하지 않았다.
- C17(Vercel 정적 노출)과 실제 Vercel 환경의 동시성(C2)은 배포 환경에서 직접 확인하지 못했다.
- XSS는 Browser 도구로 내 포트(8001) 페이지에서만 확인했고, 끝난 뒤 그 출처의 localStorage를 비웠다. 사용자의 8000 페이지 저장소는 건드리지 않았다. 테스트 임시 파일은 scratchpad에만 있다.

# orbengine (복사본 — 직접 고치지 않는다)

게임 프로토타입(`proto/`)의 **구슬 생성 엔진**을 그대로 복사한 폴더. card-forge가 프로토타입과 똑같은 규칙으로 구슬을 만들게 하려는 것이다.
Vercel은 Root Directory(`toys/card-forge`) 밖의 파일을 못 가져올 수 있어서 복사본을 커밋한다.

- 원본: `proto/orbs.py`(Jev 요청·구슬 만들기·문구·가격), `proto/engine.py`(규칙 상수·식물 판별·사거리), `proto/vendor/`(측정된 질문지와 구슬 계산)
- 갱신: `proto/` 를 고친 뒤 `python toys/card-forge/sync_orbengine.py` → 커밋. 어긋남 검사: `python toys/card-forge/sync_orbengine.py --check`
- 쓰는 곳: `../forge_orb.py`(구슬 → 화면용 카드 JSON 변환), `../server.py`·`../api/forge.py`(`/forge`)

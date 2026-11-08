"""프로토타입(proto/)의 구슬 생성 엔진을 이 폴더의 orbengine/ 으로 복사한다. card-forge가 **게임 프로토타입과 똑같은 구슬 생성 엔진**을 쓰게 하려는 것이다.
(Vercel은 Root Directory 밖의 파일을 못 가져올 수 있어서 복사본을 커밋한다. 원본은 항상 proto/ 이고, orbengine/ 은 직접 고치지 않는다.)
  python sync_orbengine.py           # proto/ → orbengine/ 복사
  python sync_orbengine.py --check   # 복사본이 원본과 같은지만 검사(다르면 종료 코드 1)
proto/ 의 orbs.py·engine.py·vendor/ 를 고친 뒤에는 이 스크립트를 다시 실행하고 커밋한다."""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, "..", "..", "proto"); DST = os.path.join(HERE, "orbengine")
FILES = ["orbs.py", "engine.py", "value.py"] + [os.path.join("vendor", f) for f in ("axes.py", "axes_v1.py", "axes_v2.py", "axes_v3.py", "axes_v4.py", "orbmake.py")]
# vendor/forge.py 는 일부러 뺀다: 이 폴더의 forge.py(원본)가 같은 파일이다.
CHECK = "--check" in sys.argv; bad = []
for f in FILES:
    a, b = os.path.join(SRC, f), os.path.join(DST, f); data = open(a, "rb").read()
    if CHECK:
        if not os.path.exists(b) or open(b, "rb").read() != data: bad.append(f)
    else:
        os.makedirs(os.path.dirname(b), exist_ok=True); open(b, "wb").write(data)
if CHECK:
    print("차이 없음" if not bad else "차이 있음: " + ", ".join(bad)); sys.exit(1 if bad else 0)
print(f"복사 완료: {len(FILES)}개 → orbengine/")

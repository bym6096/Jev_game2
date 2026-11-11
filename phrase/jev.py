"""말 짓기 판정. server.py(로컬)와 api/judge.py(Vercel)가 같이 쓴다.

요청: {"sit": 상황 id, "tiles": [조각 id...], "act": 화행 id, "history": [{"tiles", "act", "reaction"}...]}
서버가 조각 id로 문장을 다시 조립하므로, Jev에는 정해진 조각으로 만든 문장만 들어간다(자유 텍스트 없음).
"""
import json, os, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://api.typesafe.ai/v1/systemone"
DATA = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
TILES = {t["id"]: t for t in DATA["tiles"]}
SITS = {s["id"]: s for s in DATA["situations"]}
ACTS = DATA["acts"]
MAXLEN, MAXHIST = 5, 6

OUTCOME = {
    "great": "목표 쪽으로 확 기울어 거의 넘어왔다",
    "good": "목표 쪽으로 꽤 움직였다",
    "little": "조금 움직였다",
    "none": "아무 변화가 없다",
    "worse": "오히려 목표에서 멀어졌다",
}
REACTION_Q = {
    "moved": "마음이 움직이거나 안심한다",
    "amused": "재미있어하거나 웃는다",
    "scared": "겁을 먹는다",
    "tempted": "솔깃해하거나 욕심이 난다",
    "fooled": "그 말을 그대로 믿어 버린다",
    "suspicious": "의심하거나 믿지 않는다",
    "annoyed": "짜증이 나거나 화가 난다",
    "confused": "무슨 말인지 몰라 어리둥절하다",
}


# ---- 한국어 렌더러 (반말). 다른 언어는 같은 범주·화행을 받아 자기 규칙으로 조립하는 함수를 따로 둔다. ----
def _batchim(w):
    c = ord(w[-1]) - 0xAC00
    return 0 <= c < 11172 and c % 28 != 0


def _pred_form(p, act):
    if act == "assert":   return p["h"], "."
    if act == "ask":      return p["h"], "?"
    if act == "plead":    return ("줘", ", 제발.") if p["ko"] == "주다" else (p["h"] + " 줘", ".")
    if act == "command":  return p["h"] + "라", "!"
    if act == "promise":  return p["l"] + "게", "."
    if act == "threaten": return p["l"] + " 거야", ". 두고 봐!"
    if act == "exclaim":  return p.get("ne") or p["st"] + "네", "!"
    if act == "suggest":  return p["st"] + "자", "."
    raise ValueError(act)


def _noun_form(w, act):
    cop = "이야" if _batchim(w) else "야"
    return {
        "assert": (w + cop, "."), "ask": (w + cop, "?"), "plead": (w + " 줘", ", 제발."),
        "command": (w + " 내놔", "!"), "promise": (w + " 줄게", "."), "threaten": (w + cop, ". 두고 봐!"),
        "exclaim": (w + ("이네" if _batchim(w) else "네"), "!"), "suggest": (w + " 하자", "."),
    }[act]


ROLES = ("subj", "obj", "to")   # 의미역: 누가 / 무엇을 / 누구에게 (한국어는 조사, 영어는 어순·전치사로 실현)


def _with_role(w, role):
    b = _batchim(w)
    if role == "subj":
        return {"나": "내가", "너": "네가"}.get(w, w + ("이" if b else "가"))
    if role == "obj":
        return w + ("을" if b else "를")
    if role == "to":
        return w + "에게"
    return w


def parse_tile(spec):
    """'mom' 또는 'mom:subj' -> (조각, 역할). 역할은 지시 조각에만."""
    tid, _, role = str(spec).partition(":")
    t = TILES.get(tid)
    if not t or (role and (role not in ROLES or t["cat"] != "ref")):
        return None
    return t, role


def render_ko(specs, act):
    allts = [parse_tile(x) for x in specs]
    ints = [t["ko"] for t, _ in allts if t["cat"] == "int"]   # 부름·감탄은 문장 앞으로 모은다
    ts = [x for x in allts if x[0]["cat"] != "int"]
    if not ts:
        return ", ".join(ints) + "!"
    head = ", ".join(ints) + ", " if ints else ""
    preds = [n for n, (t, _) in enumerate(ts) if t["cat"] == "pred"]
    last = preds[-1] if preds else len(ts) - 1
    words = []
    for n, (t, role) in enumerate(ts):
        if n == last:
            core, end = _pred_form(t, act) if t["cat"] == "pred" else _noun_form(t["ko"], act)
            words.append(core)
        elif t["cat"] == "pred":
            words.append(t["st"] + "고")
        else:
            words.append(_with_role(t["ko"], role))
    return head + " ".join(words) + end


# ---- Jev ----
def judge(sit, tiles, act, history):
    s = SITS[sit]
    lines = []
    for n, h in enumerate(history, 1):
        r = DATA["reactions"].get(h.get("reaction"), "")
        lines.append(f"{n}. 플레이어({ACTS[h['act']]['jev']}): \"{render_ko(h['tiles'], h['act'])}\" → {s['who']}의 반응: {r}")
    said = render_ko(tiles, act)
    state = (
        "놀이 규칙: 플레이어는 주어진 말 조각만으로 짧은 말을 지어 상대에게 건넨다. 조각이 적어 말이 서툴 수 있으니, "
        "말투보다 그 말이 전하는 뜻과 의도로 판단하라. 상대가 그 말을 듣고 어떻게 느끼고 움직일지 상대의 성격과 처지에 비추어 판단하라. "
        "앞서 한 말과 같은 말을 되풀이하거나 앞뒤가 안 맞으면 상대도 그것을 알아챈다.\n"
        f"상대: {s['desc']}\n"
        f"플레이어의 목표: {s['goal']}\n"
        + ("지금까지의 대화:\n" + "\n".join(lines) + "\n" if lines else "")
        + f"이번에 플레이어가 {ACTS[act]['jev']}: <<<{said}>>>"
    )
    body = {"model": "jev-latest", "state": state, "questions": {
        "outcome": {"type": "choice", "instructions": f"이 말을 들은 {s['who']}의 마음은 플레이어의 목표 쪽으로 어떻게 움직였는가?", "criteria": OUTCOME},
        "reaction": {"type": "choice", "instructions": f"이 말을 들은 {s['who']}의 가장 큰 반응은?", "criteria": REACTION_Q},
    }}
    headers = {"Content-Type": "application/json", "User-Agent": "jev-phrase-proto/0.2"}
    key = (os.environ.get("JEV_API_KEY") or "").strip()
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(URL, json.dumps(body).encode(), headers)
    with urllib.request.urlopen(req, timeout=40) as r:
        a = json.load(r)["answers"]
    return {"said": said, "outcome": a["outcome"]["probabilities"], "reaction": a["reaction"]["probabilities"]}


def _valid_line(tiles, act):
    return (isinstance(tiles, list) and 1 <= len(tiles) <= MAXLEN and all(parse_tile(t) for t in tiles) and act in ACTS)


def handle(req, headers):
    """요청 dict -> (상태 코드, 응답 dict). ACCESS_CODE 환경 변수가 있으면 X-Access-Code 헤더가 맞아야 한다."""
    code = os.environ.get("ACCESS_CODE")
    if code and headers.get("X-Access-Code") != code:
        return 403, {"error": "접근 코드가 필요합니다 (주소 끝에 ?code=코드)"}
    sit, tiles, act, hist = req.get("sit"), req.get("tiles"), req.get("act"), req.get("history") or []
    if sit not in SITS or not _valid_line(tiles, act) or not isinstance(hist, list) or len(hist) > MAXHIST \
            or not all(isinstance(h, dict) and _valid_line(h.get("tiles"), h.get("act")) for h in hist):
        return 400, {"error": "요청 형식이 잘못되었습니다"}
    try:
        return 200, judge(sit, tiles, act, hist)
    except urllib.error.HTTPError as e:
        return 502, {"error": f"Jev HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"}
    except Exception as e:
        return 500, {"error": f"판정 오류: {type(e).__name__}"}

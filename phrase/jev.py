"""말 짓기 판정. server.py(로컬)와 api/judge.py(Vercel)가 같이 쓴다.

요청: {"brief": 의뢰 id, "cells": {칸 id: 조각 id}, "case": 대상 칸 격, "act": 말투 id, "history": [같은 모양의 앞선 시안...]}
서버가 조각 id로 문장을 다시 조립하므로, Jev에는 정해진 조각으로 만든 문장만 들어간다(자유 텍스트 없음).
점수도 서버가 계산한다: 채택 점수 × 결 배율, 배율 = 1 + (2×결 적중 + 새로움) × 채택률.
"""
import json, os, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://api.typesafe.ai/v1/systemone"
DATA = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
TILES = {t["id"]: t for t in DATA["tiles"]}
BRIEFS = {b["id"]: b for b in DATA["briefs"]}
FORMS, ACTS, CASES, VIBES = DATA["forms"], DATA["acts"], DATA["cases"], DATA["vibes"]
MAXHIST = 4

ADOPT = {"yes": "바로 채택한다", "maybe": "마음에 들어서 고민한다", "revise": "아이디어는 있지만 고쳐 오라고 한다",
         "no": "거절한다", "angry": "불쾌해한다"}
ADOPT_PTS = {"yes": 100, "maybe": 70, "revise": 40, "no": 10, "angry": 0}
FRESH = {"wow": "처음 보는, 머리에 박히는 표현이다", "fresh": "신선하고 의외다", "ok": "무난하다",
         "cliche": "어디서 본 듯 뻔하다", "broken": "말이 안 돼서 뜻이 안 전해진다"}
FRESH_BONUS = {"wow": 1.5, "fresh": 1.0, "ok": 0.3, "cliche": 0.0, "broken": -0.3}


# ---- 한국어 렌더러 (반말). 다른 언어는 같은 칸·격·말투를 받아 자기 어순과 규칙으로 조립하는 함수를 따로 둔다. ----
def _batchim(w):
    c = ord(w[-1]) - 0xAC00
    return 0 <= c < 11172 and c % 28 != 0


def _pred_form(p, act):
    if act == "assert":   return p["h"]
    if act == "ask":      return p["h"] + "?"
    if act == "plead":    return p["h"] + " 줘."
    if act == "command":  return p["h"] + "라!"
    if act == "promise":  return p["l"] + "게."
    if act == "threaten": return p["l"] + " 거야. 두고 봐."
    if act == "exclaim":  return (p.get("ne") or p["st"] + "네") + "!"
    if act == "suggest":  return p["st"] + "자."
    raise ValueError(act)


END_NO_PRED = {"assert": ".", "ask": "?", "plead": ", 제발.", "command": "!", "promise": ".", "threaten": ". 두고 봐.", "exclaim": "!", "suggest": "."}


def _case(w, case):
    b = _batchim(w)
    return w + {"obj": "을" if b else "를", "to": "에게", "like": "처럼", "with": "과" if b else "와", "at": "에서"}[case]


def _subj(w):
    return {"나": "내가", "너": "네가"}.get(w, w + ("이" if _batchim(w) else "가"))


def render_ko(form, cells, case="obj", act="assert", ending=None):
    g = lambda k: TILES[cells[k]] if cells.get(k) else None
    if form == "name":
        a1, n1, a2, n2 = g("a1"), g("n1"), g("a2"), g("n2")
        first = " ".join(t["ko"] for t in (a1, n1) if t)
        second = " ".join(t["ko"] for t in (a2, n2) if t)
        if n1 and second:
            return f"{first}의 {second}"
        return " ".join(x for x in (first, second) if x)
    if form == "short":   # 빠른 모드: 어떤 누가 / 어떤 무엇을(격) / 어떻게 / 한다 + 끝맺음
        if not cells:
            return ""
        body = render_ko("line", {k: v for k, v in cells.items() if k in ("sa", "s", "oa", "o", "m", "v")}, case, "assert")
        return body[:-1] + (ending or ".") if body.endswith(".") else body + (ending or "")
    # 한 줄: 부름 / 어떤 누가 / 어떤 무엇을(격) / 어떻게 / 부정·확신 / 한다 + 말투
    i, sa, s, oa, o, m, p, v = (g(k) for k in ("i", "sa", "s", "oa", "o", "m", "p", "v"))
    words = []
    if sa: words.append(sa["ko"])
    if s: words.append(_subj(s["ko"]) if (v or o) else s["ko"])
    if oa: words.append(oa["ko"])
    if o: words.append(_case(o["ko"], case))   # 고른 꼴은 서술어가 없어도 붙인다
    if m: words.append(m["ko"])
    if p: words.append(p["ko"])
    if v:
        words.append(_pred_form(v, act))
        body = " ".join(words)
        if act == "assert": body += "."
    else:
        body = " ".join(words) + (END_NO_PRED[act] if words else "")
    if i:
        return i["ko"] + ("! " if not body else ", ") + body if body else i["ko"] + "!"
    return body


def _jong(w):
    c = ord(w[-1]) - 0xAC00
    return c % 28 if 0 <= c < 11172 else 0


def _attach(w, pid):
    """조사 하나를 앞말에 붙인다. 받침에 맞는 꼴을 고른다."""
    p = PARTICLES[pid]
    if pid == "subj" and w in ("나", "너"):
        return {"나": "내가", "너": "네가"}[w]
    if pid == "dir":
        j = _jong(w)
        return w + ("으로" if j and j != 8 else "로")   # ㄹ 받침은 '로'
    return w + (p["b"] if _batchim(w) else p["nb"])


def render_free_ko(tokens, ending="."):
    """도화지 모드: 읽는 순서대로 놓인 토큰 목록 [{"t": 조각 id} | {"p": 조사 id}] → 문장.
    조사는 앞말에 붙고(앞말이 없으면 버린다), 마지막 서술어는 해체 + 끝맺음, 그 앞 서술어는 '~고'로 잇는다."""
    last_pred = max((i for i, k in enumerate(tokens) if "t" in k and TILES[k["t"]]["cat"] == "pred"), default=-1)
    out = []
    for i, k in enumerate(tokens):
        if "p" in k:
            if out:
                out[-1] = _attach(out[-1], k["p"])
            continue
        t = TILES[k["t"]]
        if t["cat"] == "pred":
            out.append(t["h"] if i == last_pred else t["st"] + "고")
        else:
            out.append(t["ko"])
    return " ".join(out) + ending if out else ""


def check(brief, cells, case, act):
    """칸에 맞는 범주인지, 의뢰의 규칙을 지켰는지. 문제가 있으면 이유 문자열."""
    form = FORMS[brief["form"]]
    spec = {c["id"]: c for c in form["cells"]}
    if not isinstance(cells, dict) or not cells:
        return "빈 시안"
    rule = brief.get("rule", {})
    for k, tid in cells.items():
        t = TILES.get(tid)
        if k not in spec or not t or t["cat"] not in spec[k]["cats"]:
            return "칸에 맞지 않는 조각"
        if k in rule.get("lock", []):
            return "봉인된 칸"
        if any(w in t["ko"] for w in rule.get("ban_dom_word", [])):
            return "금지된 조각"
    if rule.get("max_filled") and len(cells) > rule["max_filled"]:
        return "칸을 너무 많이 채움"
    if rule.get("require") and rule["require"] not in cells.values():
        return "꼭 넣어야 할 조각이 없음"
    if case not in CASES or (form.get("act") and act not in ACTS):
        return "격이나 말투가 잘못됨"
    return None


# ---- Jev ----
def _call(state, questions):
    headers = {"Content-Type": "application/json", "User-Agent": "jev-phrase-proto/0.3"}
    key = (os.environ.get("JEV_API_KEY") or "").strip()
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(URL, json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode(), headers)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)["answers"]


def judge(brief_id, cells, case="obj", act="assert", history=()):
    b = BRIEFS[brief_id]
    said = render_ko(b["form"], cells, case, act)
    past = [render_ko(b["form"], h["cells"], h.get("case", "obj"), h.get("act", "assert")) for h in history]
    want = " + ".join(VIBES[v] for v in b["vibes"])
    state = (
        "놀이 규칙: 플레이어는 정해진 말 조각을 문장 틀의 칸에 끼워 한 줄을 짓는 카피라이터다. 조각으로 지은 말이라 조금 서툴 수 있으니, "
        "문법보다 그 말이 주는 느낌, 떠오르는 장면, 의외성으로 판단하라. 감각이 뒤섞인 표현(소리를 맛으로, 시간을 촉감으로 말하는 식)도 "
        "제대로 먹히면 높이 쳐라.\n"
        f"의뢰인: {b['client']}\n무엇: {b['medium']}\n의뢰 내용: {b['brief']}\n원하는 결: {want}\n"
        + ("이미 받아 본 시안:\n" + "\n".join(f"- {x}" for x in past) + "\n" if past else "")
        + f"이번 시안: <<<{said}>>>"
    )
    qs = {
        "adopt": {"type": "choice", "instructions": (
            f"{b['client']}은(는) 이 시안을 실제로 {b['medium']}(으)로 쓸 것인가? 의뢰인은 돈을 내는 사람이다. "
            "무슨 뜻인지 와닿지 않거나, 의뢰의 목적과 상관없거나, 낱말을 아무렇게나 늘어놓은 것 같으면 아무리 신기해도 채택하지 않는다. "
            "이미 본 시안과 비슷하면 덜 반긴다."), "criteria": ADOPT},
        "vibe": {"type": "choice", "instructions": "이 한 줄에서 가장 강하게 느껴지는 결은?", "criteria": {k: v for k, v in VIBES.items()} | {"flat": "아무 느낌이 없다"}},
        "fresh": {"type": "choice", "instructions": "이 표현은 얼마나 새롭고 의외인가?", "criteria": FRESH},
    }
    a = _call(state, qs)
    ad, vi, fr = a["adopt"]["probabilities"], a["vibe"]["probabilities"], a["fresh"]["probabilities"]
    base = sum(ADOPT_PTS[k] * p for k, p in ad.items())
    match = sum(vi.get(v, 0) for v in b["vibes"])
    fresh = sum(FRESH_BONUS[k] * p for k, p in fr.items())
    # 결과 새로움은 의뢰인이 받아들인 만큼만 배율이 된다: 채택이 낮으면 신선해도 소용없다
    mult = max(0.5, 1 + (2 * match + fresh) * (base / 100))
    return {"said": said, "adopt": ad, "vibe": vi, "fresh": fr,
            "base": round(base), "match": round(match, 2), "fresh_bonus": round(fresh, 2), "mult": round(mult, 1),
            "score": round(base * round(mult, 1))}


LAND = {"strong": "확실히 그렇게 느낀다", "some": "어느 정도 느낀다", "bit": "살짝 느낀다", "none": "전혀 못 느낀다", "opposite": "오히려 반대로 느낀다"}
LAND_PTS = {"strong": 1.0, "some": 0.65, "bit": 0.3, "none": 0.0, "opposite": -0.2}
ENDINGS = DATA["endings"]
SENSE = {"clear": "무슨 말인지 바로 그려진다", "plausible": "조금 엉뚱하지만 그럴듯하게 그려진다", "vague": "뭔가 있어 보이지만 뜻이 흐릿하다", "nonsense": "낱말을 늘어놓은 것 같아 말이 안 된다"}
SENSE_PTS = {"clear": 1.0, "plausible": 0.75, "vague": 0.3, "nonsense": 0.0}
PARTICLES = {p["id"]: p for p in DATA["particles"]}
MAX_WORDS, MAX_TOKENS = 8, 20
LEN_K = 0.4          # 길이 배율: 칸 하나 더할 때마다 +0.4 × 꽂힘
SPEED_K, SPEED_T = 0.6, 8.0   # 속도 배율: 목표가 뜬 뒤 SPEED_T초 안에 보낼수록 최대 +0.6 × 꽂힘


def judge_rush(vibe, tokens, ending=".", history=(), secs=SPEED_T):
    """빠른 모드: 목표 결 하나.
    점수 = 100 × 꽂힘 × 길이 배율 × 속도 배율 × 새로움 배율
      길이 배율 = 1 + LEN_K × (낱말 수 − 1) × 꽂힘 × 뜻²    ← 길어도 안 꽂히거나 말이 안 되면 거의 안 붙는다
      속도 배율 = 1 + SPEED_K × (남은 몫) × 꽂힘            ← 남은 몫 = max(0, (SPEED_T − 걸린 초) / SPEED_T)
      새로움 배율 = 1 + 새로움 × 꽂힘 × 뜻²
    뜻(0~1) = 무슨 말인지 그려지는 정도. 꽂힘만으로는 말 안 되는 긴 줄도 분위기로 점수를 받아서 따로 묻는다.
    전략: 짧고 정확하게(빠름 → 속도 배율·콤보) vs 길고 그럴싸하게(길이 배율, 대신 시간이 들고 뜻이 흐려질 위험)."""
    said = render_free_ko(tokens, ending)
    past = [render_free_ko(h["tokens"], h.get("ending", ".")) for h in history]
    state = (
        "놀이 규칙: 플레이어는 정해진 말 조각을 짧은 문장 틀에 끼워 제한 시간 안에 한 줄을 빠르게 짓는다. 조각으로 지은 말이라 조금 서툴 수 있다. "
        "문법보다 이 말을 들은 보통 사람이 실제로 무엇을 느끼는지로 판단하라. 낱말을 아무렇게나 늘어놓아 뜻이 안 통하면 아무것도 못 느낀다. "
        "끝맺음(…, ㅋㅋ, ㅠㅠ 등)의 뉘앙스도 느낌에 넣어라.\n"
        f"목표: 듣는 사람이 '{VIBES[vibe]}'을(를) 느끼게 한다.\n"
        + ("방금까지 지은 줄(비슷하면 식상하다):\n" + "\n".join(f"- {x}" for x in past) + "\n" if past else "")
        + f"이번 줄: <<<{said}>>>"
    )
    a = _call(state, {
        "land": {"type": "choice", "instructions": f"이 줄을 들은 사람은 '{VIBES[vibe]}'을(를) 느끼는가?", "criteria": LAND},
        "fresh": {"type": "choice", "instructions": "이 표현은 얼마나 새롭고 의외인가?", "criteria": FRESH},
        "sense": {"type": "choice", "instructions": "분위기와 상관없이, 이 줄이 무슨 장면이나 뜻인지 그려지는가?", "criteria": SENSE},
    })
    la, fr, se = a["land"]["probabilities"], a["fresh"]["probabilities"], a["sense"]["probabilities"]
    sense = sum(SENSE_PTS[k] * p for k, p in se.items())
    land = sum(LAND_PTS[k] * p for k, p in la.items())
    fresh = sum(FRESH_BONUS[k] * p for k, p in fr.items())
    q = max(0, land)
    n = sum(1 for k in tokens if "t" in k)   # 길이는 낱말 조각 수(조사는 무료)
    g = sense * sense   # 뜻이 반쯤만 통하면 반보다 더 깎는다(0.9 → 0.81, 0.6 → 0.36)
    len_mult = 1 + LEN_K * (n - 1) * q * g
    fresh_mult = 1 + max(0, fresh) * q * g
    secs = min(max(float(secs), 0.0), 600.0)
    speed_mult = 1 + SPEED_K * max(0.0, (SPEED_T - secs) / SPEED_T) * q
    score = max(0, round(100 * land * len_mult * speed_mult * fresh_mult))
    return {"said": said, "land": la, "fresh": fr, "sense": se, "land_ev": round(land, 2), "fresh_bonus": round(fresh, 2), "sense_ev": round(sense, 2),
            "cells": n, "len_mult": round(len_mult, 2), "speed_mult": round(speed_mult, 2), "fresh_mult": round(fresh_mult, 2), "score": score}


def handle(req, headers):
    """요청 dict -> (상태 코드, 응답 dict). ACCESS_CODE 환경 변수가 있으면 X-Access-Code 헤더가 맞아야 한다."""
    code = os.environ.get("ACCESS_CODE")
    if code and headers.get("X-Access-Code") != code:
        return 403, {"error": "접근 코드가 필요합니다 (주소 끝에 ?code=코드)"}
    if req.get("mode") == "rush":
        return _handle_rush(req)
    b = BRIEFS.get(req.get("brief"))
    hist = req.get("history") or []
    if not b or not isinstance(hist, list) or len(hist) > MAXHIST:
        return 400, {"error": "요청 형식이 잘못되었습니다"}
    case, act = req.get("case", "obj"), req.get("act", "assert")
    why = check(b, req.get("cells"), case, act)
    for h in hist:
        why = why or (check(b, h.get("cells"), h.get("case", "obj"), h.get("act", "assert")) if isinstance(h, dict) else "기록 형식")
    if why:
        return 400, {"error": why}
    try:
        return 200, judge(b["id"], req["cells"], case, act, hist)
    except urllib.error.HTTPError as e:
        return 502, {"error": f"Jev HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"}
    except Exception as e:
        return 500, {"error": f"판정 오류: {type(e).__name__}"}


def _rush_ok(tokens, ending, need=None):
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= MAX_TOKENS or ending not in ENDINGS:
        return False
    for k in tokens:
        if not isinstance(k, dict) or len(k) != 1:
            return False
        if "t" in k and k["t"] not in TILES or "p" in k and k["p"] not in PARTICLES or not ("t" in k or "p" in k):
            return False
    words = [k["t"] for k in tokens if "t" in k]
    return 1 <= len(words) <= MAX_WORDS and len(set(words)) == len(words) and (not need or need in words)


def _handle_rush(req):
    vibe, hist, ending = req.get("vibe"), req.get("history") or [], req.get("ending", ".")
    if vibe not in VIBES or not isinstance(hist, list) or len(hist) > 6 or not _rush_ok(req.get("tokens"), ending, req.get("need")) \
            or not all(isinstance(h, dict) and _rush_ok(h.get("tokens"), h.get("ending", ".")) for h in hist):
        return 400, {"error": "요청 형식이 잘못되었습니다"}
    secs = req.get("secs", SPEED_T)
    if not isinstance(secs, (int, float)):
        return 400, {"error": "요청 형식이 잘못되었습니다"}
    try:
        return 200, judge_rush(vibe, req["tokens"], ending, hist, secs)
    except urllib.error.HTTPError as e:
        return 502, {"error": f"Jev HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"}
    except Exception as e:
        return 500, {"error": f"판정 오류: {type(e).__name__}"}

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


def render_ko(form, cells, case="obj", act="assert"):
    g = lambda k: TILES[cells[k]] if cells.get(k) else None
    if form == "name":
        a1, n1, a2, n2 = g("a1"), g("n1"), g("a2"), g("n2")
        first = " ".join(t["ko"] for t in (a1, n1) if t)
        second = " ".join(t["ko"] for t in (a2, n2) if t)
        if n1 and second:
            return f"{first}의 {second}"
        return " ".join(x for x in (first, second) if x)
    # 한 줄: 부름 / 어떤 누가 / 어떤 무엇을(격) / 어떻게 / 부정·확신 / 한다 + 말투
    i, sa, s, oa, o, m, p, v = (g(k) for k in ("i", "sa", "s", "oa", "o", "m", "p", "v"))
    words = []
    if sa: words.append(sa["ko"])
    if s: words.append(_subj(s["ko"]) if v else s["ko"])
    if oa: words.append(oa["ko"])
    if o: words.append(_case(o["ko"], case) if v else o["ko"])
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


def handle(req, headers):
    """요청 dict -> (상태 코드, 응답 dict). ACCESS_CODE 환경 변수가 있으면 X-Access-Code 헤더가 맞아야 한다."""
    code = os.environ.get("ACCESS_CODE")
    if code and headers.get("X-Access-Code") != code:
        return 403, {"error": "접근 코드가 필요합니다 (주소 끝에 ?code=코드)"}
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

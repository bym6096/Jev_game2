"""Prototype web server: serves proto/static and a small JSON API. Rules live in engine.py; Jev calls (new orbs from a typed name) in orbs.py."""
import os, sys, json, random, secrets, traceback, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import orbs, engine
SESS = {}
STATIC = os.path.join(HERE, "static"); MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
def new_session(stage_type):
    sid = secrets.token_hex(6); R = random.Random(); g = engine.HexGame(orbs.starter_orbs(), stage_type=stage_type, seed=R.randrange(10 ** 9))
    SESS[sid] = {"g": g, "blanks": [orbs.new_blank("평범한", R), orbs.new_blank("깨끗한", R)], "written": [None, None], "R": R}; return sid
def payload(sid):
    S = SESS[sid]; g = S["g"]; v = g.view()
    v["sid"] = sid; v["blanks"] = [{**b, "max_typed": orbs.max_typed(b), "orb": S["written"][i]} for i, b in enumerate(S["blanks"])]
    v["bag_names"] = [g.inst[i]["o"]["name"] for i in g.bag]; return v
class H(BaseHTTPRequestHandler):
    def log_message(s, *a): pass
    def send(s, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        s.send_response(code); s.send_header("Content-Type", ctype); s.send_header("Content-Length", str(len(b))); s.send_header("Cache-Control", "no-store"); s.end_headers(); s.wfile.write(b)
    def do_GET(s):
        p = urllib.parse.urlparse(s.path); path = p.path
        if path == "/api/state":
            sid = urllib.parse.parse_qs(p.query).get("sid", [""])[0]
            return s.send(200, payload(sid)) if sid in SESS else s.send(404, {"error": "세션이 없습니다"})
        f = "index.html" if path == "/" else path.lstrip("/")
        fp = os.path.normpath(os.path.join(STATIC, f))
        if not fp.startswith(STATIC) or not os.path.isfile(fp): return s.send(404, {"error": "not found"})
        s.send(200, open(fp, "rb").read(), MIME.get(os.path.splitext(fp)[1], "application/octet-stream"))
    def do_POST(s):
        try:
            n = int(s.headers.get("Content-Length", 0)); body = json.loads(s.rfile.read(n) or b"{}") if n < 20000 else {}
            path = urllib.parse.urlparse(s.path).path
            if path == "/api/new":
                st = body.get("stage_type", "balanced"); st = st if st in engine.STAGE_TYPES else "balanced"; return s.send(200, payload(new_session(st)))
            sid = body.get("sid"); S = SESS.get(sid)
            if not S: return s.send(404, {"error": "세션이 없습니다"})
            g = S["g"]
            if path == "/api/write":
                i = int(body.get("idx", -1))
                if g.phase != "setup" or i not in (0, 1) or S["written"][i]: return s.send(400, {"error": "이미 쓴 빈 구슬이거나 쓸 수 없는 단계입니다"})
                blank = S["blanks"][i]; typed, err = orbs.check_typed(blank, str(body.get("text", "")))
                if err: return s.send(400, {"error": err})
                full = orbs.fuse(blank, typed)
                try: o = orbs.orb_from_jev(full)
                except Exception as e: return s.send(502, {"error": f"Jev 호출 실패: {str(e)[:120]}"})
                g.add_orb(o); S["written"][i] = {"name": full, "text": o["text"], "mana": o["mana"], "role": o["role"], "scribble": bool(o.get("scribble"))}
                return s.send(200, payload(sid))
            if path == "/api/start":
                if g.phase == "setup": g.start()
                return s.send(200, payload(sid))
            if path == "/api/play":
                t = body.get("tile"); r = g.play(int(body.get("idx", -1)), tuple(t) if t else None); v = payload(sid); v["action"] = r; return s.send(200, v)
            if path == "/api/end_turn":
                r = g.end_turn(); v = payload(sid); v["action"] = r; return s.send(200, v)
            s.send(404, {"error": "unknown"})
        except Exception as e:
            traceback.print_exc(); s.send(500, {"error": f"서버 오류: {e}"})
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8010")); print(f"http://localhost:{port}"); ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()

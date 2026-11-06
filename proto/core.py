"""Stateless request handling shared by the local server (server.py) and the Vercel function (api/app.py).
The whole game state travels with every request as a signed blob (HMAC over a compressed pickle), so no server memory is needed.
Secret: STATE_SECRET, else JEV_API_KEY, else a random per-process value (fine for local use)."""
import os, sys, base64, hmac, hashlib, pickle, random, secrets, zlib, hmac as _h
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import engine, orbs
_SECRET = (os.environ.get("STATE_SECRET") or os.environ.get("JEV_API_KEY") or secrets.token_hex(16)).encode()
def pack(S):
    raw = zlib.compress(pickle.dumps(S, protocol=4), 6); return base64.urlsafe_b64encode(raw).decode() + "." + hmac.new(_SECRET, raw, hashlib.sha256).hexdigest()
def unpack(blob):
    p, sig = str(blob).rsplit(".", 1); raw = base64.urlsafe_b64decode(p.encode())
    if not hmac.compare_digest(hmac.new(_SECRET, raw, hashlib.sha256).hexdigest(), sig): raise ValueError("서명이 맞지 않습니다")
    return pickle.loads(zlib.decompress(raw))
def view(S):
    g = S["g"]; v = g.view()
    v["blanks"] = [{**b, "max_typed": orbs.max_typed(b), "orb": S["written"][i]} for i, b in enumerate(S["blanks"])]
    v["bag_names"] = [g.inst[i]["o"]["name"] for i in g.bag]; v["blob"] = pack(S); return v
def handle(body):
    """-> (http status, json-able dict)"""
    code = os.environ.get("ACCESS_CODE")
    if code and body.get("code") != code: return 403, {"error": "접근 코드가 필요합니다", "need_code": True}
    op = body.get("op")
    if op == "new":
        st = body.get("stage_type", "balanced"); st = st if st in engine.STAGE_TYPES else "balanced"; R = random.Random()
        g = engine.HexGame(orbs.starter_orbs(), stage_type=st, seed=R.randrange(10 ** 9))
        return 200, view({"g": g, "blanks": [orbs.new_blank("평범한", R), orbs.new_blank("깨끗한", R)], "written": [None, None]})
    try: S = unpack(body.get("blob", ""))
    except Exception: return 400, {"error": "게임 상태가 올바르지 않습니다. 새 게임을 시작하세요."}
    g = S["g"]
    if op == "write":
        try: i = int(body.get("idx", -1))
        except (TypeError, ValueError): i = -1
        if g.phase != "setup" or i not in (0, 1) or S["written"][i]: return 400, {"error": "이미 쓴 빈 구슬이거나 쓸 수 없는 단계입니다"}
        blank = S["blanks"][i]; typed, err = orbs.check_typed(blank, str(body.get("text", "")))
        if err: return 400, {"error": err}
        full = orbs.fuse(blank, typed)
        try: o = orbs.orb_from_jev(full)
        except Exception as e: return 502, {"error": f"Jev 호출 실패: {str(e)[:120]}"}
        g.add_orb(o); S["written"][i] = {"name": full, "text": o["text"], "mana": o["mana"], "role": o["role"], "scribble": bool(o.get("scribble")), "verb": o["payload"][0][0] if o["payload"] else None, "mat": o.get("mat")}
        return 200, view(S)
    if op == "start":
        if g.phase == "setup": g.start()
        return 200, view(S)
    if op == "play":
        t = body.get("tile")
        try: r = g.play(int(body.get("idx", -1)), tuple(int(x) for x in t) if t else None, int(body["target"]) if body.get("target") is not None else None)
        except (TypeError, ValueError): r = {"error": "요청이 잘못되었습니다"}
        v = view(S); v["action"] = r; v["events"] = list(getattr(g, "events", [])); return 200, v
    if op == "preview":
        # 복사본으로 턴 종료를 미리 돌려 본다(난수 상태까지 덩어리에 들어 있어 실제 턴 종료와 결과가 같다). 저장하지 않는다.
        if g.phase != "play": return 200, {"preview": None}
        v1 = g.view(); g2 = unpack(body.get("blob", ""))["g"]; g2.end_turn(); v2 = g2.view()
        id1 = {e["id"]: e for e in v1["enemies"]}; id2 = {e["id"]: e for e in v2["enemies"]}
        moves = [{"id": i, "from": [e["q"], e["r"]], "to": [id2[i]["q"], id2[i]["r"]]} for i, e in id1.items() if i in id2 and (e["q"], e["r"]) != (id2[i]["q"], id2[i]["r"])]
        own = []
        for k in ("buildings", "summons"):
            n = {x["id"]: x for x in v2[k]}
            for x in v1[k]:
                y = n.get(x["id"])
                if y is None: own.append({"id": x["id"], "kind": k, "q": x["q"], "r": x["r"], "name": x["name"], "lost": True, "dmg": x["hp"]})
                elif y["hp"] < x["hp"]: own.append({"id": x["id"], "kind": k, "q": x["q"], "r": x["r"], "name": x["name"], "lost": False, "dmg": x["hp"] - y["hp"]})
        pv = {"over": v2["phase"] == "over", "result": v2["result"], "hp": v2["hp"] - v1["hp"], "gold": v2["gold"] - v1["gold"], "res": {k: v2["res"][k] - v1["res"][k] for k in v1["res"]},
              "kills": sum(1 for i in id1 if i not in id2), "spawn": sum(1 for i in id2 if i not in id1), "moves": moves, "own": own, "dead": [[e["q"], e["r"]] for i, e in id1.items() if i not in id2], "spawned": [[e["q"], e["r"]] for i, e in id2.items() if i not in id1]}
        return 200, {"preview": pv}
    if op == "end_turn":
        r = g.end_turn(); v = view(S); v["action"] = r; v["events"] = list(getattr(g, "events", [])); return 200, v
    return 404, {"error": "알 수 없는 요청"}

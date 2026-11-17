"""Send the same decision items to Jev and Gemini Decision 1 and log both.

Both APIs take nearly the same body:
  Jev:    POST https://api.typesafe.ai/v1/systemone            {"model", "state", "questions"}
  Gemini: POST https://generativelanguage.googleapis.com/v1beta/decisions  {"model", "input", "questions"}
Question shapes (choice / noul / score with "instructions" and "criteria") are shared.

Input: items JSON (same format as jev_run.py):
  [{"id": "...", "cond": "...", "state": "<text>", "questions": {...}, "expect": {"q": "answer"}?}]
Output: JSONL, one line per call: backend, id, cond, rep, answers, usage, latency_ms.

Usage:
  python3 -I tools/decide_compare.py items.json out.jsonl --max 400 [--repeat 1] [--backends jev,gemini]

Keys: in the cloud sandbox the egress proxy attaches credentials for both hosts.
Locally, set JEV_API_KEY and GEMINI_API_KEY (never printed).
"""
import argparse, json, os, sys, time, urllib.error, urllib.request

BACKENDS = {
    "jev": {"url": "https://api.typesafe.ai/v1/systemone", "model": "jev-latest", "field": "state"},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/decisions", "model": "gemini-decision-1", "field": "input"},
}


def _headers(backend):
    h = {"Content-Type": "application/json"}
    if backend == "jev":
        k = (os.environ.get("JEV_API_KEY") or "").strip()
        if k:
            h["Authorization"] = "Bearer " + k
    else:
        h["x-goog-api-key"] = (os.environ.get("GEMINI_API_KEY") or "").strip() or "proxy-injected"
    return h


def call(backend, state, questions):
    b = BACKENDS[backend]
    body = {"model": b["model"], b["field"]: state, "questions": questions}
    req = urllib.request.Request(b["url"], json.dumps(body).encode(), _headers(backend))
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return data, (time.perf_counter() - t0) * 1000


def input_tokens(backend, usage):
    return usage.get("input_tokens") if backend == "jev" else usage.get("total_input_tokens")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("out")
    ap.add_argument("--max", type=int, required=True, help="hard cap on requests per backend")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--backends", default="jev,gemini")
    a = ap.parse_args()

    items = json.load(open(a.items, encoding="utf-8"))
    backends = a.backends.split(",")
    planned = len(items) * a.repeat
    if planned > a.max:
        sys.exit(f"planned {planned} requests per backend > cap {a.max}; nothing sent")

    stats = {b: {"calls": 0, "errors": 0, "tokens": 0, "lat": []} for b in backends}
    with open(a.out, "w", encoding="utf-8") as f:
        for it in items:
            for rep in range(a.repeat):
                for be in backends:   # interleave so both see the same time window
                    s = stats[be]
                    d = None
                    for attempt in range(4):
                        try:
                            d, ms = call(be, it["state"], it["questions"])
                            break
                        except urllib.error.HTTPError as e:
                            if e.code in (429, 500, 502, 503) and attempt < 3:
                                time.sleep(3 * (attempt + 1))
                                continue
                            s["errors"] += 1
                            print(f"[{be}] HTTP {e.code} on {it['id']}: {e.read()[:300]!r}", file=sys.stderr)
                            break
                        except Exception as e:
                            if attempt == 3:
                                s["errors"] += 1
                                print(f"[{be}] error on {it['id']}: {e}", file=sys.stderr)
                            else:
                                time.sleep(2)
                    s["calls"] += 1
                    if s["errors"] >= 8:
                        sys.exit(f"STOP: 8 errors on {be} after {s['calls']} calls")
                    if d is None:
                        continue
                    s["tokens"] += input_tokens(be, d.get("usage", {})) or 0
                    s["lat"].append(ms)
                    f.write(json.dumps({"backend": be, "id": it["id"], "cond": it.get("cond"), "rep": rep,
                                        "answers": d["answers"], "usage": d.get("usage"),
                                        "model": d.get("model"), "latency_ms": round(ms)},
                                       ensure_ascii=False) + "\n")
                    f.flush()
    out = {}
    for be, s in stats.items():
        lat = sorted(s["lat"])
        p = lambda q: round(lat[min(len(lat) - 1, int(q * len(lat)))]) if lat else None
        out[be] = {"calls": s["calls"], "errors": s["errors"], "input_tokens": s["tokens"],
                   "latency_ms_p50": p(0.5), "latency_ms_p95": p(0.95)}
    print(json.dumps(out))


if __name__ == "__main__":
    main()

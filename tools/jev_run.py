"""Jev measurement runner with a hard request cap.

Input: a JSON file with a list of items:
  [{"id": "...", "cond": "...", "state": "<text or object>",
    "questions": {"q": {"type": "choice", "instructions": "...", "criteria": {"a": null, "b": null}}}}]
Output: JSONL, one line per call: id, cond, rep, answers, usage, latency_ms.

Usage:
  python3 -I jev_run.py items.json out.jsonl --max 300 [--repeat 1] [--model jev-latest]

The API key is never read or printed here; the environment's egress proxy
attaches the Authorization header for api.typesafe.ai.
"""
import argparse, json, sys, time, urllib.error, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
PRICE_PER_M = 0.042  # USD per 1M input tokens, third-party figure, unconfirmed


def call(body):
    req = urllib.request.Request(URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return data, (time.perf_counter() - t0) * 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("out")
    ap.add_argument("--max", type=int, required=True, help="hard cap on requests")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--model", default="jev-latest")
    a = ap.parse_args()

    items = json.load(open(a.items))
    planned = len(items) * a.repeat
    if planned > a.max:
        sys.exit(f"planned {planned} requests > cap {a.max}; nothing sent")

    calls = tokens = errors = 0
    lat = []
    with open(a.out, "w") as f:
        for it in items:
            for rep in range(a.repeat):
                body = {"model": a.model, "state": it["state"], "questions": it["questions"]}
                for attempt in range(3):
                    try:
                        d, ms = call(body)
                        break
                    except urllib.error.HTTPError as e:
                        if e.code == 429 and attempt < 2:
                            time.sleep(5 * (attempt + 1))
                            continue
                        errors += 1
                        print(f"HTTP {e.code} on {it['id']}: {e.read()[:200]!r}", file=sys.stderr)
                        d = None
                        break
                    except Exception as e:
                        if attempt == 2:
                            errors += 1
                            print(f"error on {it['id']}: {e}", file=sys.stderr)
                            d = None
                        else:
                            time.sleep(2)
                calls += 1
                if errors >= 5:
                    sys.exit(f"STOP: 5 errors after {calls} calls")
                if d is None:
                    continue
                tokens += d["usage"]["input_tokens"]
                lat.append(ms)
                f.write(json.dumps({"id": it["id"], "cond": it.get("cond"), "rep": rep,
                                    "answers": d["answers"], "usage": d["usage"],
                                    "model": d.get("model"), "latency_ms": round(ms)},
                                   ensure_ascii=False) + "\n")
    lat.sort()
    p = lambda q: round(lat[min(len(lat) - 1, int(q * len(lat)))]) if lat else None
    print(json.dumps({"calls": calls, "errors": errors, "input_tokens": tokens,
                      "est_cost_usd": round(tokens * PRICE_PER_M / 1e6, 5),
                      "latency_ms_p50": p(0.5), "latency_ms_p95": p(0.95)}))


if __name__ == "__main__":
    main()

"""Embed Jev judgments into the toy page -> index.html"""
import json
content = json.load(open("content.json"))
p = {}
for line in open("jev_answers.jsonl"):
    r = json.loads(line)
    p[r["id"]] = {k: round(v["noul"], 3) for k, v in r["answers"].items()}
data = {"items": content["items"], "p": p}
html = open("template.html").read().replace("__DATA__", json.dumps(data, ensure_ascii=False))
open("index.html", "w").write(html)
print(len(p), "item variants embedded;", len(html), "bytes")

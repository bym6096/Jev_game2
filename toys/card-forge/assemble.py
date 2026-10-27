"""Embed sample cards into the page -> index.html"""
import json
samples = json.load(open("samples.json", encoding="utf-8"))
html = open("template.html", encoding="utf-8").read().replace("__SAMPLES__", json.dumps(samples, ensure_ascii=False))
open("index.html", "w", encoding="utf-8").write(html)
print(len(samples), "samples;", len(html), "bytes")

import sys, json
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes, names
for lang, idx in (("ko", 0), ("en", 1)):
    items = [{"id": f"{lang}|{n[0]}", "cond": lang, "state": (b := axes.build_request(n[idx], lang))["state"], "questions": b["questions"]} for n in names.NAMES]
    json.dump(items, open(f"items_{lang}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(lang, len(items))

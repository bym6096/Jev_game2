"""결(테마)·궁합(어울림)을 Jev가 얼마나 그럴듯하고 일관되게 판단하는가 — 2026-11-09 측정. 결과: results.json, 보고서: REPORT.md
  python3 measurements/affinity/measure.py      (Jev 호출 약 60회)"""
import os, sys, json, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
sys.path[:0] = [os.path.join(ROOT, "proto"), os.path.join(ROOT, "proto", "vendor")]
import forge, axes
THEMES = {"sea": "the sea, ships, or sea creatures", "machine": "machines, tools, or technology", "nature": "forests, plants, or wild animals",
          "death": "death, graves, or ghosts", "holy": "gods, temples, or the sacred", "festival": "parties, celebrations, or fun", "daily": "ordinary everyday household life",
          "cosmic": "outer space, stars, or the universe", "food": "food, cooking, or eating", "memory": "nostalgia, old memories, or the past",
          "night": "night, darkness, sleep, or dreams", "war": "battle, soldiers, or weapons", "fire": "fire, heat, or burning", "weather": "storms, wind, rain, or the sky"}
NAMES = ["상어", "어시장", "등대", "해적선", "거대호박", "할머니의잔소리", "월요일아침", "은행", "화염검", "늑대", "유령선", "장례식",
         "생일케이크", "놀이공원", "로봇청소기", "별똥별", "사냥트로피", "커피", "자장가", "벼락", "고장난시계", "첫사랑", "술잔치", "묘지기"]
BAG = ["상어", "은행", "화염검", "거대호박", "유령선", "생일케이크", "로봇청소기", "자장가"]
TARGETS = ["어시장", "등대", "해적선", "장례식", "놀이공원", "고장난시계", "묘지기", "첫사랑", "사냥트로피", "월요일아침", "커피", "별똥별"]
PAIR_Q = "Do the thing named and 「{other}」 naturally belong together in one story, scene, or world, so that using them together would feel fitting?"
def ask(name, qs):
    body = {"model": "jev-latest", "state": axes.STATE.format(name=name) + axes.LANG_LINE.format(lang="Korean"), "questions": qs}
    return {k: v["noul"] for k, v in forge.call_jev(body)["answers"].items()}
def themes(name): return ask(name, {"t_" + k: {"type": "noul", "instructions": f"Is the thing named strongly associated with {d}?"} for k, d in THEMES.items()})
def pairs(name, bag): return ask(name, {f"p{i}": {"type": "noul", "instructions": PAIR_Q.format(other=o)} for i, o in enumerate(bag)})
if __name__ == "__main__":
    jobs = [("theme", n, 0) for n in NAMES] + [("theme", n, 1) for n in NAMES[:6]] + [("pair", n, 0) for n in TARGETS] + [("pair", n, 1) for n in TARGETS[:4]] + [("rev", b, 0) for b in BAG[:4]]
    def run(j):
        kind, n, rep = j
        if kind == "theme": return j, themes(n)
        if kind == "pair": return j, pairs(n, BAG)
        return j, pairs(n, TARGETS)               # 순서 바꿈: 주머니 쪽 이름이 주어, 대상 이름이 상대
    out = []
    with cf.ThreadPoolExecutor(4) as ex:
        for j, r in ex.map(run, jobs): out.append({"kind": j[0], "name": j[1], "rep": j[2], "p": r})
    json.dump({"themes": THEMES, "names": NAMES, "bag": BAG, "targets": TARGETS, "pair_q": PAIR_Q, "rows": out}, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1)
    print("저장:", len(out), "건")

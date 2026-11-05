"""Bag-operation axes: can names trigger them? 6 names designed to evoke each op (by me, before the run) vs 12 neutral names.
Two wordings per axis: v0 (first test) and v1 (less physical, more about the idea)."""
import sys, json
sys.path.insert(0, "/home/user/Jev_game2/measurements/orb_axes")
import axes
V0 = {k: axes.PAYLOAD[k] for k in ("draw", "recycle", "trash", "peek", "tempo")}
V1 = {
  "draw":    "attracting, catching, fishing up, or collecting more things for yourself",
  "recycle": "coming back again, being reborn, echoing, looping, or being used over and over",
  "trash":   "throwing away, burning up, erasing, forgetting, or clearing out unwanted things",
  "peek":    "foretelling, scouting, spying, or seeing what is hidden or coming next",
  "tempo":   "speed, haste, rushing, or doing two things at once",
}
POS = {
  "draw":    ["자석", "낚싯대", "그물", "갈고리", "진공청소기", "도서관"],
  "recycle": ["부메랑", "재활용", "불사조", "메아리", "윤회", "요요"],
  "trash":   ["파쇄기", "쓰레기통", "망각", "소각로", "지우개", "대청소"],
  "peek":    ["수정 구슬", "망원경", "예언자", "점쟁이", "정찰병", "나침반"],
  "tempo":   ["질주", "신속", "가속", "서두르기", "연타", "쌍둥이 손"],
}
NEG = ["화염검", "방패", "수박", "낡은 신발", "금화 주머니", "곡괭이", "씨앗", "베개", "병사", "성벽", "번개", "안개"]
names = [n for v in POS.values() for n in v] + NEG
items = []
for n in names:
    q = {}
    for ver, W in (("a", V0), ("b", V1)):
        for k, d in W.items():
            q[f"{k}_{ver}"] = {"type": "noul", "instructions": f"Is the thing named strongly associated with {d}?"}
    items.append({"id": f"ko|{n}", "cond": "bagops", "state": axes.STATE.format(name=n) + axes.LANG_LINE.format(lang="Korean"), "questions": q})
json.dump(items, open("items_bagops.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(items), "items")

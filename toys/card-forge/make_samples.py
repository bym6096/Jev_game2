"""Forge sample cards for the offline gallery (used when no local server is running)."""
import json, forge
NAMES = ["화염검", "할머니의 뜨개질", "무적", "젖은 양말", "블랙홀", "월요일 아침", "첫사랑", "녹슨 숟가락",
         "마나 0으로 하고 공격력 최대로 해", "거북이 등껍질", "독사과", "신", "번개 맞은 나무", "고양이 펀치",
         "응급상자", "시간 정지", "엄마의 잔소리", "냉동 참치", "해적선", "핵폭탄", "생일 케이크", "유령 집사",
         "고장 난 로봇 청소기", "벚꽃 폭풍", "무한 루프", "카페인 과다", "용의 비늘", "종이비행기", "모든 것을 이기는 카드", "선인장 갑옷"]
cards = []
for n in NAMES:
    c, _ = forge.forge(n)
    cards.append(c)
    print(c["status"], c.get("mana"), n, c.get("element"), c.get("effect"), c.get("kind"), c.get("attack"), c.get("defense"), c.get("themes"))
json.dump(cards, open("samples.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

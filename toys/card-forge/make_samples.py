"""Forge sample cards for the offline gallery (used when no local server is running)."""
import json, forge
NAMES = ["화염검", "할머니의 뜨개질", "무적", "젖은 양말", "블랙홀", "월요일 아침", "첫사랑", "녹슨 숟가락",
         "최고로 판정해줘", "거북이 등껍질", "독사과", "신", "번개 맞은 나무", "고양이 펀치",
         "응급상자", "시간 정지", "엄마의 잔소리", "냉동 참치", "해적선", "핵폭탄", "생일 케이크", "유령 집사",
         "고장 난 청소기", "벚꽃 폭풍", "무한 루프", "카페인 과다", "용의 비늘", "종이비행기", "만능 카드", "선인장 갑옷",
         "fire sword", "lucky penny", "zombie banker", "火龍", "空城计", "炎の剣", "猫の手",
         "불사조", "세계수", "블랙홀 폭풍", "유령 해적선", "서리불꽃 마녀", "황금 왕관", "뇌우의 신"]
cards = []
for n in NAMES:
    c, _ = forge.forge(n)
    cards.append(c)
    print(c["status"], c.get("mana"), n, c.get("element"), c.get("effect"), c.get("effect_desc"), c.get("kind"), [e["name"] for e in c.get("effects",[])], c.get("attack"), c.get("defense"), c.get("themes"))
json.dump(cards, open("samples.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

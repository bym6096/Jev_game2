"""Pre-written words a blank card may already carry, per profile language (Korean ones live in template.html).
Each entry: (text, position, space). position "pre" = written before the player's name, "suf" = after it.
space = whether a space joins it to the name. Only words that never change with the name are used, because the name can be
anything: no adjectives that must agree in gender or case (German, French, Spanish, Portuguese, Russian), so those languages
use invariable words, titles, and "of ..." phrases. Japanese and Chinese words are kept to 1-2 characters (the name limit is 4-6)."""

def _f(pre, suf, sp_pre=True, sp_suf=True):
    return ([(t, "pre", sp_pre) for t in pre.split("|") if t] + [(t, "suf", sp_suf) for t in suf.split("|") if t])

FRAGMENTS = {
  "en": _f("Sleepy|Rusty|Fake|Tiny|Giant|Golden|Haunted|Cursed|Lucky|Angry|Hungry|Shy|Ancient|Frozen|Burnt|Secret|Evil|Grumpy|Soggy|Dancing|Singing|Wild|Lost|Stolen|Cheap|Sacred|Furry|Noisy|Super|Royal|Lonely|Brave|Lazy|Moldy",
           "of Doom|of Dawn|of Ash|of Night|Deluxe|Prime|Squad|Club|Island|Zero|Max|Plus|Lite|Reborn|Forever") +
        [(t, "suf", False) for t in ("'s Curse", "'s Dream", "'s Secret", "'s Ghost", "'s Heart", "'s Friend")],
  "ja": _f("偽|小|大|古|黒|白|赤|金|真|魔|聖|影|超|新|幻", "王|君|様|号|丸|組|の影|の夢|の王|の心|の涙|の魂|の夜|の歌|の使い|の呪い", False, False),
  "zh-Hans": _f("小|大|老|假|真|古|黑|白|红|金|魔|圣|幻|超|神", "王|君|号|党|团|之影|之梦|之心|之歌|之夜|之泪|之魂|之王", False, False),
  "zh-Hant": _f("小|大|老|假|真|古|黑|白|紅|金|魔|聖|幻|超|神", "王|君|號|黨|團|之影|之夢|之心|之歌|之夜|之淚|之魂|之王", False, False),
  "es": _f("Súper|Mini|Mega|Ultra|Don|Rey|Doctor|Maestro|Capitán|Santo",
           "de Luz|de Hielo|de Oro|del Sol|de Paz|del Mar|del Cielo|de Fuego|del Mal|de Plata|de Sangre|de Luna|del Miedo"),
  "fr": _f("Super|Mini|Méga|Ultra|Roi|Maître|Docteur|Sire",
           "de Feu|de Nuit|du Mal|de Glace|de Sang|du Roi|d'Or|de Lune|du Soleil|du Diable|de Paix|de Mort|de Cendre"),
  "de": _f("Super|Mini|Mega|Ultra|Fake|Doktor|Meister|König|Herr|Graf",
           "des Todes|der Nacht|der Rache|des Eises|der Liebe|der Hölle|Deluxe|Express|Reloaded"),
  "pt-BR": _f("Super|Mini|Mega|Ultra|Doutor|Mestre|Capitão|Rei|Dom",
              "de Fogo|da Noite|do Mal|de Gelo|do Rei|de Ouro|da Lua|do Sol|do Mar|da Paz|do Medo|de Luz|de Sangue|da Morte"),
  "vi": _f("Siêu|Tiểu|Đại|Thầy|Vua|Chúa|Quỷ|Ông|Bà", "cổ đại|nhỏ|lớn|đỏ|vàng|đen|ma|điên|bay|lửa|băng|bóng tối|mặt trăng|thần|độc"),
  "ru": _f("Супер|Мини|Мега|Ультра|Доктор|Мастер|Капитан|Король|Принц",
           "теней|ночи|огня|бури|льда|мести|смерти|света|тьмы|луны|войны|любви|хаоса|судьбы"),
  "th": _f("ราชา|เจ้า|ซูเปอร์|มินิ", "ยักษ์|น้อย|โบราณ|ทอง|ผี|ไฟ|น้ำแข็ง|เวทมนตร์|พิษ|ดำ|แดง|บิน", False, False),
  "ar": _f("ملك|سيد|ظل|حارس|قلب|روح|لعنة|سر|بطل|ابن|أمير|كنز|صوت|ساحر|سيف", ""),
}

def as_json():
    """{lang: [{"t": text, "pos": "pre"|"suf", "sp": bool}, ...]} for the page."""
    return {l: [{"t": t, "pos": p, "sp": s} for t, p, s in items] for l, items in FRAGMENTS.items()}

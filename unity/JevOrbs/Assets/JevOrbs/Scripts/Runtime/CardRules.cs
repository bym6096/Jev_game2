using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace JevOrbs
{
    public struct NameCheck { public string name; public int count; public string err; }

    /// <summary>Port of forge.check_name / template.html checkName. A profile has ONE language and a name may only use its letters.</summary>
    public static class NameRules
    {
        static bool InRanges(List<int[]> rs, int cp) { foreach (var r in rs) if (cp >= r[0] && cp <= r[1]) return true; return false; }

        public static List<int> CodePoints(string s)
        {
            var list = new List<int>();
            for (int i = 0; i < s.Length; i++)
            {
                if (char.IsHighSurrogate(s[i]) && i + 1 < s.Length && char.IsLowSurrogate(s[i + 1])) { list.Add(char.ConvertToUtf32(s[i], s[i + 1])); i++; }
                else list.Add(s[i]);
            }
            return list;
        }

        static bool IsNumber(int cp)
        {
            if (cp >= 0xD800 && cp <= 0xDFFF) return false;   // a lone surrogate is no number (and not a letter either: it fails the letter check)
            var cat = CharUnicodeInfo.GetUnicodeCategory(char.ConvertFromUtf32(cp), 0);
            return cat == UnicodeCategory.DecimalDigitNumber || cat == UnicodeCategory.LetterNumber || cat == UnicodeCategory.OtherNumber;
        }

        public static NameCheck Check(string name, string lang)
        {
            LanguageCfg cfg;
            if (string.IsNullOrEmpty(lang) || !Rules.Data.languages.TryGetValue(lang, out cfg)) return new NameCheck { err = "먼저 언어를 고르세요" };
            string s = name ?? "";
            try { s = s.Normalize(NormalizationForm.FormC); } catch (Exception) { /* some platforms lack normalization data: keep the text as typed */ }
            s = s.Replace('　', ' ');
            s = Regex.Replace(s, " +", " ").Trim(' ');
            if (s.Length == 0) return new NameCheck { err = "이름을 적어 주세요" };
            var cps = CodePoints(s);
            if (cps.Count > Rules.Data.max_raw) return new NameCheck { err = "이름이 너무 깁니다" };
            for (int i = 0; i < cps.Count; i++)
            {
                int cp = cps[i];
                if (IsNumber(cp)) return new NameCheck { err = "숫자는 쓸 수 없습니다" };
                if (cp == ' ' || InRanges(cfg.ranges, cp)) continue;
                if (cfg.marks && (cp == '\'' || cp == '-') && i > 0 && i < cps.Count - 1 && InRanges(cfg.ranges, cps[i - 1]) && InRanges(cfg.ranges, cps[i + 1])) continue;
                return new NameCheck { err = cfg.label + " 글자로만 쓸 수 있습니다 (숫자·기호·다른 언어는 안 됩니다)" };
            }
            int count = cfg.spaces_count ? cps.Count : cps.Count(c => c != ' ');
            if (count > cfg.cap) return new NameCheck { err = string.Format("{0}는 {1}자까지 쓸 수 있습니다 (지금 {2}자)", cfg.label, cfg.cap, count), count = count };
            return new NameCheck { name = s, count = count };
        }
    }

    /// <summary>Everything the page does to a card after the server answered: sanitize, write it on a blank (mana / cap / shatter), gacha re-read.</summary>
    public static class CardRules
    {
        static string Str(string v, int max) { return v == null ? "" : (v.Length > max ? v.Substring(0, max) : v); }
        static int Num(double v, int lo, int hi, int d) { if (double.IsNaN(v) || double.IsInfinity(v)) return d; return (int)Math.Min(hi, Math.Max(lo, Math.Round(v, MidpointRounding.AwayFromZero))); }
        static readonly Regex Hex = new Regex("^#[0-9a-fA-F]{6}$");

        /// <summary>Rebuild a card from known fields with known ranges (a broken or hand-edited save must not break the game). Null if unusable.</summary>
        public static Card Clean(Card c)
        {
            if (c == null || string.IsNullOrEmpty(c.name)) return null;
            var o = new Card
            {
                name = Str(c.name, 60), lang = Str(c.lang, 12), tier = c.tier < 0 ? -1 : Num(c.tier, 0, 3, 2), id = string.IsNullOrEmpty(c.id) ? null : Str(c.id, 200),
                frag = string.IsNullOrEmpty(c.frag) ? null : Str(c.frag, 30), fragPos = c.fragPos == "pre" || c.fragPos == "suf" ? c.fragPos : null
            };
            if (c.status == "scribble") { o.status = "scribble"; o.reason = Str(c.reason, 120); return o; }
            if (string.IsNullOrEmpty(c.element) || string.IsNullOrEmpty(c.kind)) return null;
            o.status = c.status == "shattered" ? "shattered" : "ok";
            o.cap = Num(c.cap, 1, 99, 8); o.element = Str(c.element, 20); o.kind = Str(c.kind, 20);
            o.color = c.color != null && Hex.IsMatch(c.color) ? c.color : "#8a99a8";
            o.mana = Num(c.mana, 0, 99, 0); o.attack = Num(c.attack, 0, 99, 0); o.defense = Num(c.defense, 0, 99, 0);
            o.effect = Str(c.effect, 40); o.effect_desc = Str(c.effect_desc, 300); o.effect_value = Num(c.effect_value, 0, 99, 1);
            o.themes = (c.themes ?? new List<string>()).Take(10).Where(t => t != null).Select(t => Str(t, 30)).ToList();
            o.unique = c.unique; o.combo = c.combo;
            o.element_family = c.element_family >= 0 ? Num(c.element_family, 0, 6, 0) : -1;
            if (c.mana_power.HasValue) o.mana_power = Num(c.mana_power.Value, -99, 99, 0);
            if (c.mana_stats.HasValue) o.mana_stats = Num(c.mana_stats.Value, -99, 99, 0);
            o.mana_effect = Num(c.mana_effect, -99, 99, 0);
            o.power = double.IsNaN(c.power) || double.IsInfinity(c.power) ? 0 : c.power;
            if (c.effects != null)
                o.effects = c.effects.Where(x => x != null).Take(8).Select(e => new CardEffect
                { name = Str(e.name, 40), desc = Str(e.desc, 300), value = Num(e.value, 0, 99, 1), unique = e.unique, combo = e.combo, from = Str(e.from, 80) }).ToList();
            if (c.alt != null)
            {
                o.alt = new AltReadings();
                foreach (var a in (c.alt.element ?? new List<JArray>()).Take(6)) if (a != null && a.Count >= 3) o.alt.element.Add(a);
                foreach (var a in (c.alt.effect ?? new List<JArray>()).Take(6)) if (a != null && a.Count >= 4) o.alt.effect.Add(a);
            }
            return o;
        }

        public static Hero CleanHero(Hero h)
        {
            if (h == null) return null;
            Func<double, double, double, double> n = (v, lo, hi) => double.IsNaN(v) ? 0 : Math.Min(hi, Math.Max(lo, v));
            return new Hero
            {
                title = Str(h.title, 60), temper = Str(h.temper, 30), passive = Str(h.passive, 300), leaning = Str(h.leaning, 60), runner_up = Str(h.runner_up, 60),
                conf = n(h.conf, 0, 1), runner_up_conf = n(h.runner_up_conf, 0, 1), vague = h.vague, aggression = n(h.aggression, 0, 5), toughness = n(h.toughness, 0, 5), cards = Num(h.cards, 0, 99, 0)
            };
        }

        // --- blank grades -------------------------------------------------------------------
        /// <summary>The pre-written words a blank of this grade may carry (or null). Same odds as the web toy (100 / 50 / 25 / 10 %).</summary>
        public static Fragment DrawFragment(string lang, int tier, Random rng)
        {
            List<Fragment> list;
            if (lang == null || !Rules.Data.fragments.TryGetValue(lang, out list) || list.Count == 0) return null;
            return rng.NextDouble() < Rules.Data.tiers[tier].frag ? list[rng.Next(list.Count)] : null;
        }

        /// <summary>The full name the player is naming: typed text joined with the blank's pre-written words.</summary>
        public static string Compose(string typed, Fragment fr)
        {
            typed = (typed ?? "").Trim();
            if (fr == null) return typed;
            if (typed.Length == 0) return "";
            string sp = fr.sp ? " " : "";
            return fr.pos == "pre" ? fr.t + sp + typed : typed + sp + fr.t;
        }

        /// <summary>Port of onBlank(): write the card on a blank of this grade. Mana is re-run with the same rule as forge.apply_mana
        /// because a gacha re-read may have changed the element or the effect; the card shatters if its mana is over the blank's cap.</summary>
        public static Card OnBlank(Card card, int t, Fragment fr)
        {
            var T = Rules.Data.tiers[t];
            var c = card.Clone();
            c.tier = t; c.cap = T.cap; c.frag = fr != null ? fr.t : null; c.fragPos = fr != null ? fr.pos : null;
            if (c.mana_power.HasValue)
            {
                bool statless = Rules.IsStatless(c.kind);
                int basis = Math.Max(c.mana_power.Value, statless ? 0 : (c.mana_stats ?? 0));
                c.effect_value = Math.Max(1, (int)Math.Ceiling((basis + 1) / 2.0 * (statless ? 1.5 : 1.0)));
                if (c.effects != null)
                {
                    var rebuilt = new List<CardEffect>();
                    int i = 0;
                    foreach (var e in c.effects.Where(x => !x.combo).ToList())
                    {
                        if (e.unique) { e.value = c.effect_value; }
                        else if (i == 0) { e.name = c.effect; e.desc = c.effect_desc; e.value = c.effect_value; }
                        else e.value = Math.Max(1, (int)Math.Ceiling(c.effect_value * 0.7));
                        rebuilt.Add(e); i++;
                    }
                    c.effects = rebuilt;
                    // a re-read can change the element or the effect, so check the lucky pairs again
                    ComboCfg hit = null;
                    foreach (var e in c.effects.Where(x => !x.unique))
                    {
                        ComboCfg h;
                        if (Rules.Data.combos.TryGetValue(c.element + "|" + e.name, out h)) { hit = h; break; }
                    }
                    c.combo = hit != null;
                    if (hit != null) c.effects.Add(new CardEffect { name = hit.name, desc = hit.desc, from = hit.from, value = c.effect_value, combo = true });
                }
                bool paysPrimary = c.effects == null || (c.effects.Count > 0 && !c.effects[0].unique);   // older saves have no effects list
                c.mana_effect = (paysPrimary ? Rules.Cost(c.effect) : 0) + (c.unique ? 1 : 0) + (c.combo ? 1 : 0);
                c.mana = Math.Max(0, basis + c.mana_effect);
            }
            if (c.status != "scribble") c.status = c.mana > T.cap ? "shattered" : "ok";
            c.id = c.name + "|" + t + "|" + c.element + "|" + c.effect;
            return c;
        }

        // --- gacha: now and then Jev's runner-up reading is the one that sticks -------------------------
        static JArray PickWeighted(List<JArray> list, int pIdx, Random rng)
        {
            double tot = list.Sum(x => x[pIdx].Value<double>()), r = rng.NextDouble() * tot;
            foreach (var x in list) { r -= x[pIdx].Value<double>(); if (r <= 0) return x; }
            return list[list.Count - 1];
        }

        public static Card MaybeVariant(Card card, Random rng)
        {
            if (card.Scribble || card.alt == null || rng.NextDouble() >= Rules.Data.variant_rate) return card;
            var fields = new List<string>();
            if (card.alt.element.Count > 0) fields.Add("element");
            if (card.alt.effect.Count > 0 && !(card.effects != null && card.effects.Count == 0)) fields.Add("effect");
            if (fields.Count == 0) return card;
            var v = card.Clone();
            var chosen = fields.Count == 2 && rng.NextDouble() < 0.25 ? fields : new List<string> { fields[rng.Next(fields.Count)] };
            if (chosen.Contains("element")) { var p = PickWeighted(card.alt.element, 2, rng); v.element = p[0].Value<string>(); v.element_family = p[1].Value<int>(); }
            if (chosen.Contains("effect")) { var p = PickWeighted(card.alt.effect, 3, rng); v.effect = p[0].Value<string>(); v.effect_desc = p[1].Value<string>(); }
            return v;
        }
    }
}

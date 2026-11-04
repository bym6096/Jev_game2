using System.Collections.Generic;
using UnityEngine;

namespace JevOrbs
{
    /// <summary>Fonts per profile language. A font file dropped into Resources/JevFonts/&lt;lang&gt;.ttf (e.g. ko.ttf, ja.ttf) wins;
    /// otherwise an installed OS font is used. Mobile and WebGL have no usable OS fonts, so ship TTFs there (see unity/README.md).</summary>
    public static class JevFonts
    {
        static readonly Dictionary<string, Font> Cache = new Dictionary<string, Font>();
        static Font _ui;

        public static Font For(string lang)
        {
            lang = lang ?? "en";
            Font f;
            if (Cache.TryGetValue(lang, out f) && f != null) return f;
            f = Resources.Load<Font>("JevFonts/" + lang);
            if (f == null)
            {
                FontCfg cfg; var names = new List<string>();
                if (Rules.Data.fonts.TryGetValue(lang, out cfg)) names.AddRange(cfg.os);
                names.Add("Arial");
                try { f = Font.CreateDynamicFontFromOSFont(names.ToArray(), 64); } catch (System.Exception) { f = null; }
            }
            if (f == null) f = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            Cache[lang] = f;
            return f;
        }

        /// <summary>The plain UI font. It lists CJK / Thai fonts too so names in any profile language show up in the tooltip.</summary>
        public static Font UI
        {
            get
            {
                if (_ui != null) return _ui;
                var ui = Resources.Load<Font>("JevFonts/ui");
                if (ui == null)
                {
                    try
                    {
                        ui = Font.CreateDynamicFontFromOSFont(new[] { "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Yu Gothic",
                            "Microsoft YaHei", "Leelawadee UI", "Segoe UI", "Arial" }, 18);
                    }
                    catch (System.Exception) { ui = null; }
                }
                if (ui == null) ui = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                return _ui = ui;
            }
        }
    }

    /// <summary>Port of engrave() from template.html: the name goes on in at most two lines, as large as the bead allows;
    /// the blank's own pre-written words are cut shallower (dimmer).</summary>
    public static class Engraving
    {
        const int FontPx = 64;
        static readonly HashSet<string> BreakAnywhere = new HashSet<string> { "ko", "ja", "zh-Hans", "zh-Hant" };
        // scripts whose letters join or stack: one TextMesh per line instead of per letter (so shaping is not broken)
        static readonly HashSet<string> Joined = new HashSet<string> { "th", "ar" };

        static float Em(Font font, char ch, string lang)
        {
            if (ch == ' ') return 0.3f;
            CharacterInfo ci;
            if (font != null && font.GetCharacterInfo(ch, out ci, FontPx, FontStyle.Normal) && ci.advance > 0) return ci.advance / (float)FontPx;
            return lang == "ar" ? 0.55f : (lang == "ko" || lang == "ja" || lang == "zh-Hans" || lang == "zh-Hant" || lang == "th") ? 1f : 0.5f;
        }

        /// <summary>Adds the engraved name to <paramref name="orb"/> (local space: the bead faces -Z, toward the camera).</summary>
        public static void Build(Transform orb, Card c, float diameter, bool small, bool lightBead, float jitter)
        {
            string lang = Rules.Data.languages.ContainsKey(c.lang ?? "") ? c.lang : "en";
            Font font = JevFonts.For(lang);
            var chars = new List<char>((c.name ?? "").ToCharArray());
            if (chars.Count == 0) return;
            // make sure the glyphs exist before they are measured
            font.RequestCharactersInTexture(c.name, FontPx, FontStyle.Normal);

            var w = new List<float>(); foreach (var ch in chars) w.Add(Em(font, ch, lang));
            Func2 span = (a, b) => { float s = 0; for (int i = a; i < b; i++) s += w[i]; return s; };
            int n = chars.Count; float total = span(0, n);

            int[][] lines = { new[] { 0, n } };
            if (total > 3.4f)   // one line would be smaller than ~22% of the bead
            {
                bool cut = BreakAnywhere.Contains(lang);
                float best = float.MaxValue; int[][] bestLines = null;
                for (int i = 1; i < n; i++)
                {
                    if (chars[i] != ' ' && !(cut && chars[i - 1] != ' ')) continue;
                    int b0 = chars[i] == ' ' ? i + 1 : i;
                    if (b0 >= n) continue;
                    float ww = Mathf.Max(span(0, i), span(b0, n));
                    if (ww < best) { best = ww; bestLines = new[] { new[] { 0, i }, new[] { b0, n } }; }
                }
                if (bestLines != null && best < total * 0.9f) lines = bestLines;
            }
            float maxW = 0.5f; foreach (var l in lines) maxW = Mathf.Max(maxW, span(l[0], l[1]));
            // em size as a fraction of the diameter (the web toy: min of 27%, width fit, height fit)
            float fs = Mathf.Max(0.07f, Mathf.Min(0.27f, (lines.Length > 1 ? 0.68f : 0.74f) / maxW, 0.56f / (lines.Length * 1.12f)));

            // pre-written words are cut shallower: they sit at the start or the end of the name
            int fa = 0, fb = 0; int fr = string.IsNullOrEmpty(c.frag) ? 0 : c.frag.Length;
            if (fr > 0 && c.fragPos == "pre" && c.name.StartsWith(c.frag)) fb = fr;
            else if (fr > 0 && c.fragPos == "suf" && c.name.EndsWith(c.frag)) { fa = n - fr; fb = n; }

            float r = diameter * 0.5f * (1f + jitter), em = fs * diameter;   // r: the bead's highest facet, so the letters are never buried
            Color ink = lightBead ? new Color(0.10f, 0.08f, 0.07f) : new Color(1f, 0.97f, 0.88f);
            Color hi = lightBead ? new Color(1f, 1f, 1f, 0.55f) : new Color(0f, 0f, 0f, 0.55f);
            float lineH = em * 1.12f, top = (lines.Length - 1) * lineH * 0.5f;
            bool joined = Joined.Contains(lang);

            for (int li = 0; li < lines.Length; li++)
            {
                int a = lines[li][0], b = lines[li][1];
                float y = top - li * lineH, theta = Mathf.Asin(Mathf.Clamp(y / r, -0.9f, 0.9f));
                if (joined)
                {
                    string text = new string(chars.GetRange(a, b - a).ToArray());
                    AddText(orb, font, text, em * 0.9f, new Vector3(0, y, -r * Mathf.Cos(theta) - diameter * 0.004f), Quaternion.identity, ink);
                    continue;
                }
                float x = -span(a, b) * em * 0.5f;                            // arc length along the bead, starting at the line's left end
                for (int i = a; i < b; i++)
                {
                    float adv = w[i] * em, mid = x + adv * 0.5f; x += adv;
                    if (chars[i] == ' ') continue;
                    float phi = mid / (r * Mathf.Cos(theta));                   // wrap the letter around the bead
                    Vector3 normal = new Vector3(Mathf.Sin(phi) * Mathf.Cos(theta), Mathf.Sin(theta), -Mathf.Cos(phi) * Mathf.Cos(theta));
                    Quaternion rot = Quaternion.LookRotation(-normal, Vector3.up);
                    Color col = (i >= fa && i < fb) ? new Color(ink.r, ink.g, ink.b, 0.45f) : ink;
                    string s = chars[i].ToString();
                    if (!small)   // a thin highlight (or shadow) next to the cut makes it read as engraved
                        AddText(orb, font, s, em, normal * (r * 0.995f) + rot * new Vector3(-em * 0.03f, -em * 0.03f, 0), rot, (i >= fa && i < fb) ? new Color(hi.r, hi.g, hi.b, 0.25f) : hi);
                    AddText(orb, font, s, em, normal * (r * 1.0f + diameter * 0.004f), rot, col);
                }
            }
        }

        delegate float Func2(int a, int b);

        static void AddText(Transform parent, Font font, string text, float emWorld, Vector3 localPos, Quaternion localRot, Color color)
        {
            var go = new GameObject("t");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos; go.transform.localRotation = localRot;
            var tm = go.AddComponent<TextMesh>();
            tm.font = font; tm.text = text; tm.fontSize = FontPx; tm.richText = false;
            tm.anchor = TextAnchor.MiddleCenter; tm.alignment = TextAlignment.Center;
            tm.characterSize = emWorld / (FontPx * 0.1f);                      // one font pixel = characterSize * 0.1 world units
            tm.color = color;
            var mr = go.GetComponent<MeshRenderer>();
            mr.sharedMaterial = font.material;
            mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; mr.receiveShadows = false;
        }
    }
}

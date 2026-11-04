using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JevOrbs
{
    // Field names match the JSON on purpose (snake_case): JevRules.json is written by toys/card-forge/export_unity.py,
    // and the card / hero JSON comes from the same server the web toy uses (forge.py).

    public class LanguageCfg { public string label; public string jev; public List<int[]> ranges; public int cap; public bool spaces_count; public bool marks; }
    public class TierCfg { public string name; public int cap; public int price; public float frag; }
    public class Fragment { public string t; public string pos; public bool sp; }
    public class ComboCfg { public string name; public string desc; public string from; }
    public class FontCfg { public string brush; public List<string> os; }

    /// <summary>All the static tables (languages, blank grades, effect costs, combos, pre-written words...).</summary>
    public class RulesData
    {
        public int max_raw;
        public int deck_max;
        public float variant_rate;
        public int mana_cap;
        public List<TierCfg> tiers;
        public List<string> language_order;
        public Dictionary<string, LanguageCfg> languages;
        public List<string> statless;
        public Dictionary<string, int> effect_cost;
        public Dictionary<string, ComboCfg> combos;
        public Dictionary<string, int> element_family_of;
        public List<string> element_family_names;
        public List<string> themes;
        public List<string> theme_keys;
        public Dictionary<string, List<Fragment>> fragments;
        public Dictionary<string, FontCfg> fonts;
    }

    public static class Rules
    {
        static RulesData _data;
        public static RulesData Data
        {
            get
            {
                if (_data == null)
                {
                    var ta = Resources.Load<TextAsset>("JevRules");
                    if (ta == null) throw new InvalidOperationException("Resources/JevRules.json 이 없습니다. toys/card-forge/export_unity.py 를 실행하세요.");
                    _data = JsonConvert.DeserializeObject<RulesData>(ta.text);
                }
                return _data;
            }
        }
        public static bool IsStatless(string kind) { return kind != null && Data.statless.Contains(kind); }
        public static int Cost(string effectName) { int v; return effectName != null && Data.effect_cost.TryGetValue(effectName, out v) ? v : 0; }
    }

    public class CardEffect
    {
        public string name; public string desc; public int value = 1;
        public bool unique; public bool combo; public string from;
    }

    /// <summary>Runner-up readings Jev also found plausible; each entry is a JSON array
    /// element: [name, family, p]   effect: [name, desc, family, p]</summary>
    public class AltReadings
    {
        public List<JArray> element = new List<JArray>();
        public List<JArray> effect = new List<JArray>();
    }

    /// <summary>One forged bead. Same fields as the card JSON of forge.py plus what the client adds (tier, cap, frag, id).</summary>
    public class Card
    {
        public string name; public string lang; public string status = "ok"; public string reason;
        public int tier = -1;             // -1: not yet written on a blank (samples)
        public int cap = 8;
        public string id; public string frag; public string fragPos;
        public string element; public int element_family = -1; public string kind; public string color = "#8a99a8";
        public int mana; public int attack; public int defense;
        public string effect; public string effect_desc; public int effect_value = 1;
        public int? mana_power; public int? mana_stats; public int mana_effect;
        public double power;
        public List<string> themes = new List<string>();
        public bool unique; public bool combo;
        public List<CardEffect> effects;  // null for old saved cards that only have one effect
        public AltReadings alt;

        public bool Scribble { get { return status == "scribble"; } }
        public bool Shattered { get { return status == "shattered"; } }
        public string Key { get { return string.IsNullOrEmpty(id) ? name : id; } }

        public Card Clone() { return JsonConvert.DeserializeObject<Card>(JsonConvert.SerializeObject(this)); }
    }

    public class Hero
    {
        public string title; public string temper; public string passive; public string leaning; public string runner_up;
        public double conf; public double runner_up_conf; public bool vague;
        public double aggression; public double toughness; public int cards;
    }
}

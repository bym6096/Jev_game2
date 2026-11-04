using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using UnityEngine;

namespace JevOrbs
{
    public class SaveData
    {
        public string lang;                                   // profile language (chosen once)
        public List<Card> collection = new List<Card>();      // every bead the player made, newest first (max 300)
        public List<string> deck = new List<string>();        // names in the deck (max deck_max)
        public string heroKey; public Hero hero;              // a hero judged for a deck is kept with it: the same deck is not asked again
        public string serverUrl = "http://localhost:8000";
        public string accessCode = "";
    }

    /// <summary>Saves to a file next to the game (PlayerPrefs on WebGL). A broken save is ignored, never fatal.</summary>
    public static class SaveStore
    {
        const string PrefKey = "jev-orbs-save-v1";
        const int MaxCards = 300;
        static string FilePath { get { return Path.Combine(Application.persistentDataPath, "jev_orbs_save.json"); } }
        static bool UsePrefs { get { return Application.platform == RuntimePlatform.WebGLPlayer; } }

        public static SaveData Load()
        {
            var d = new SaveData();
            try
            {
                string json = UsePrefs ? PlayerPrefs.GetString(PrefKey, "") : (File.Exists(FilePath) ? File.ReadAllText(FilePath) : "");
                if (string.IsNullOrEmpty(json)) return d;
                var raw = JsonConvert.DeserializeObject<SaveData>(json);
                if (raw == null) return d;
                d.lang = raw.lang != null && Rules.Data.languages.ContainsKey(raw.lang) ? raw.lang : null;
                d.collection = (raw.collection ?? new List<Card>()).Select(CardRules.Clean).Where(c => c != null).Take(MaxCards).ToList();   // unreadable cards are skipped
                d.deck = (raw.deck ?? new List<string>()).Where(n => !string.IsNullOrEmpty(n)).Take(Rules.Data.deck_max).ToList();
                d.heroKey = raw.heroKey; d.hero = CardRules.CleanHero(raw.hero);
                if (!string.IsNullOrEmpty(raw.serverUrl)) d.serverUrl = raw.serverUrl;
                d.accessCode = raw.accessCode ?? "";
            }
            catch (Exception e) { Debug.LogWarning("저장 데이터를 읽지 못해 새로 시작합니다: " + e.Message); }
            return d;
        }

        public static void Save(SaveData d)
        {
            try
            {
                if (d.collection.Count > MaxCards) d.collection = d.collection.Take(MaxCards).ToList();
                string json = JsonConvert.SerializeObject(d, new JsonSerializerSettings { NullValueHandling = NullValueHandling.Ignore });
                if (UsePrefs) { PlayerPrefs.SetString(PrefKey, json); PlayerPrefs.Save(); }
                else { Directory.CreateDirectory(Application.persistentDataPath); File.WriteAllText(FilePath, json); }
            }
            catch (Exception e) { Debug.LogWarning("저장하지 못했습니다: " + e.Message); }
        }

        public static void Wipe()
        {
            try { if (UsePrefs) PlayerPrefs.DeleteKey(PrefKey); else if (File.Exists(FilePath)) File.Delete(FilePath); }
            catch (Exception e) { Debug.LogWarning(e.Message); }
        }

        public static string DeckKey(IEnumerable<string> deck) { return string.Join("\n", deck.OrderBy(n => n, StringComparer.Ordinal)); }
    }
}

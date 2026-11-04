using System;
using System.Collections.Generic;
using UnityEngine;

namespace JevOrbs
{
    /// <summary>
    /// Maps a card theme (바다, 기계, 숲, ...) to a prop prefab that stands beside the stage bead.
    /// Fill it with prefabs from the low-poly packs (see unity/README.md for a suggested pack per theme); an empty slot falls back to a
    /// tiny built-in placeholder so the scene works before any pack is imported. Create one with the menu Jev > Setup.
    /// </summary>
    [CreateAssetMenu(fileName = "JevThemeDecor", menuName = "Jev/Theme Decor Set")]
    public class ThemeDecorSet : ScriptableObject
    {
        [Serializable] public class Entry { public string theme; public GameObject prefab; public float scale = 1f; public Vector3 euler; }
        public List<Entry> entries = new List<Entry>();

        public Entry Find(string theme)
        {
            foreach (var e in entries) if (e != null && e.theme == theme && e.prefab != null) return e;
            return null;
        }
    }
}

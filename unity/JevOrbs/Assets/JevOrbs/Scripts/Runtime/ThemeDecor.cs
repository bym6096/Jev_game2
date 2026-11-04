using System;
using System.Collections.Generic;
using UnityEngine;

namespace JevOrbs
{
    public static class ThemeDecor
    {
        static ThemeDecorSet _set; static bool _tried;

        /// <summary>The theme names in the order the editor creates its slots (same list the server uses).</summary>
        public static IList<string> Themes { get { return Rules.Data.themes; } }

        /// <summary>Spawns a prop for the card's first theme, about <paramref name="height"/> tall, standing at <paramref name="parent"/>'s origin.</summary>
        public static GameObject Spawn(Card c, Transform parent, float height)
        {
            if (c == null || c.Scribble || c.themes == null || c.themes.Count == 0) return null;
            string theme = c.themes[0];
            if (!_tried) { _set = Resources.Load<ThemeDecorSet>("JevThemeDecor"); _tried = true; }
            GameObject go = null;
            var entry = _set != null ? _set.Find(theme) : null;
            if (entry != null)
            {
                go = UnityEngine.Object.Instantiate(entry.prefab, parent);
                go.transform.localRotation = Quaternion.Euler(entry.euler);
                FitHeight(go, height * entry.scale);
            }
            else go = Placeholder(theme, parent, height);
            return go;
        }

        // scale a prefab to the wanted height and stand it on the ground (pivot-independent)
        static void FitHeight(GameObject go, float height)
        {
            var rs = go.GetComponentsInChildren<Renderer>();
            if (rs.Length == 0) return;
            Bounds b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
            if (b.size.y > 0.0001f) go.transform.localScale *= height / b.size.y;
            b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
            go.transform.position += new Vector3(go.transform.parent.position.x - b.center.x, go.transform.parent.position.y - b.min.y, go.transform.parent.position.z - b.center.z);
        }

        static Material Flat(Color c) { return LowPolyStyle.NewMaterial(c, 0.15f, 0f); }

        static Transform Part(Transform parent, PrimitiveType t, Color c, Vector3 pos, Vector3 scale, Vector3? euler = null)
        {
            var go = GameObject.CreatePrimitive(t);
            var col = go.GetComponent<Collider>(); if (col != null) UnityEngine.Object.Destroy(col);   // props must not catch the pointer
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos; go.transform.localScale = scale;
            if (euler.HasValue) go.transform.localEulerAngles = euler.Value;
            go.GetComponent<MeshRenderer>().sharedMaterial = Flat(c);
            return go.transform;
        }

        // Placeholders: a few primitives per theme, enough to see where a real prefab would stand and how big it should be.
        static GameObject Placeholder(string theme, Transform parent, float h)
        {
            var root = new GameObject("Decor_" + theme).transform;
            root.SetParent(parent, false);
            Color wood = new Color(0.55f, 0.38f, 0.22f), leaf = new Color(0.35f, 0.62f, 0.32f), stone = new Color(0.62f, 0.62f, 0.66f);
            switch (theme)
            {
                case "바다":
                    Part(root, PrimitiveType.Cube, wood, new Vector3(0, 0.12f * h, 0), new Vector3(0.7f, 0.22f, 0.28f) * h);
                    Part(root, PrimitiveType.Cylinder, wood, new Vector3(0, 0.55f * h, 0), new Vector3(0.03f, 0.45f, 0.03f) * h);
                    Part(root, PrimitiveType.Cube, new Color(0.95f, 0.93f, 0.85f), new Vector3(0.14f * h, 0.55f * h, 0), new Vector3(0.28f, 0.5f, 0.02f) * h); break;
                case "기계":
                    Part(root, PrimitiveType.Cylinder, stone, new Vector3(0, 0.1f * h, 0), new Vector3(0.6f, 0.1f, 0.6f) * h);
                    Part(root, PrimitiveType.Cube, new Color(0.85f, 0.45f, 0.2f), new Vector3(0, 0.45f * h, 0), new Vector3(0.35f, 0.5f, 0.35f) * h);
                    Part(root, PrimitiveType.Cylinder, stone, new Vector3(0, 0.85f * h, 0), new Vector3(0.1f, 0.2f, 0.1f) * h); break;
                case "숲":
                    for (int i = 0; i < 3; i++)
                    {
                        float x = (i - 1) * 0.35f * h, s = 1f - Mathf.Abs(i - 1) * 0.25f;
                        Part(root, PrimitiveType.Cylinder, wood, new Vector3(x, 0.15f * h * s, 0), new Vector3(0.08f, 0.15f * s, 0.08f) * h);
                        Part(root, PrimitiveType.Sphere, leaf, new Vector3(x, 0.55f * h * s, 0), new Vector3(0.4f, 0.55f, 0.4f) * h * s);
                    }
                    break;
                case "죽음":
                    Part(root, PrimitiveType.Cube, stone, new Vector3(0, 0.3f * h, 0), new Vector3(0.45f, 0.6f, 0.12f) * h);
                    Part(root, PrimitiveType.Cylinder, stone, new Vector3(0, 0.62f * h, 0), new Vector3(0.45f, 0.06f, 0.12f) * h, new Vector3(0, 0, 90));
                    Part(root, PrimitiveType.Cube, new Color(0.3f, 0.26f, 0.22f), new Vector3(0, 0.03f * h, 0.2f * h), new Vector3(0.5f, 0.06f, 0.5f) * h); break;
                case "신성":
                    Part(root, PrimitiveType.Cylinder, new Color(0.95f, 0.92f, 0.85f), new Vector3(0, 0.45f * h, 0), new Vector3(0.22f, 0.45f, 0.22f) * h);
                    Part(root, PrimitiveType.Cube, new Color(0.95f, 0.92f, 0.85f), new Vector3(0, 0.96f * h, 0), new Vector3(0.5f, 0.08f, 0.5f) * h); break;
                case "축제":
                    for (int i = 0; i < 3; i++)
                        Part(root, PrimitiveType.Sphere, new Color[] { new Color(0.95f, 0.35f, 0.35f), new Color(0.98f, 0.8f, 0.3f), new Color(0.4f, 0.7f, 0.95f) }[i],
                            new Vector3((i - 1) * 0.3f * h, (0.6f + 0.1f * (i % 2)) * h, 0), new Vector3(0.28f, 0.34f, 0.28f) * h);
                    break;
                case "일상":
                    Part(root, PrimitiveType.Cylinder, new Color(0.92f, 0.9f, 0.86f), new Vector3(0, 0.2f * h, 0), new Vector3(0.28f, 0.2f, 0.28f) * h);
                    Part(root, PrimitiveType.Cylinder, new Color(0.92f, 0.9f, 0.86f), new Vector3(0.19f * h, 0.2f * h, 0), new Vector3(0.12f, 0.03f, 0.12f) * h, new Vector3(0, 0, 90)); break;
                case "우주":
                    Part(root, PrimitiveType.Sphere, new Color(0.45f, 0.5f, 0.9f), new Vector3(0, 0.5f * h, 0), new Vector3(0.6f, 0.6f, 0.6f) * h);
                    Part(root, PrimitiveType.Cylinder, new Color(0.95f, 0.8f, 0.5f), new Vector3(0, 0.5f * h, 0), new Vector3(1.0f, 0.01f, 1.0f) * h, new Vector3(20, 0, 15)); break;
                case "음식":
                    Part(root, PrimitiveType.Cylinder, new Color(0.9f, 0.7f, 0.45f), new Vector3(0, 0.12f * h, 0), new Vector3(0.5f, 0.12f, 0.5f) * h);
                    Part(root, PrimitiveType.Cylinder, new Color(0.98f, 0.9f, 0.9f), new Vector3(0, 0.33f * h, 0), new Vector3(0.42f, 0.1f, 0.42f) * h);
                    Part(root, PrimitiveType.Sphere, new Color(0.9f, 0.2f, 0.25f), new Vector3(0, 0.5f * h, 0), new Vector3(0.14f, 0.14f, 0.14f) * h); break;
                case "추억":
                    Part(root, PrimitiveType.Cube, new Color(0.6f, 0.45f, 0.3f), new Vector3(0, 0.15f * h, 0), new Vector3(0.6f, 0.3f, 0.4f) * h);
                    Part(root, PrimitiveType.Cube, new Color(0.7f, 0.55f, 0.38f), new Vector3(0.05f * h, 0.38f * h, 0), new Vector3(0.45f, 0.16f, 0.3f) * h, new Vector3(0, 12, 0)); break;
                default:
                    Part(root, PrimitiveType.Cube, stone, new Vector3(0, 0.25f * h, 0), new Vector3(0.4f, 0.5f, 0.4f) * h); break;
            }
            return root.gameObject;
        }
    }
}

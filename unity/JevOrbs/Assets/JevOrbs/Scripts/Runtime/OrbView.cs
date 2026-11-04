using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

namespace JevOrbs
{
    /// <summary>
    /// A bead in 3D. Built from a Card:
    ///   color    = Jev's color (pulled into the low-poly palette)      size = mana
    ///   material = blank grade (worn stone / glass / crystal / gold leaf)   pattern = element family
    ///   surface  = only the engraved name (the rest is in the hover tooltip)
    /// </summary>
    public class OrbView : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerClickHandler, IPointerMoveHandler
    {
        public Card card;
        public float diameter;
        public bool small;
        public bool idle = true;
        public bool forging;                                    // a blank that flashes while Jev reads the name

        public static event Action<OrbView, Vector2> Hover;     // pointer is on a bead (screen position)
        public static event Action<OrbView> HoverEnd;
        public static event Action<OrbView, Vector2> Clicked;   // (bead, screen position)

        Transform body;
        readonly List<Material> mats = new List<Material>();
        readonly List<Mesh> meshes = new List<Mesh>();
        readonly List<Transform> shards = new List<Transform>();
        Vector3 basePos; float phase; bool hovered; float reveal = 1f;

        /// <summary>The bead grows with its mana (a cracked one is the biggest: too heavy for its blank). World units.</summary>
        public static float DiameterFor(Card c, bool small)
        {
            float m = Mathf.Clamp(c.mana, 0, 12);
            return (0.74f + m * 0.041f) * (small ? 0.82f : 1.7f);
        }

        public static OrbView Create(Card c, Transform parent, Vector3 pos, bool small)
        {
            var go = new GameObject("Orb_" + c.name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos;
            var v = go.AddComponent<OrbView>();
            v.Build(c, small);
            return v;
        }

        /// <summary>A blank (not yet engraved) bead of this grade.</summary>
        public static OrbView CreateBlank(int tier, Transform parent, Vector3 pos, bool forging)
        {
            var c = new Card { name = "blank", lang = "en", status = "ok", tier = tier, element = "", kind = "", color = "#" + ColorUtility.ToHtmlStringRGB(LowPolyStyle.TierTint[tier]), mana = 4, element_family = -1 };
            var go = new GameObject("Blank_" + tier);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos;
            var v = go.AddComponent<OrbView>();
            v.Build(c, false, true);
            v.forging = forging;
            return v;
        }

        void Build(Card c, bool isSmall, bool blank = false)
        {
            card = c; small = isSmall;
            int tier = c.tier < 0 ? 2 : Mathf.Clamp(c.tier, 0, 3);
            diameter = blank ? 1.9f : DiameterFor(c, small);
            bool scrib = c.Scribble, broken = c.Shattered;

            Color jev; LowPolyStyle.TryHex(scrib ? "#777777" : c.color, out jev);
            bool lightBead = LowPolyStyle.Luminance(jev) > 0.2f;       // decides ink vs. glowing letters, from Jev's own color (before the palette pull)
            Color col = scrib ? new Color(0.5f, 0.5f, 0.5f) : blank ? LowPolyStyle.TierTint[tier] : LowPolyStyle.Harmonize(jev);
            int fam = scrib || blank ? -1 : (c.element_family >= 0 ? c.element_family : FamilyFallback(c.element));

            // blank grade -> material. jitter: wobble of the vertices (worn stone is lumpy, a gem is clean)
            float smooth, metal, jitter; Color? emit = null;
            switch (tier)
            {
                // Mix(web look, pack look): the packs are matte with soft highlights, so the pack values are far less glossy than the web's glass / metal
                case 0: smooth = 0.05f; metal = 0f; jitter = 0.06f; col = Color.Lerp(col, new Color(0.55f, 0.52f, 0.47f), 0.25f * LowPolyStyle.Blend); break;      // worn stone, ink-smudged
                case 1: smooth = LowPolyStyle.Mix(0.75f, 0.32f); metal = 0f; jitter = 0.03f; break;                                                        // glass -> glazed clay
                case 2: smooth = LowPolyStyle.Mix(0.95f, 0.50f); metal = 0f; jitter = 0.03f; emit = col * LowPolyStyle.Mix(0.18f, 0.12f); break;            // crystal -> satin, faint inner glow
                default: smooth = LowPolyStyle.Mix(0.7f, 0.45f); metal = LowPolyStyle.Mix(0.85f, 0.25f); jitter = 0.03f; emit = new Color(0.45f, 0.34f, 0.08f) * 0.4f; break;   // gold leaf -> satin gold
            }
            if (scrib) { smooth = 0.05f; metal = 0f; jitter = 0.05f; emit = null; }
            // dark beads would sink into the bright scenes: like the packs' pumpkins and lanterns they glow from inside instead of just being dark
            if (!scrib && !blank && !lightBead && !emit.HasValue) emit = col * LowPolyStyle.Mix(0.0f, 0.45f);
            if (broken) col = Color.Lerp(col, new Color(0.15f, 0.12f, 0.14f), 0.45f);

            body = new GameObject("body").transform;
            body.SetParent(transform, false);
            body.localScale = Vector3.one * diameter;
            var mesh = OrbMeshFactory.Build(c.name + "|" + tier, 1, jitter, broken);
            meshes.Add(mesh);
            body.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = body.gameObject.AddComponent<MeshRenderer>();
            var mat = LowPolyStyle.NewMaterial(col, smooth, metal, fam >= 0 ? LowPolyStyle.Pattern(fam) : null, emit);
            mats.Add(mat); mr.sharedMaterial = mat;

            var sc = gameObject.AddComponent<SphereCollider>();
            sc.radius = diameter * 0.5f;

            // gold leaf: a thin gold band around the bead
            if (tier == 3 && !scrib)
            {
                var band = MakePart("goldband", OrbMeshFactory.Torus(0.5f * 1.03f, 0.012f, 24, 4), LowPolyStyle.NewMaterial(new Color(0.96f, 0.80f, 0.32f), 0.8f, 1f, null, new Color(0.5f, 0.38f, 0.08f)));
                band.localScale = Vector3.one * diameter; band.localRotation = Quaternion.Euler(78f, 0f, 20f);
            }
            // a cracked bead shows a dark glowing core through the gap
            if (broken)
            {
                var core = MakePart("core", OrbMeshFactory.Build("core", 0, 0.12f, false), LowPolyStyle.NewMaterial(new Color(0.12f, 0.05f, 0.08f), 0.1f, 0f, null, new Color(0.9f, 0.18f, 0.25f) * 0.7f));
                core.localScale = Vector3.one * diameter * 0.55f;
            }
            // little shards circle the big stage bead, tinted by element family
            if (!small && !blank && !scrib && fam >= 0)
            {
                var shardMesh = OrbMeshFactory.Shard(); meshes.Add(shardMesh);
                for (int i = 0; i < 3; i++)
                {
                    var sm = LowPolyStyle.NewMaterial(LowPolyStyle.FamilyAccent[fam], 0.6f, 0f, null, LowPolyStyle.FamilyAccent[fam] * 0.6f);
                    var t = MakePart("shard" + i, shardMesh, sm, false);
                    t.localScale = Vector3.one * diameter * 0.11f;
                    shards.Add(t);
                }
            }
            if (!blank) Engraving.Build(transform, c, diameter, small, lightBead && !broken, jitter);
            if (scrib) AddStrikethrough();

            basePos = transform.localPosition; phase = UnityEngine.Random.value * 6.28f;
        }

        static int FamilyFallback(string element)
        {
            int f;
            return element != null && Rules.Data.element_family_of.TryGetValue(element, out f) ? f : -1;
        }

        Transform MakePart(string partName, Mesh m, Material mat, bool ownMesh = true)
        {
            var go = new GameObject(partName);
            go.transform.SetParent(transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = m;
            go.AddComponent<MeshRenderer>().sharedMaterial = mat;
            mats.Add(mat); if (ownMesh) meshes.Add(m);
            return go.transform;
        }

        void AddStrikethrough()
        {
            // a wavy cancel line across the scribbled name
            var mesh = new Mesh { name = "JevStrike" };
            var verts = new List<Vector3>(); var idx = new List<int>();
            const int N = 12; float w = diameter * 0.7f, h = diameter * 0.018f;
            for (int i = 0; i <= N; i++)
            {
                float x = Mathf.Lerp(-w * 0.5f, w * 0.5f, i / (float)N), y = Mathf.Sin(i * 1.3f) * diameter * 0.02f;
                float z = -Mathf.Sqrt(Mathf.Max(0.0001f, diameter * diameter * 0.25f - x * x)) * 1.04f;
                verts.Add(new Vector3(x, y - h, z)); verts.Add(new Vector3(x, y + h, z));
            }
            for (int i = 0; i < N; i++) { int a = i * 2; idx.AddRange(new[] { a, a + 3, a + 1, a, a + 2, a + 3 }); }
            mesh.SetVertices(verts); mesh.SetTriangles(idx, 0); mesh.RecalculateNormals();
            var mat = LowPolyStyle.NewMaterial(new Color(0.2f, 0.1f, 0.12f), 0.1f, 0f);
            MakePart("strike", mesh, mat);
        }

        /// <summary>A yellow ring marks a bead that is in the deck.</summary>
        public void MarkInDeck()
        {
            var ring = MakePart("deckring", OrbMeshFactory.Torus(0.5f, 0.02f, 28, 4), LowPolyStyle.NewMaterial(new Color(1f, 0.85f, 0.25f), 0.3f, 0f, null, new Color(0.9f, 0.7f, 0.1f) * 0.8f));
            ring.localScale = Vector3.one * diameter * 1.12f; ring.localRotation = Quaternion.Euler(80f, 0f, 0f);
        }

        /// <summary>A newly forged bead pops out of the blank.</summary>
        public void PlayReveal() { reveal = 0f; }

        void Update()
        {
            float t = Time.time + phase;
            if (reveal < 1f) reveal = Mathf.MoveTowards(reveal, 1f, Time.deltaTime * 2.2f);
            float pop = reveal < 1f ? Mathf.Sin(reveal * Mathf.PI * 0.5f) * (1f + (1f - reveal) * 0.25f) : 1f;
            float target = (hovered ? 1.07f : 1f) * pop * (forging ? 1f + Mathf.Sin(Time.time * 14f) * 0.03f : 1f);
            transform.localScale = Vector3.Lerp(transform.localScale, Vector3.one * target, 1f - Mathf.Exp(-14f * Time.deltaTime));
            if (idle)
            {
                float lift = hovered ? 0.12f : 0f;
                transform.localPosition = Vector3.Lerp(transform.localPosition, basePos + new Vector3(0, Mathf.Sin(t * 1.3f) * diameter * 0.015f + lift, 0), 1f - Mathf.Exp(-10f * Time.deltaTime));
                transform.localRotation = Quaternion.Euler(Mathf.Sin(t * 0.7f) * 3f, Mathf.Sin(t * 0.5f) * 12f, 0f);   // a gentle sway keeps the letters readable
            }
            for (int i = 0; i < shards.Count; i++)
            {
                float a = t * (0.8f + i * 0.15f) + i * 2.1f, rad = diameter * (0.62f + i * 0.05f);
                shards[i].localPosition = new Vector3(Mathf.Cos(a) * rad, Mathf.Sin(a * 0.7f + i) * rad * 0.45f, Mathf.Sin(a) * rad * 0.6f);
                shards[i].Rotate(new Vector3(30f, 50f, 20f) * Time.deltaTime);
            }
        }

        public void OnPointerEnter(PointerEventData e) { hovered = true; if (Hover != null) Hover(this, e.position); }
        public void OnPointerMove(PointerEventData e) { if (hovered && Hover != null) Hover(this, e.position); }
        public void OnPointerExit(PointerEventData e) { hovered = false; if (HoverEnd != null) HoverEnd(this); }
        public void OnPointerClick(PointerEventData e) { if (Clicked != null) Clicked(this, e.position); }

        void OnDestroy()
        {
            foreach (var m in mats) if (m != null) Destroy(m);
            foreach (var m in meshes) if (m != null) Destroy(m);
            if (hovered && HoverEnd != null) HoverEnd(this);
        }
    }
}

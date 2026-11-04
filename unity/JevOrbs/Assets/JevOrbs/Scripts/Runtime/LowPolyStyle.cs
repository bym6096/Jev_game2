using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace JevOrbs
{
    /// <summary>
    /// One place for "look like the low-poly packs" (RG Poly / EmaceArt Creator Bundle): flat-shaded faceted meshes, saturated mid-value colors,
    /// a warm key light with cool fill, a little bloom, no fine textures. The web toy's colors came from Jev as-is (0.20-0.70 lightness);
    /// here they are pulled into the band those packs use so a dark "night" bead and a bright "sun" bead both sit in the same scene.
    /// </summary>
    public static class LowPolyStyle
    {
        // --- palette -------------------------------------------------------------------
        public const float MinSat = 0.34f, MaxSat = 0.90f, MinVal = 0.40f, MaxVal = 0.96f;

        public static bool TryHex(string hex, out Color c)
        {
            c = new Color(0.54f, 0.6f, 0.66f);
            return !string.IsNullOrEmpty(hex) && ColorUtility.TryParseHtmlString(hex, out c);
        }

        /// <summary>Jev's color -> a color that belongs in the low-poly palette (hue kept, saturation and value pulled into the pack's range).</summary>
        public static Color Harmonize(Color jev)
        {
            float h, s, v; Color.RGBToHSV(jev, out h, out s, out v);
            s = Mathf.Lerp(MinSat, MaxSat, Mathf.Clamp01(s));
            v = Mathf.Lerp(MinVal, MaxVal, Mathf.Clamp01((v - 0.2f) / 0.75f));
            return Color.HSVToRGB(h, s, v);
        }

        public static float Luminance(Color c) { return 0.2126f * c.linear.r + 0.7152f * c.linear.g + 0.0722f * c.linear.b; }

        // blank grade -> color of an unengraved bead (TIER_TINT in the web toy)
        public static readonly Color[] TierTint =
        {
            new Color32(0x8b, 0x85, 0x78, 255), new Color32(0x8e, 0xa6, 0xbd, 255), new Color32(0xa9, 0xd6, 0xea, 255), new Color32(0xe0, 0xbd, 0x55, 255)
        };

        // element family -> accent color of the little shards that circle the stage bead
        public static readonly Color[] FamilyAccent =
        {
            new Color32(0xff, 0x9a, 0x4d, 255), // 0 natural force
            new Color32(0xb8, 0xc4, 0xd0, 255), // 1 material
            new Color32(0x7d, 0xd6, 0x6b, 255), // 2 living thing
            new Color32(0xb3, 0x8c, 0xff, 255), // 3 abstract concept
            new Color32(0xff, 0xd9, 0x66, 255), // 4 everyday life
            new Color32(0xff, 0x8f, 0xb8, 255), // 5 people and relationships
            new Color32(0x6e, 0xc9, 0xff, 255), // 6 culture
        };

        // --- materials -----------------------------------------------------------------
        static Material _template;

        static bool UsingSrp { get { return GraphicsSettings.currentRenderPipeline != null; } }

        /// <summary>A lit material that matches the active render pipeline (URP/Lit or Standard). Shaders are looked up through a material
        /// asset in Resources (JevOrbLit, made by the Jev/Setup menu) so a build keeps them; Shader.Find is the editor fallback.</summary>
        public static Material Template()
        {
            if (_template != null) return _template;
            var res = Resources.Load<Material>("JevOrbLit");
            if (res != null && res.shader != null && res.shader.name.StartsWith("Universal") == UsingSrp) return _template = res;
            Shader sh = UsingSrp ? Shader.Find("Universal Render Pipeline/Lit") : Shader.Find("Standard");
            if (sh == null) sh = Shader.Find("Standard");
            if (sh == null) sh = Shader.Find("Sprites/Default");
            return _template = new Material(sh);
        }

        public static Material NewMaterial(Color color, float smoothness, float metallic, Texture tex = null, Color? emission = null)
        {
            var m = new Material(Template());
            SetColor(m, color);
            if (m.HasProperty("_Smoothness")) m.SetFloat("_Smoothness", smoothness);
            if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", smoothness);
            if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", metallic);
            if (tex != null)
            {
                if (m.HasProperty("_BaseMap")) m.SetTexture("_BaseMap", tex);
                if (m.HasProperty("_MainTex")) m.SetTexture("_MainTex", tex);
            }
            if (emission.HasValue)
            {
                m.EnableKeyword("_EMISSION");
                if (m.HasProperty("_EmissionColor")) m.SetColor("_EmissionColor", emission.Value);
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            return m;
        }

        public static void SetColor(Material m, Color c)
        {
            if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", c);
            if (m.HasProperty("_Color")) m.SetColor("_Color", c);
        }

        // --- inner patterns (one per element family), baked once into small tileable textures ----------------
        static readonly Dictionary<int, Texture2D> Patterns = new Dictionary<int, Texture2D>();

        /// <summary>Soft gray-scale pattern multiplied into the bead's color: 0 streaks, 1 facets, 2 veins, 3 rings, 4 dots, 5 waves, 6 lattice.</summary>
        public static Texture2D Pattern(int family)
        {
            family = Mathf.Clamp(family, 0, 6);
            Texture2D t;
            if (Patterns.TryGetValue(family, out t) && t != null) return t;
            const int W = 128, H = 64;
            var tex = new Texture2D(W, H, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Bilinear, name = "JevPattern" + family };
            var px = new Color32[W * H];
            for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                {
                    float u = x / (float)W, v = y / (float)H, g;
                    switch (family)
                    {
                        case 0: g = Mathf.PerlinNoise(u * 4f + 3f, v * 14f); break;                                              // streaks of weather
                        case 1: g = Mathf.Abs(Mathf.Sin(u * Mathf.PI * 8f)) * 0.5f + Mathf.Abs(Mathf.Sin(v * Mathf.PI * 4f + u * 3f)) * 0.5f; break; // facets
                        case 2: g = 1f - Mathf.Abs(Mathf.PerlinNoise(u * 6f, v * 6f) - 0.5f) * 3f; break;                        // veins
                        case 3: g = 0.5f + 0.5f * Mathf.Sin(Mathf.Sqrt((u - 0.5f) * (u - 0.5f) * 4f + (v - 0.5f) * (v - 0.5f)) * 40f); break; // rings
                        case 4: g = Mathf.Sin(u * Mathf.PI * 16f) * Mathf.Sin(v * Mathf.PI * 8f) > 0.55f ? 1f : 0.4f; break;     // dots
                        case 5: g = 0.5f + 0.5f * Mathf.Sin(v * Mathf.PI * 10f + Mathf.Sin(u * Mathf.PI * 6f) * 1.5f); break;    // waves
                        default: g = Mathf.Abs(Mathf.Sin((u * 8f + v * 4f) * Mathf.PI)) * Mathf.Abs(Mathf.Sin((u * 8f - v * 4f) * Mathf.PI)); break; // lattice
                    }
                    byte b = (byte)Mathf.RoundToInt(Mathf.Lerp(0.68f, 1f, Mathf.Clamp01(g)) * 255f);
                    px[y * W + x] = new Color32(b, b, b, 255);
                }
            tex.SetPixels32(px); tex.Apply(false);
            Patterns[family] = tex;
            return tex;
        }

        // --- lighting / camera rig ---------------------------------------------------------
        /// <summary>Warm sun + cool sky fill, soft shadows, light haze: the lighting the packs are usually shown in.</summary>
        public static Light BuildLighting(Transform parent)
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.62f, 0.72f, 0.88f);
            RenderSettings.ambientEquatorColor = new Color(0.52f, 0.52f, 0.58f);
            RenderSettings.ambientGroundColor = new Color(0.30f, 0.27f, 0.30f);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.62f, 0.72f, 0.82f); RenderSettings.fogStartDistance = 22f; RenderSettings.fogEndDistance = 55f;

            var go = new GameObject("JevKeyLight");
            go.transform.SetParent(parent, false);
            go.transform.rotation = Quaternion.Euler(42f, -32f, 0f);
            var l = go.AddComponent<Light>();
            l.type = LightType.Directional; l.color = new Color(1f, 0.93f, 0.8f); l.intensity = 1.15f;
            l.shadows = LightShadows.Soft; l.shadowStrength = 0.7f;
            return l;
        }

        /// <summary>Filled in by the JevOrbs.URP assembly (Scripts/URP) when the Universal RP package is installed: bloom, tonemapping, saturation.
        /// Kept out of this assembly so the runtime code compiles in a project with or without URP.</summary>
        public static Action<Camera, Transform> PostFx;

        /// <summary>Camera look: sky-colored background and MSAA, plus the URP post effects when available.</summary>
        public static void StyleCamera(Camera cam, Transform parent)
        {
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.62f, 0.72f, 0.82f);
            cam.allowMSAA = true;
            if (PostFx != null) PostFx(cam, parent);   // set by JevOrbs.URP when the Universal RP package is present
        }
    }
}

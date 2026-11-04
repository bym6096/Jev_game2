using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace JevOrbs
{
    /// <summary>
    /// Only compiled when the Universal RP package is installed (see JevOrbs.URP.asmdef).
    /// Gives the camera the soft, saturated look the low-poly packs are shown in: a little bloom, ACES tonemapping, a touch of saturation, a light vignette.
    /// </summary>
    static class JevUrpPostFx
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Register() { LowPolyStyle.PostFx = Apply; }

        static void Apply(Camera cam, Transform parent)
        {
            if (GraphicsSettings.currentRenderPipeline == null) return;   // the project is not rendering with URP (yet)

            var data = cam.GetComponent<UniversalAdditionalCameraData>();
            if (data == null) data = cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;

            var go = new GameObject("JevPostFX");
            go.transform.SetParent(parent, false);
            var vol = go.AddComponent<Volume>();
            vol.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            var bloom = profile.Add<Bloom>(true);
            bloom.threshold.Override(1.0f); bloom.intensity.Override(0.35f); bloom.scatter.Override(0.55f);   // only the glowing beads / emissive bits bloom
            var tone = profile.Add<Tonemapping>(true);
            tone.mode.Override(TonemappingMode.ACES);
            var adj = profile.Add<ColorAdjustments>(true);
            adj.saturation.Override(14f); adj.contrast.Override(4f);
            var vig = profile.Add<Vignette>(true);
            vig.intensity.Override(0.15f);
            vol.sharedProfile = profile;
        }
    }
}

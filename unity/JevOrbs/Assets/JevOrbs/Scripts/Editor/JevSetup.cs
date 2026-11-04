using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace JevOrbs.EditorTools
{
    /// <summary>
    /// One-click setup: menu Jev > Setup.
    ///   1. Resources/JevOrbLit.mat   a Lit material that matches the project's render pipeline (so a build keeps the shader)
    ///   2. Resources/JevThemeDecor   the empty slots where you drop prefabs from the low-poly packs (one per theme)
    ///   3. Scenes/JevOrbs.unity      a scene with the game in it, added to the Build Settings
    /// Runs by itself once when the project is first opened (never in batch mode); re-running only fills in what is missing.
    /// </summary>
    public static class JevSetup
    {
        const string Root = "Assets/JevOrbs";
        const string ScenePath = Root + "/Scenes/JevOrbs.unity";
        const string MatPath = Root + "/Resources/JevOrbLit.mat";
        const string DecorPath = Root + "/Resources/JevThemeDecor.asset";

        [InitializeOnLoadMethod]
        static void AutoSetup()
        {
            if (Application.isBatchMode) return;
            EditorApplication.delayCall += () =>
            {
                if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling || EditorApplication.isUpdating) return;
                if (File.Exists(ScenePath) && File.Exists(MatPath) && File.Exists(DecorPath)) return;
                try { Run(false); } catch (Exception e) { Debug.LogWarning("[Jev] 자동 설정에 실패했습니다. 메뉴 Jev > Setup 으로 다시 해 보세요: " + e.Message); }
            };
        }

        [MenuItem("Jev/Setup (재질·테마 소품·장면 만들기)")]
        static void MenuRun() { Run(true); }

        [MenuItem("Jev/장면 열기")]
        static void OpenScene()
        {
            if (!File.Exists(ScenePath)) Run(false);
            if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) EditorSceneManager.OpenScene(ScenePath);
        }

        static bool UsingUrp { get { return GraphicsSettings.currentRenderPipeline != null; } }

        static void Run(bool interactive)
        {
            Directory.CreateDirectory(Root + "/Resources"); Directory.CreateDirectory(Root + "/Scenes");
            MakeMaterial();
            MakeDecorSet();
            MakeScene();
            AssetDatabase.SaveAssets(); AssetDatabase.Refresh();

            string note = UsingUrp
                ? "URP로 렌더링 중입니다. 설정이 끝났습니다."
                : "지금은 URP가 켜져 있지 않아 기본(Built-in) 셰이더로 보입니다. 로우폴리 팩들은 대부분 URP용이므로 아래를 한 번 해 주세요.\n\n" +
                  "1) Project 창에서 우클릭 > Create > Rendering > URP Asset (with Universal Renderer)\n" +
                  "2) Edit > Project Settings > Graphics > Default Render Pipeline 에 그 에셋을 끌어 넣기\n" +
                  "3) Quality 설정의 Render Pipeline Asset 에도 같은 에셋 지정\n" +
                  "4) 메뉴 Jev > Setup 을 한 번 더 실행 (재질을 URP용으로 다시 만듭니다)";
            Debug.Log("[Jev] 설정 완료: " + ScenePath + "\n" + note);
            if (interactive) EditorUtility.DisplayDialog("Jev 설정", "장면 " + ScenePath + " 을(를) 만들었습니다.\n\n" + note, "확인");
        }

        static void MakeMaterial()
        {
            var shader = Shader.Find(UsingUrp ? "Universal Render Pipeline/Lit" : "Standard") ?? Shader.Find("Standard");
            var existing = AssetDatabase.LoadAssetAtPath<Material>(MatPath);
            if (existing != null)
            {
                if (existing.shader != null && shader != null && existing.shader.name == shader.name) return;
                existing.shader = shader; EditorUtility.SetDirty(existing); return;     // pipeline changed: switch the shader, keep the asset (and its GUID)
            }
            AssetDatabase.CreateAsset(new Material(shader), MatPath);
        }

        static void MakeDecorSet()
        {
            if (AssetDatabase.LoadAssetAtPath<ThemeDecorSet>(DecorPath) != null) return;
            var set = ScriptableObject.CreateInstance<ThemeDecorSet>();
            foreach (var theme in Rules.Data.themes) set.entries.Add(new ThemeDecorSet.Entry { theme = theme });
            AssetDatabase.CreateAsset(set, DecorPath);
        }

        static void MakeScene()
        {
            if (!File.Exists(ScenePath))
            {
                var sc = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Additive);   // additive: whatever the user has open stays untouched
                new GameObject("JevGame").AddComponent<JevGame>();
                EditorSceneManager.SaveScene(sc, ScenePath);
                EditorSceneManager.CloseScene(sc, true);
            }
            var scenes = EditorBuildSettings.scenes;
            foreach (var s in scenes) if (s.path == ScenePath) return;
            var list = new System.Collections.Generic.List<EditorBuildSettingsScene>(scenes) { new EditorBuildSettingsScene(ScenePath, true) };
            EditorBuildSettings.scenes = list.ToArray();
        }
    }
}

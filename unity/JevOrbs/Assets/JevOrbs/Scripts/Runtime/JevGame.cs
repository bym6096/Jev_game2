using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace JevOrbs
{
    /// <summary>
    /// The whole toy as one component (port of toys/card-forge/template.html): pick a profile language once, choose a blank, write a name,
    /// Jev reads it and a bead appears; the beads sit on a shelf, go into a deck, and the deck becomes the hero.
    /// Everything (camera, light, diorama, UI) is built in Awake, so any empty scene works: add this component to an empty GameObject and press Play
    /// (or open Assets/JevOrbs/Scenes/JevOrbs.unity, which Jev > Setup creates).
    /// </summary>
    public class JevGame : MonoBehaviour
    {
        [Header("Server (toys/card-forge/server.py or the Vercel deploy). The Jev key lives there, never in the game.")]
        public string serverUrl = "http://localhost:8000";

        // --- world layout (see LowPolyStyle / README for how this is meant to be dressed with the low-poly packs) ---
        static readonly Vector3 StagePos = new Vector3(-2.2f, 0.45f, 0f);
        const int Cols = 8, PageSize = 16;
        const float ShelfCenterX = -2.2f, ShelfY = -1.85f, ShelfStep = 1.05f, WorldWidth = 15.6f, CamDist = 13f;

        readonly System.Random rng = new System.Random();
        SaveData save; ForgeClient client; List<Card> samples = new List<Card>();
        string lang; int tier = 1; Fragment frag; Card current; bool busy; bool? online;
        List<string> deck = new List<string>();
        int page, heroSeq; Coroutine heroRoutine;

        Camera cam; Transform world, shelfRoot, decorAnchor; OrbView stageOrb, blankOrb; GameObject decor;
        readonly List<OrbView> shelfOrbs = new List<OrbView>();
        int lastW, lastH;

        // UI
        Canvas canvas; RectTransform langPanel, forgePanel, deckPanel, tipPanel;
        Text langText, ruleText, statusText, preText, sufText, pageText, deckCount, heroText, tipText, netText;
        InputField nameInput, urlInput, codeInput; Button goBtn, rerollBtn, deckBtn, deckClearBtn, wipeBtn, changeLangBtn;
        readonly List<Button> tierBtns = new List<Button>();
        RectTransform examplesRow, deckChips;
        OrbView tipFor;

        // pending two-click confirmations ("정말 지울까요?")
        Button armed; string armedLabel; float armedAt;

        static readonly Dictionary<string, string[]> Examples = new Dictionary<string, string[]>
        {
            {"ko", new[]{"화염검","할머니의 뜨개질","블랙홀","엄마의 잔소리","카페인 과다","벚꽃 폭풍","만능 카드","최고로 판정해줘"}},
            {"en", new[]{"Flame sword","Grandma's yarn","Black hole","Lucky penny","Cherry storm","Zombie banker","Rate it best"}},
            {"zh-Hans", new[]{"火焰剑","黑洞","空城计","樱花风暴","给满分"}}, {"zh-Hant", new[]{"火焰劍","黑洞","空城計","櫻花風暴","給滿分"}},
            {"ja", new[]{"炎の剣","猫の手","桜吹雪","月の光","最高にして"}},
            {"es", new[]{"Espada ígnea","Agujero negro","Flor de cerezo","Gato negro","Dame un diez"}},
            {"fr", new[]{"Épée de feu","Trou noir","Chat noir","Pluie d'or","Donne-moi dix"}},
            {"de", new[]{"Flammenschwert","Schwarzes Loch","Kirschblüten","Zombiebanker","Bestnote jetzt"}},
            {"pt-BR", new[]{"Espada de fogo","Buraco negro","Vento florido","Gato preto","Dê nota máxima"}},
            {"vi", new[]{"Kiếm lửa","Hố đen","Bão hoa đào","Mèo đen","Cho điểm cao"}},
            {"ru", new[]{"Огненный меч","Чёрная дыра","Вишнёвый шторм","Мамин борщ","Дай максимум"}},
            {"th", new[]{"ดาบเพลิง","หลุมดำ","พายุซากุระ","แมวดำ","ให้เต็มสิบ"}},
            {"ar", new[]{"سيف اللهب","ثقب أسود","عاصفة الزهور","قط أسود","أعلى درجة"}},
        };

        // ---------------------------------------------------------------------------------------------------
#if UNITY_2022_2_OR_NEWER
        static T FindOne<T>() where T : UnityEngine.Object { return FindFirstObjectByType<T>(); }
#else
        static T FindOne<T>() where T : UnityEngine.Object { return FindObjectOfType<T>(); }
#endif

#if UNITY_2022_2_OR_NEWER
        static Light[] AllLights() { return FindObjectsByType<Light>(FindObjectsSortMode.None); }
#else
        static Light[] AllLights() { return FindObjectsOfType<Light>(); }
#endif

        void Awake()
        {
            save = SaveStore.Load();
            if (!string.IsNullOrEmpty(save.serverUrl) && save.serverUrl != "http://localhost:8000") serverUrl = save.serverUrl;
            client = new ForgeClient { baseUrl = serverUrl, accessCode = save.accessCode };
            lang = save.lang; deck = new List<string>(save.deck);
            LoadSamples();
            BuildWorld();
            BuildUI();
        }

        void Start()
        {
            ApplyProfile();
            DrawBlank();
            RenderDeck();
            Show(CardRules.OnBlank(samples.Count > 0 ? samples[0] : EmptyCard(), 2, null));
            RefreshShelf();
            if (lang != null && deck.Count > 0) heroRoutine = StartCoroutine(JudgeHero());
        }

        void OnEnable() { OrbView.Hover += OnOrbHover; OrbView.HoverEnd += OnOrbHoverEnd; OrbView.Clicked += OnOrbClicked; }
        void OnDisable() { OrbView.Hover -= OnOrbHover; OrbView.HoverEnd -= OnOrbHoverEnd; OrbView.Clicked -= OnOrbClicked; }

        static Card EmptyCard() { return new Card { name = "?", lang = "en", element = "", kind = "스킬", mana = 0, mana_power = 0, mana_stats = 0, effects = new List<CardEffect>() }; }

        void LoadSamples()
        {
            try
            {
                var ta = Resources.Load<TextAsset>("JevSamples");
                var raw = ta != null ? JsonConvert.DeserializeObject<List<Card>>(ta.text) : new List<Card>();
                samples = raw.Select(CardRules.Clean).Where(c => c != null).Select(c => CardRules.OnBlank(c, 2, null)).ToList();   // samples are shown on a clean blank
            }
            catch (Exception e) { Debug.LogWarning("견본 구슬을 읽지 못했습니다: " + e.Message); }
        }

        // ------------------------------------------------------------------------------------------ world
        void BuildWorld()
        {
            world = new GameObject("JevWorld").transform; world.SetParent(transform, false);

            cam = Camera.main;
            if (cam == null) { var cg = new GameObject("Main Camera") { tag = "MainCamera" }; cam = cg.AddComponent<Camera>(); cg.AddComponent<AudioListener>(); }
            cam.transform.position = new Vector3(0f, 2.4f, -CamDist);
            cam.transform.LookAt(new Vector3(0f, 0.6f, 0f));
            cam.nearClipPlane = 0.3f; cam.farClipPlane = 120f;
            if (cam.GetComponent<UnityEngine.EventSystems.PhysicsRaycaster>() == null) cam.gameObject.AddComponent<UnityEngine.EventSystems.PhysicsRaycaster>();
            LowPolyStyle.StyleCamera(cam, world);
            FitCamera();

            // replace the default scene light with the style's warm key light
            foreach (var l in AllLights()) if (l.type == LightType.Directional) l.enabled = false;
            LowPolyStyle.BuildLighting(world);

            EnsureEventSystem();
            BuildDiorama();
        }

        void FitCamera()
        {
            float aspect = Mathf.Max(0.3f, (float)Screen.width / Mathf.Max(1, Screen.height));
            cam.fieldOfView = 2f * Mathf.Atan(WorldWidth / (2f * aspect) / CamDist) * Mathf.Rad2Deg;   // the scene is always WorldWidth wide
            lastW = Screen.width; lastH = Screen.height;
        }

        static void EnsureEventSystem()
        {
            if (FindOne<EventSystem>() != null) return;
            var go = new GameObject("EventSystem");
            go.AddComponent<EventSystem>();
#if ENABLE_INPUT_SYSTEM && !ENABLE_LEGACY_INPUT_MANAGER
            var t = Type.GetType("UnityEngine.InputSystem.UI.InputSystemUIInputModule, Unity.InputSystem");
            if (t != null) { go.AddComponent(t); return; }
#endif
            go.AddComponent<StandaloneInputModule>();
        }

        Transform AddMesh(string n, Mesh m, Color c, Vector3 pos, Vector3 scale, float smooth = 0.1f)
        {
            var go = new GameObject(n);
            go.transform.SetParent(world, false); go.transform.localPosition = pos; go.transform.localScale = scale;
            go.AddComponent<MeshFilter>().sharedMesh = m;
            go.AddComponent<MeshRenderer>().sharedMaterial = LowPolyStyle.NewMaterial(c, smooth, 0f);
            return go.transform;
        }

        void AddBox(string n, Color c, Vector3 pos, Vector3 scale)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);   // a cube is already flat-shaded
            Destroy(go.GetComponent<Collider>());                      // scenery must not catch the pointer
            go.name = n; go.transform.SetParent(world, false); go.transform.localPosition = pos; go.transform.localScale = scale;
            go.GetComponent<MeshRenderer>().sharedMaterial = LowPolyStyle.NewMaterial(c, 0.1f, 0f);
        }

        /// <summary>A small stand-in for the packs' environment: a flat-shaded tabletop, hills, a pedestal and shelf planks.
        /// Delete JevWorld's "Diorama" children and put pack scenery here when the packs are imported.</summary>
        void BuildDiorama()
        {
            var d = new GameObject("Diorama").transform; d.SetParent(world, false);
            var keep = world; world = d;                                                         // Mesh() parents to `world`
            AddMesh("Ground", OrbMeshFactory.Prism(10), new Color(0.46f, 0.70f, 0.40f), new Vector3(0f, -4.6f, 5f), new Vector3(34f, 1.5f, 20f));
            Color[] hill = { new Color(0.40f, 0.64f, 0.45f), new Color(0.50f, 0.72f, 0.50f), new Color(0.38f, 0.58f, 0.62f) };
            for (int i = 0; i < 6; i++)
            {
                var m = OrbMeshFactory.Build("hill" + i, 1, 0.12f, false);
                AddMesh("Hill" + i, m, hill[i % 3], new Vector3(-13f + i * 5.4f, -2.6f, 9f + (i % 2) * 3f), new Vector3(7f, 4.6f + (i % 3), 5f));
            }
            AddMesh("Pedestal", OrbMeshFactory.Prism(8), new Color(0.80f, 0.76f, 0.68f), StagePos + new Vector3(0, -1.35f, 0.1f), new Vector3(2.8f, 0.5f, 2.8f), 0.2f);
            for (int r = 0; r < PageSize / Cols; r++)
                AddBox("ShelfPlank" + r, new Color(0.58f, 0.40f, 0.24f), new Vector3(ShelfCenterX, ShelfY - r * ShelfStep - 0.52f, 0.5f), new Vector3(Cols * ShelfStep * 1.2f, 0.1f, 1.1f));
            world = keep;

            shelfRoot = new GameObject("Shelf").transform; shelfRoot.SetParent(world, false);
            decorAnchor = new GameObject("DecorAnchor").transform; decorAnchor.SetParent(world, false);
            decorAnchor.position = StagePos + new Vector3(2.6f, -1.1f, 0.2f);
        }

        // -------------------------------------------------------------------------------------------- UI
        void BuildUI()
        {
            var cgo = new GameObject("JevCanvas"); cgo.transform.SetParent(transform, false);
            canvas = cgo.AddComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 10;
            var scaler = cgo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize; scaler.referenceResolution = new Vector2(1280, 720); scaler.matchWidthOrHeight = 0.5f;
            cgo.AddComponent<GraphicRaycaster>();

            // forge bar (top-left)
            forgePanel = UIKit.Panel(canvas.transform, "Forge", UIKit.PanelBg);
            UIKit.Anchor(forgePanel, new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, 1), new Vector2(14, -14), new Vector2(690, 0));
            var v = forgePanel.gameObject.AddComponent<VerticalLayoutGroup>();
            v.spacing = 6; v.padding = new RectOffset(12, 12, 10, 10); v.childControlWidth = true; v.childControlHeight = true; v.childForceExpandWidth = true; v.childForceExpandHeight = false;
            forgePanel.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            var r1 = UIKit.HRow(forgePanel, 8, 30);
            var title = UIKit.Label(r1.transform, "빈 구슬 공방", 20, TextAnchor.MiddleLeft, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(title.gameObject, 150, 30);
            langText = UIKit.Label(r1.transform, "", 15, TextAnchor.MiddleLeft, UIKit.Dim); UIKit.Size(langText.gameObject, -1, 30, 1);
            changeLangBtn = UIKit.Btn(r1.transform, "언어 바꾸기", () => Confirm(changeLangBtn, ChangeLanguage), 13); UIKit.Size(changeLangBtn.gameObject, 100, 30);
            wipeBtn = UIKit.Btn(r1.transform, "저장 지우기", () => Confirm(wipeBtn, WipeAll), 13); UIKit.Size(wipeBtn.gameObject, 100, 30);

            ruleText = UIKit.Label(forgePanel, "", 12, TextAnchor.MiddleLeft, UIKit.Dim); UIKit.Size(ruleText.gameObject, -1, 18);

            var r2 = UIKit.HRow(forgePanel, 6, 46);
            for (int i = 0; i < Rules.Data.tiers.Count; i++)
            {
                int ti = i;
                var b = UIKit.Btn(r2.transform, "", () => { tier = ti; DrawBlank(); }, 12); UIKit.Size(b.gameObject, 160, 46, 1);
                tierBtns.Add(b);
            }

            var r3 = UIKit.HRow(forgePanel, 6, 38);
            preText = UIKit.Label(r3.transform, "", 17, TextAnchor.MiddleRight, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(preText.gameObject, 110, 38);
            nameInput = UIKit.Input(r3.transform, "이름을 적으세요", 20); UIKit.Size(nameInput.gameObject, 220, 38, 1);
            sufText = UIKit.Label(r3.transform, "", 17, TextAnchor.MiddleLeft, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(sufText.gameObject, 110, 38);
            nameInput.onValueChanged.AddListener(_ => UpdateCount());
            goBtn = UIKit.Btn(r3.transform, "새기기", () => OnForge(), 16); UIKit.Size(goBtn.gameObject, 84, 38);
            rerollBtn = UIKit.Btn(r3.transform, "다른 말", () => DrawBlank(), 13); UIKit.Size(rerollBtn.gameObject, 74, 38);

            examplesRow = UIKit.Rect("examples", forgePanel);
            var eh = examplesRow.gameObject.AddComponent<HorizontalLayoutGroup>(); eh.spacing = 4; eh.childControlWidth = true; eh.childControlHeight = true; eh.childForceExpandWidth = false;
            UIKit.Size(examplesRow.gameObject, -1, 26);

            statusText = UIKit.Label(forgePanel, "", 14, TextAnchor.UpperLeft, UIKit.TextCol); UIKit.Size(statusText.gameObject, -1, 40);

            // deck + hero (right)
            deckPanel = UIKit.Panel(canvas.transform, "Deck", UIKit.PanelBg);
            UIKit.Anchor(deckPanel, new Vector2(1, 1), new Vector2(1, 1), new Vector2(1, 1), new Vector2(-14, -14), new Vector2(330, 0));
            var dv = deckPanel.gameObject.AddComponent<VerticalLayoutGroup>();
            dv.spacing = 6; dv.padding = new RectOffset(12, 12, 10, 10); dv.childControlWidth = true; dv.childControlHeight = true; dv.childForceExpandWidth = true; dv.childForceExpandHeight = false;
            deckPanel.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            var d1 = UIKit.HRow(deckPanel, 6, 28);
            var dt = UIKit.Label(d1.transform, "내 덱", 18, TextAnchor.MiddleLeft, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(dt.gameObject, 60, 28);
            deckCount = UIKit.Label(d1.transform, "", 13, TextAnchor.MiddleRight, UIKit.Dim); UIKit.Size(deckCount.gameObject, -1, 28, 1);
            deckChips = UIKit.Rect("chips", deckPanel);
            var grid = deckChips.gameObject.AddComponent<GridLayoutGroup>(); grid.cellSize = new Vector2(144, 26); grid.spacing = new Vector2(4, 4); grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount; grid.constraintCount = 2;
            deckChips.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            var d2 = UIKit.HRow(deckPanel, 6, 32);
            deckBtn = UIKit.Btn(d2.transform, "덱에 넣기", ToggleDeck, 14); UIKit.Size(deckBtn.gameObject, 150, 32, 1);
            deckClearBtn = UIKit.Btn(d2.transform, "덱 비우기", () => { deck.Clear(); DeckChanged(); }, 13); UIKit.Size(deckClearBtn.gameObject, 100, 32);
            var ht = UIKit.Label(deckPanel, "주인공", 18, TextAnchor.MiddleLeft, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(ht.gameObject, -1, 26);
            heroText = UIKit.Label(deckPanel, "", 14, TextAnchor.UpperLeft); UIKit.Size(heroText.gameObject, -1, 150);

            // pager (bottom-left) and server (bottom-right)
            var pager = UIKit.Rect("Pager", canvas.transform);
            UIKit.Anchor(pager, new Vector2(0, 0), new Vector2(0, 0), new Vector2(0, 0), new Vector2(14, 12), new Vector2(560, 30));
            var ph = pager.gameObject.AddComponent<HorizontalLayoutGroup>(); ph.spacing = 6; ph.childControlWidth = true; ph.childControlHeight = true; ph.childForceExpandWidth = false;
            var prev = UIKit.Btn(pager, "◀", () => { page--; RefreshShelf(); }, 14); UIKit.Size(prev.gameObject, 40, 30);
            var next = UIKit.Btn(pager, "▶", () => { page++; RefreshShelf(); }, 14); UIKit.Size(next.gameObject, 40, 30);
            pageText = UIKit.Label(pager, "", 13, TextAnchor.MiddleLeft, UIKit.Dim); UIKit.Size(pageText.gameObject, 440, 30, 1);

            var net = UIKit.Panel(canvas.transform, "Server", new Color(0.09f, 0.11f, 0.16f, 0.7f));
            UIKit.Anchor(net, new Vector2(1, 0), new Vector2(1, 0), new Vector2(1, 0), new Vector2(-14, 12), new Vector2(430, 0));
            var nv = net.gameObject.AddComponent<VerticalLayoutGroup>(); nv.spacing = 4; nv.padding = new RectOffset(8, 8, 6, 6); nv.childControlWidth = true; nv.childControlHeight = true; nv.childForceExpandWidth = true; nv.childForceExpandHeight = false;
            net.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            netText = UIKit.Label(net, "서버: 아직 연결 안 함 (없으면 견본 구슬만)", 12, TextAnchor.MiddleLeft, UIKit.Dim); UIKit.Size(netText.gameObject, -1, 18);
            var nr = UIKit.HRow(net, 4, 26);
            urlInput = UIKit.Input(nr.transform, "http://localhost:8000", 13); UIKit.Size(urlInput.gameObject, 250, 26, 1); urlInput.text = client.baseUrl;
            codeInput = UIKit.Input(nr.transform, "입장 코드", 13); UIKit.Size(codeInput.gameObject, 110, 26); codeInput.text = client.accessCode;
            urlInput.onEndEdit.AddListener(_ => ApplyServerSettings()); codeInput.onEndEdit.AddListener(_ => ApplyServerSettings());

            // tooltip
            tipPanel = UIKit.Panel(canvas.transform, "Tip", new Color(0.07f, 0.08f, 0.12f, 0.95f));
            tipPanel.pivot = new Vector2(0, 1); tipPanel.sizeDelta = new Vector2(320, 0);
            var tv = tipPanel.gameObject.AddComponent<VerticalLayoutGroup>(); tv.padding = new RectOffset(12, 12, 10, 10); tv.childControlWidth = true; tv.childControlHeight = true; tv.childForceExpandWidth = true; tv.childForceExpandHeight = false;
            tipPanel.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            tipPanel.GetComponent<Image>().raycastTarget = false;
            tipText = UIKit.Label(tipPanel, "", 14, TextAnchor.UpperLeft);
            tipPanel.gameObject.SetActive(false);

            // language picker (first run)
            langPanel = UIKit.Panel(canvas.transform, "LangPicker", new Color(0.05f, 0.06f, 0.1f, 0.94f));
            UIKit.Anchor(langPanel, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(760, 0));
            var lv = langPanel.gameObject.AddComponent<VerticalLayoutGroup>(); lv.spacing = 10; lv.padding = new RectOffset(20, 20, 18, 18); lv.childControlWidth = true; lv.childControlHeight = true; lv.childForceExpandWidth = true; lv.childForceExpandHeight = false;
            langPanel.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            var lt = UIKit.Label(langPanel, "이 프로필이 쓸 언어를 고르세요", 22, TextAnchor.MiddleCenter, new Color(0.96f, 0.78f, 0.35f), true); UIKit.Size(lt.gameObject, -1, 34);
            var ln = UIKit.Label(langPanel, "한 번 고르면 이 프로필의 구슬 이름은 그 언어의 글자로만 쓸 수 있습니다. (숫자와 기호는 쓸 수 없습니다)", 13, TextAnchor.MiddleCenter, UIKit.Dim); UIKit.Size(ln.gameObject, -1, 22);
            var gridGo = UIKit.Rect("langs", langPanel);
            var lg = gridGo.gameObject.AddComponent<GridLayoutGroup>(); lg.cellSize = new Vector2(170, 52); lg.spacing = new Vector2(8, 8); lg.constraint = GridLayoutGroup.Constraint.FixedColumnCount; lg.constraintCount = 4;
            gridGo.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            foreach (var key in Rules.Data.language_order)
            {
                string k = key; var cfg = Rules.Data.languages[k];
                UIKit.Btn(gridGo, cfg.label + "\n<size=11>" + cfg.cap + "자까지</size>", () => PickLanguage(k), 15);
            }
        }

        // ------------------------------------------------------------------------------------- profile / blank
        void ApplyProfile()
        {
            bool has = lang != null;
            langPanel.gameObject.SetActive(!has);
            forgePanel.gameObject.SetActive(has); deckPanel.gameObject.SetActive(has);
            if (!has) return;
            var c = Rules.Data.languages[lang];
            langText.text = "언어: <b>" + c.label + "</b>";
            ruleText.text = string.Format("{0} 글자로만 · {1}자까지 (공백 {2}) · 숫자와 기호는 쓸 수 없습니다{3}", c.label, c.cap, c.spaces_count ? "포함" : "제외",
                Rules.Data.fragments.ContainsKey(lang) ? " · 미리 적힌 글자 포함" : "");
            nameInput.text = ""; statusText.text = "";
            ClearChildren(examplesRow);
            string[] ex; if (Examples.TryGetValue(lang, out ex))
                foreach (var e in ex) { string n = e; var b = UIKit.Btn(examplesRow, n, () => { frag = null; RenderBlank(); nameInput.text = n; OnForge(); }, 12); UIKit.Size(b.gameObject, Mathf.Clamp(14f + n.Length * 12f, 48, 130), 26); }
            frag = null; RenderBlank();
        }

        // children are destroyed at the end of the frame, so hide them first or the layout would still count them
        static void ClearChildren(Transform parent)
        {
            for (int i = parent.childCount - 1; i >= 0; i--) { var ch = parent.GetChild(i); ch.gameObject.SetActive(false); Destroy(ch.gameObject); }
        }

        void PickLanguage(string k) { lang = k; save.lang = k; SaveStore.Save(save); ApplyProfile(); DrawBlank(); RenderDeck(); if (deck.Count > 0) { if (heroRoutine != null) StopCoroutine(heroRoutine); heroRoutine = StartCoroutine(JudgeHero()); } }

        void ChangeLanguage()
        {
            lang = null; save.lang = null; deck.Clear(); save.deck = new List<string>(); save.hero = null; save.heroKey = null; heroSeq++;
            SaveStore.Save(save); ApplyProfile(); RenderDeck(); RefreshShelf(); heroText.text = "";
        }

        void WipeAll()
        {
            SaveStore.Wipe();
            save = new SaveData { serverUrl = client.baseUrl, accessCode = client.accessCode };
            lang = null; deck.Clear(); heroSeq++; page = 0;
            ApplyProfile(); RenderDeck(); RefreshShelf(); heroText.text = "";
        }

        // two-click confirmation: the first click arms the button, a second one within 3 s does it
        void Confirm(Button b, Action act)
        {
            if (armed == b && Time.unscaledTime - armedAt < 3f) { UIKit.SetLabel(b, armedLabel); armed = null; act(); return; }
            if (armed != null) UIKit.SetLabel(armed, armedLabel);
            armed = b; armedAt = Time.unscaledTime; armedLabel = b.GetComponentInChildren<Text>().text; UIKit.SetLabel(b, "정말요?");
        }

        void DrawBlank()
        {
            frag = lang != null ? CardRules.DrawFragment(lang, tier, rng) : null;
            RenderBlank();
        }

        void RenderBlank()
        {
            for (int i = 0; i < tierBtns.Count; i++)
            {
                var T = Rules.Data.tiers[i];
                bool hasFrag = lang != null && Rules.Data.fragments.ContainsKey(lang);
                UIKit.SetLabel(tierBtns[i], "<b>" + T.name + "</b>\n<size=11>마나 한계 " + T.cap + " · 값 " + T.price + (hasFrag ? " · 미리 적힌 말 " + Mathf.RoundToInt(T.frag * 100) + "%" : "") + "</size>");
                UIKit.SetSelected(tierBtns[i], i == tier);
            }
            preText.text = frag != null && frag.pos == "pre" ? frag.t : "";
            sufText.text = frag != null && frag.pos == "suf" ? frag.t : "";
            preText.gameObject.SetActive(preText.text.Length > 0); sufText.gameObject.SetActive(sufText.text.Length > 0);
            rerollBtn.gameObject.SetActive(Rules.Data.tiers[tier].frag > 0 && lang != null && Rules.Data.fragments.ContainsKey(lang));
            UpdateCount();
        }

        void UpdateCount()
        {
            if (lang == null || nameInput == null) return;
            if (string.IsNullOrWhiteSpace(nameInput.text)) { if (!busy) statusText.text = ""; return; }
            var r = NameRules.Check(CardRules.Compose(nameInput.text, frag), lang);
            statusText.text = r.err ?? string.Format("{0} {1} / {2}자", Rules.Data.languages[lang].label, r.count, Rules.Data.languages[lang].cap);
        }

        // ---------------------------------------------------------------------------------------- forging
        void OnForge()
        {
            if (busy || lang == null) return;
            var chk = NameRules.Check(CardRules.Compose(nameInput.text, frag), lang);
            if (chk.err != null) { statusText.text = chk.err; return; }
            StartCoroutine(ForgeRoutine(chk.name, tier, frag));
        }

        IEnumerator ForgeRoutine(string name, int t, Fragment fr)
        {
            busy = true; goBtn.interactable = false; statusText.text = "새기는 중…";
            ShowBlank(t, true);
            float t0 = Time.realtimeSinceStartup;
            Card card = null; string err = null;
            if (online != false)
            {
                var task = client.ForgeAsync(name, lang);
                while (!task.IsCompleted) yield return null;
                if (task.IsFaulted || task.IsCanceled) online = false;
                else
                {
                    var res = task.Result;
                    if (res.offline) online = false;
                    else if (res.value != null) { card = res.value; online = true; }
                    else { err = res.needCode ? "서버가 입장 코드를 요구합니다. 오른쪽 아래 '입장 코드' 칸에 넣으세요" : res.error; online = true; }
                }
                netText.text = online == true ? "서버: <color=#8be28b>연결됨</color>" : "서버: <color=#ffb86b>없음 — 견본 구슬만 열 수 있습니다</color>";
            }
            if (card == null && err == null)
            {
                card = samples.FirstOrDefault(c => c.name == name);
                if (card == null) err = "이 이름은 미리 만든 구슬에 없습니다 (서버를 켜면 어떤 이름이든 새길 수 있습니다)";
            }
            float wait = 0.7f - (Time.realtimeSinceStartup - t0);
            if (wait > 0f) yield return new WaitForSecondsRealtime(wait);
            busy = false; goBtn.interactable = true;
            if (err != null) { ClearBlank(); statusText.text = err; yield break; }

            card = CardRules.OnBlank(CardRules.MaybeVariant(card, rng), t, fr);
            Show(card);
            if (!save.collection.Any(c => c.Key == card.Key)) save.collection.Insert(0, card);
            SaveStore.Save(save);
            page = 0; RefreshShelf();
            nameInput.text = ""; DrawBlank();
            ShowStatus(card);
        }

        void ShowBlank(int t, bool forging)
        {
            ClearBlank();
            if (stageOrb != null) stageOrb.gameObject.SetActive(false);
            blankOrb = OrbView.CreateBlank(t, world, StagePos, forging);
        }

        void ClearBlank()
        {
            if (blankOrb != null) Destroy(blankOrb.gameObject);
            blankOrb = null;
            if (stageOrb != null) stageOrb.gameObject.SetActive(true);
        }

        void Show(Card c)
        {
            current = c; HideTip();
            ClearBlank();
            if (stageOrb != null) Destroy(stageOrb.gameObject);
            stageOrb = OrbView.Create(c, world, StagePos, false);
            stageOrb.PlayReveal();
            if (decor != null) Destroy(decor);
            decor = ThemeDecor.Spawn(c, decorAnchor, 1.7f);
            UpdateDeckBtn();
            ShowStatus(c);
        }

        void ShowStatus(Card c)
        {
            if (c.status == "ok")
            {
                var fx = c.effects ?? new List<CardEffect> { new CardEffect { name = c.effect } };
                statusText.text = string.Format("마나 {0} / {1}{2} · {3} · {4}", c.mana, c.cap, ManaWhy(c), c.element, fx.Count == 0 ? "효과 없음" : string.Join(" · ", fx.Select(e => e.name).ToArray()));
            }
            else if (c.status == "shattered") statusText.text = string.Format("{0}이 이름의 무게(마나 {1})를 견디지 못했습니다", Rules.Data.tiers[Mathf.Clamp(c.tier < 0 ? 2 : c.tier, 0, 3)].name, c.mana);
            else statusText.text = "구슬이 이름 대신 명령을 읽었습니다: " + (c.reason ?? "수상한 낙서");
        }

        static string ManaWhy(Card c)
        {
            if (!c.mana_stats.HasValue) return "";
            string fx = c.mana_effect != 0 ? string.Format(" {0} 효과 {1}", c.mana_effect > 0 ? "+" : "−", Math.Abs(c.mana_effect)) : "";
            return Rules.IsStatless(c.kind) ? string.Format(" (이름의 힘 {0}{1})", c.mana_power ?? 0, fx) : string.Format(" (이름의 힘 {0} · 수치 {1} 중 큰 쪽{2})", c.mana_power ?? 0, c.mana_stats ?? 0, fx);
        }

        // ------------------------------------------------------------------------------------------ shelf
        List<Card> AllCards()
        {
            var all = new List<Card>(save.collection);
            foreach (var s in samples) if (!save.collection.Any(c => c.name == s.name)) all.Add(s);
            return all;
        }

        void RefreshShelf()
        {
            foreach (var o in shelfOrbs) if (o != null) Destroy(o.gameObject);
            shelfOrbs.Clear();
            var all = AllCards();
            int pages = Mathf.Max(1, (all.Count + PageSize - 1) / PageSize);
            page = Mathf.Clamp(page, 0, pages - 1);
            for (int i = 0; i < PageSize; i++)
            {
                int k = page * PageSize + i; if (k >= all.Count) break;
                var pos = new Vector3(ShelfCenterX + (i % Cols - (Cols - 1) / 2f) * ShelfStep, ShelfY - (i / Cols) * ShelfStep, 0.4f);
                OrbView o;
                try { o = OrbView.Create(all[k], shelfRoot, pos, true); }
                catch (Exception e) { Debug.LogWarning("구슬을 그리지 못해 건너뜁니다: " + e.Message); continue; }   // one broken card must not blank the shelf
                if (deck.Contains(all[k].name)) o.MarkInDeck();
                shelfOrbs.Add(o);
            }
            pageText.text = string.Format("{0} / {1}  ·  직접 새긴 구슬 {2}개 · 견본 {3}개 (깨끗한 구슬 기준)", page + 1, pages, save.collection.Count, samples.Count);
        }

        // ------------------------------------------------------------------------------------ deck / hero
        void UpdateDeckBtn()
        {
            if (deckBtn == null) return;
            if (current == null || current.status != "ok") { deckBtn.interactable = false; UIKit.SetLabel(deckBtn, "덱에 넣기"); return; }
            bool inDeck = deck.Contains(current.name);
            UIKit.SetLabel(deckBtn, inDeck ? "덱에서 빼기" : "덱에 넣기");
            deckBtn.interactable = inDeck || deck.Count < Rules.Data.deck_max;
        }

        void ToggleDeck()
        {
            if (current == null || current.status != "ok") return;
            if (!deck.Remove(current.name) && deck.Count < Rules.Data.deck_max) deck.Add(current.name);
            DeckChanged();
        }

        void DeckChanged()
        {
            save.deck = new List<string>(deck); SaveStore.Save(save);
            RenderDeck(); RefreshShelf();
            if (heroRoutine != null) StopCoroutine(heroRoutine);
            heroRoutine = StartCoroutine(JudgeAfter(0.5f));
        }

        IEnumerator JudgeAfter(float delay) { yield return new WaitForSeconds(delay); yield return JudgeHero(); }

        void RenderDeck()
        {
            ClearChildren(deckChips);
            if (deck.Count == 0) UIKit.Label(deckChips, "비어 있음", 13, TextAnchor.MiddleLeft, UIKit.Dim);
            for (int i = 0; i < deck.Count; i++)
            {
                string n = deck[i];
                var b = UIKit.Btn(deckChips, n + " ×", () => { deck.Remove(n); DeckChanged(); }, 12);
            }
            deckCount.text = string.Format("{0} / {1}개", deck.Count, Rules.Data.deck_max);
            deckClearBtn.gameObject.SetActive(deck.Count > 0);
            UpdateDeckBtn();
        }

        IEnumerator JudgeHero()
        {
            if (deck.Count == 0) { heroSeq++; heroText.text = "<color=#b8c2d0>덱에 구슬을 넣으면 Jev가 덱 전체를 읽고 주인공을 정합니다.</color>"; yield break; }
            string key = SaveStore.DeckKey(deck);
            if (save.heroKey == key && save.hero != null) { heroSeq++; heroText.text = HeroRich(save.hero); yield break; }   // the same deck is not asked again
            int seq = ++heroSeq;
            heroText.text = "<color=#b8c2d0>덱을 읽는 중…</color>";
            var task = client.HeroAsync(new List<string>(deck), lang);
            while (!task.IsCompleted) yield return null;
            if (seq != heroSeq) yield break;                                // a newer deck change already asked again
            if (task.IsFaulted || task.IsCanceled || task.Result.offline) { heroText.text = "<color=#ffb86b>주인공 판정은 서버가 있어야 합니다. 오른쪽 아래에서 서버 주소를 확인하세요.</color>"; yield break; }
            var res = task.Result;
            if (res.value == null) { heroText.text = "<color=#ff7b7b>" + (res.error ?? "오류") + "</color>"; yield break; }
            save.heroKey = key; save.hero = res.value; SaveStore.Save(save);
            heroText.text = HeroRich(res.value);
        }

        static string Bar(double v) { int n = Mathf.Clamp(Mathf.RoundToInt((float)v), 0, 5); return new string('■', n) + new string('□', 5 - n); }

        static string HeroRich(Hero h)
        {
            var sb = new StringBuilder();
            sb.AppendLine("<size=20><b><color=" + UIKit.Gold + ">" + h.title + "</color></b></size>  <color=#b8c2d0>" + h.temper + " 기질</color>");
            sb.AppendLine("<b>패시브</b> " + h.passive);
            sb.AppendLine("공격성 " + Bar(h.aggression) + " " + h.aggression.ToString("0.0") + " / 5");
            sb.AppendLine("강인함 " + Bar(h.toughness) + " " + h.toughness.ToString("0.0") + " / 5");
            sb.Append("<size=12><color=#b8c2d0>");
            sb.Append(h.vague
                ? string.Format("덱의 색이 뚜렷하지 않습니다. (가장 가까운 것: {0} {1}%) 같은 결의 구슬을 더 모으면 정체가 드러납니다.", h.leaning, Mathf.RoundToInt((float)h.conf * 100))
                : string.Format("덱 {0}개를 읽은 결과 {1}% 확신. 다음으로 가까운 것은 {2} {3}%.", h.cards, Mathf.RoundToInt((float)h.conf * 100), h.runner_up, Mathf.RoundToInt((float)h.runner_up_conf * 100)));
            sb.Append("</color></size>");
            return sb.ToString();
        }

        // ------------------------------------------------------------------------------------- server
        void ApplyServerSettings()
        {
            client.baseUrl = string.IsNullOrWhiteSpace(urlInput.text) ? "http://localhost:8000" : urlInput.text.Trim();
            client.accessCode = codeInput.text.Trim();
            save.serverUrl = client.baseUrl; save.accessCode = client.accessCode; SaveStore.Save(save);
            online = null; netText.text = "서버: 주소를 바꿨습니다. 다음에 새길 때 연결합니다";
        }

        // ------------------------------------------------------------------------------------- tooltip
        void OnOrbHover(OrbView o, Vector2 screen)
        {
            if (o == null || Application.isMobilePlatform) return;     // touch has no hover: a tap on the big bead opens it (OnOrbClicked)
            ShowTip(o, screen);
        }
        void OnOrbHoverEnd(OrbView o) { if (tipFor == o) HideTip(); }
        void OnOrbClicked(OrbView o, Vector2 screen)
        {
            if (o == null) return;
            if (o.small) { Show(o.card); return; }                       // a bead on the shelf goes to the stage
            if (Application.isMobilePlatform) { if (tipFor == o) HideTip(); else ShowTip(o, screen); }
        }

        void ShowTip(OrbView o, Vector2 screen)
        {
            if (o.card == null) return;
            if (tipFor != o) tipText.text = TipRich(o.card);
            tipFor = o;
            tipPanel.gameObject.SetActive(true);
            bool right = screen.x > Screen.width * 0.6f, low = screen.y < Screen.height * 0.35f;
            tipPanel.pivot = new Vector2(right ? 1f : 0f, low ? 0f : 1f);
            tipPanel.position = screen + new Vector2(right ? -22f : 22f, low ? 22f : -22f);
        }

        void HideTip() { tipFor = null; if (tipPanel != null) tipPanel.gameObject.SetActive(false); }

        /// <summary>What a bead holds (port of tipHTML): element, kind, grade, mana, every effect (✦ unique gold, ◆ combo blue), themes, stats.</summary>
        static string TipRich(Card c)
        {
            var sb = new StringBuilder();
            sb.AppendLine("<size=20><b>" + c.name + "</b></size>");
            if (c.Scribble) { sb.AppendLine("<color=#b8c2d0>수상한 낙서</color>"); sb.Append(c.reason ?? "구슬이 이름이 아니라 명령을 읽었다"); return sb.ToString(); }
            int ti = Mathf.Clamp(c.tier < 0 ? 2 : c.tier, 0, 3);
            sb.AppendLine("<color=#b8c2d0>" + c.element + " · " + c.kind + " · " + Rules.Data.tiers[ti].name + "</color>   <b><color=" + UIKit.Gold + ">마나 " + c.mana + "</color></b>");
            var list = c.effects ?? new List<CardEffect> { new CardEffect { name = c.effect, desc = c.effect_desc, value = c.effect_value } };
            if (list.Count == 0) sb.AppendLine("<color=#b8c2d0>효과 없음</color>");
            foreach (var e in list)
            {
                string mark = e.unique ? "✦ " : e.combo ? "◆ " : "";
                string col = e.unique ? UIKit.Gold : e.combo ? UIKit.Blue : "#ffffff";
                sb.AppendLine("<b><color=" + col + ">" + mark + e.name + " " + e.value + "</color></b> " + e.desc + (e.combo && !string.IsNullOrEmpty(e.from) ? " <color=#b8c2d0>(" + e.from + ")</color>" : ""));
            }
            if (c.themes != null && c.themes.Count > 0) sb.AppendLine("<color=#b8c2d0>" + string.Join(" · ", c.themes.ToArray()) + "</color>");
            if (!Rules.IsStatless(c.kind)) sb.AppendLine("<color=#ff9b7a>공격 " + c.attack + "</color>   <color=#7ac2ff>방어 " + c.defense + "</color>");
            sb.Append(c.Shattered ? "<color=" + UIKit.Red + ">과부하 · 파손 — 마나 " + c.mana + " / 한계 " + c.cap + "</color>" : "<color=#b8c2d0>마나 " + c.mana + " / 한계 " + c.cap + "</color>");
            return sb.ToString();
        }

        void Update()
        {
            if (Screen.width != lastW || Screen.height != lastH) FitCamera();
            if (armed != null && Time.unscaledTime - armedAt > 3f) { UIKit.SetLabel(armed, armedLabel); armed = null; }
        }
    }
}

using System;
using UnityEngine;
using UnityEngine.UI;

namespace JevOrbs
{
    /// <summary>Tiny helpers that build uGUI in code, so the whole game needs no scene or prefab file.</summary>
    public static class UIKit
    {
        public static readonly Color PanelBg = new Color(0.09f, 0.11f, 0.16f, 0.84f);
        public static readonly Color BtnBg = new Color(0.22f, 0.29f, 0.40f, 0.96f);
        public static readonly Color BtnOn = new Color(0.88f, 0.64f, 0.22f, 1f);
        public static readonly Color TextCol = new Color(0.95f, 0.95f, 0.91f);
        public static readonly Color Dim = new Color(0.72f, 0.76f, 0.82f);
        public const string Gold = "#f2c75c", Blue = "#78b8ff", Red = "#ff7b7b";

        public static RectTransform Rect(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return (RectTransform)go.transform;
        }

        public static RectTransform Panel(Transform parent, string name, Color bg)
        {
            var r = Rect(name, parent);
            var img = r.gameObject.AddComponent<Image>(); img.color = bg;
            return r;
        }

        public static void Anchor(RectTransform r, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 pos, Vector2 size)
        {
            r.anchorMin = anchorMin; r.anchorMax = anchorMax; r.pivot = pivot; r.anchoredPosition = pos; r.sizeDelta = size;
        }

        public static Text Label(Transform parent, string text, int size = 16, TextAnchor anchor = TextAnchor.MiddleLeft, Color? color = null, bool bold = false)
        {
            var r = Rect("text", parent);
            var t = r.gameObject.AddComponent<Text>();
            t.font = JevFonts.UI; t.fontSize = size; t.alignment = anchor; t.color = color ?? TextCol; t.text = text;
            t.fontStyle = bold ? FontStyle.Bold : FontStyle.Normal;
            t.raycastTarget = false; t.supportRichText = true;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
            return t;
        }

        public static Button Btn(Transform parent, string label, Action onClick, int size = 15)
        {
            var r = Rect("btn_" + label, parent);
            var img = r.gameObject.AddComponent<Image>(); img.color = Color.white;
            var b = r.gameObject.AddComponent<Button>();
            b.targetGraphic = img;
            var cb = b.colors; cb.normalColor = BtnBg; cb.highlightedColor = new Color(0.34f, 0.44f, 0.60f); cb.pressedColor = BtnOn; cb.selectedColor = BtnBg;
            cb.disabledColor = new Color(0.2f, 0.22f, 0.26f, 0.6f); b.colors = cb;
            var t = Label(r, label, size, TextAnchor.MiddleCenter);
            Stretch(t.rectTransform, 4, 2);
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            if (onClick != null) b.onClick.AddListener(() => onClick());
            return b;
        }

        public static void SetLabel(Button b, string text) { var t = b.GetComponentInChildren<Text>(); if (t != null) t.text = text; }
        public static void SetSelected(Button b, bool on)
        {
            var cb = b.colors; cb.normalColor = on ? BtnOn : BtnBg; cb.selectedColor = cb.normalColor; b.colors = cb;
        }

        public static InputField Input(Transform parent, string placeholder, int size = 20)
        {
            var r = Rect("input", parent);
            var bg = r.gameObject.AddComponent<Image>(); bg.color = new Color(0.97f, 0.95f, 0.88f, 1f);
            var inp = r.gameObject.AddComponent<InputField>();
            var text = Label(r, "", size, TextAnchor.MiddleLeft, new Color(0.12f, 0.1f, 0.08f)); text.supportRichText = false; text.raycastTarget = true;
            Stretch(text.rectTransform, 8, 4);
            var ph = Label(r, placeholder, size, TextAnchor.MiddleLeft, new Color(0.45f, 0.42f, 0.36f)); ph.fontStyle = FontStyle.Italic;
            Stretch(ph.rectTransform, 8, 4);
            inp.textComponent = text; inp.placeholder = ph; inp.targetGraphic = bg; inp.lineType = InputField.LineType.SingleLine;
            return inp;
        }

        public static void Stretch(RectTransform r, float padX, float padY)
        {
            r.anchorMin = Vector2.zero; r.anchorMax = Vector2.one; r.offsetMin = new Vector2(padX, padY); r.offsetMax = new Vector2(-padX, -padY);
        }

        public static LayoutElement Size(GameObject go, float w = -1, float h = -1, float flexW = -1)
        {
            var le = go.GetComponent<LayoutElement>() ?? go.AddComponent<LayoutElement>();
            if (w >= 0) le.preferredWidth = w;
            if (h >= 0) le.preferredHeight = h;
            if (flexW >= 0) le.flexibleWidth = flexW;
            return le;
        }

        public static HorizontalLayoutGroup HRow(Transform parent, float spacing = 6, float height = 34)
        {
            var r = Rect("row", parent);
            var h = r.gameObject.AddComponent<HorizontalLayoutGroup>();
            h.spacing = spacing; h.childAlignment = TextAnchor.MiddleLeft;
            h.childControlWidth = true; h.childControlHeight = true; h.childForceExpandWidth = false; h.childForceExpandHeight = true;
            Size(r.gameObject, -1, height);
            return h;
        }

        public static VerticalLayoutGroup VStack(Transform parent, string name, float spacing = 8, int pad = 12)
        {
            var r = Rect(name, parent);
            var v = r.gameObject.AddComponent<VerticalLayoutGroup>();
            v.spacing = spacing; v.padding = new RectOffset(pad, pad, pad, pad);
            v.childControlWidth = true; v.childControlHeight = true; v.childForceExpandWidth = true; v.childForceExpandHeight = false;
            return v;
        }
    }
}

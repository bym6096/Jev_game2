const S = 34, SQ3 = Math.sqrt(3), R = 5;
let st = null, prev = null, sel = null, busy = false, pinned = null;
let history = [], startState = null, pv = null, pvSeq = 0, showPv = true, dragMoved = false;
const $ = (id) => document.getElementById(id);
const px = (q, r) => [S * SQ3 * (q + r / 2), S * 1.5 * r];
const hexPts = (cx, cy, s = S - 1.5) => Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 180 * (60 * i - 30); return `${(cx + s * Math.cos(a)).toFixed(1)},${(cy + s * Math.sin(a)).toFixed(1)}`; }).join(" ");
const key = (q, r) => q + "," + r;
const ROLE = { cast: "시전", build: "건물", summon: "소환", move: "이동", plant: "식물" };
const kindOf = (o) => (o.role === "build" && o.payload && o.payload[0] && (o.payload[0][0] === "grow" || (o.payload[0][0] === "harvest" && o.payload[0][2] === "food")) ? "plant" : o.role);
const RES = { wood: "나무", ore: "광석", food: "식량", gold: "골드" };
const GLYPH = { tree: "🌲", ore: "⛏" };

let accessCode = ""; try { accessCode = localStorage.getItem("proto-code") || ""; } catch (e) {}
async function api(op, body = {}) {
  const send = async () => {
    const res = await fetch("/api/app", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ op, code: accessCode, blob: st && st.blob, ...body }) });
    return res.json();
  };
  try {
    let v = await send();
    if (v.need_code) { const c = window.prompt("접근 코드를 입력하세요"); if (c) { accessCode = c; try { localStorage.setItem("proto-code", c); } catch (e) {} v = await send(); } }
    return v;
  } catch (e) { return { error: "서버에 연결하지 못했습니다. 잠시 뒤 다시 시도하세요." }; }
}
function toast(t) { const e = $("toast"); e.textContent = t; e.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => e.classList.remove("show"), 2400); }
function el(tag, attrs = {}, ...kids) { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; }
function svg(tag, attrs = {}, ...kids) { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); for (const k of kids) if (k != null) e.append(k); return e; }
/* ---------- 구슬 모양 (card-forge 참고) ----------
   색 = 효과 종류(+이름으로 살짝 변주), 크기 = 마나, 속무늬 = 구슬 종류, 겉에는 새긴 이름만. */
const VERB_COLOR = { damage: "#d8503f", drain: "#b8325a", guard: "#4b86dc", heal: "#4cbf86", money: "#e0b03a", steal: "#c99a2e", process: "#d19a3e", grow: "#7cbf4f", buff: "#e5863a", debuff: "#8f6bd8", control: "#6c5fd0", draw: "#37b6c8", recycle: "#37b6c8", trash: "#6e8796", peek: "#58a8d8", tempo: "#3aa0e8", energy: "#3aa0e8", create: "#d36ec0", amplify: "#e060a0", burn: "#ef6a2b", remove: "#7a8a92", transform: "#c070d0", move: "#6db7ea" };
const MAT_COLOR = { wood: "#5fa84f", ore: "#8a97a8", food: "#9ab84a", gold: "#e0b03a" };
const PATTERN = { build: "repeating-radial-gradient(circle at 50% 50%,#fff9 0 1px,#fff0 1px 8px)", summon: "repeating-conic-gradient(from 12deg at 50% 50%,#fff9 0 5deg,#fff0 5deg 20deg)", move: "radial-gradient(circle at 50% 60%,#fff8 0,#fff0 58%)", plant: "radial-gradient(circle at 28% 72%,#fff7 0,#fff0 42%),radial-gradient(circle at 72% 30%,#fff5 0,#fff0 36%)" };
const hash = (str) => { let h = 2166136261; for (const c of str) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
function hexToHsl(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255, g = parseInt(hex.slice(3, 5), 16) / 255, b = parseInt(hex.slice(5, 7), 16) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  let h = 0, sat = 0; if (d) { sat = d / (1 - Math.abs(2 * l - 1)); h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h *= 60; if (h < 0) h += 360; }
  return [h, sat * 100, l * 100];
}
function orbColor(o) {
  if (o.scribble) return "#777777";
  const verb = o.verb || (o.payload && o.payload[0] && o.payload[0][0]), mat = o.mat || (o.payload && o.payload[0] && o.payload[0][2]);
  const base = ((verb === "harvest" || verb === "grow") ? MAT_COLOR[mat] : VERB_COLOR[verb]) || VERB_COLOR[verb] || "#8a99a8", [h, sat, l] = hexToHsl(base), n = hash(o.name);
  return `hsl(${((h + (n % 25) - 12) + 360) % 360} ${Math.max(35, sat - (n >> 5) % 8)}% ${l + ((n >> 9) % 9) - 4}%)`;
}
const orbSize = (o) => Math.round(78 + Math.min(12, Math.max(0, o.mana ?? 4)) * 4.2);
// 이름은 두 줄까지: 공백이 있으면 가운데에 가까운 공백에서, 없으면 글자 사이에서 나눈다(한 줄이 구슬의 ~22%보다 작아지는 경우만).
function engrave(name, d) {
  const ch = [...name], wd = (c) => c === " " ? .3 : /[ᄀ-ᇿ㄰-㆏가-힯一-鿿぀-ヿ]/.test(c) ? 1 : .55;
  const span = (a, b) => ch.slice(a, b).reduce((t, c) => t + wd(c), 0), n = ch.length, total = span(0, n);
  let lines = [[0, n]];
  if (total > 3.4) {
    let best = null; const cut = !ch.includes(" ");
    for (let i = 1; i < n; i++) {
      if (ch[i] !== " " && !cut) continue; if (cut && n >= 4 && (i < 2 || n - i < 2)) continue;
      const a = [0, i], b = [ch[i] === " " ? i + 1 : i, n]; if (b[0] >= n) continue;
      const w = Math.max(span(...a), span(...b)); if (!best || w < best.w) best = { w, l: [a, b] };
    }
    if (best && best.w < total * .9) lines = best.l;
  }
  const maxW = Math.max(...lines.map((l) => span(...l)), .5);
  const fs = Math.max(9, Math.min(d * .27, d * (lines.length > 1 ? .68 : .74) / maxW, d * .56 / (lines.length * 1.12)));
  return { lines: lines.map(([a, b]) => ch.slice(a, b).join("").trim()), fs: Math.min(d * .32, fs) };
}
function sphere(o, d = orbSize(o)) {
  const e = engrave(o.name, d), eng = el("span", { class: "eng" });
  e.lines.forEach((l) => eng.append(el("span", { class: "ln" }, l)));
  return el("div", { class: "sphere" + (o.scribble ? " scribble" : ""), style: `--el:${orbColor(o)};--d:${d}px;--fs:${e.fs.toFixed(1)}px;--pat:${PATTERN[kindOf(o)] || "none"}` }, eng);
}
// 구슬 밑에 한 줄로 보이는 효과 요약(자세한 문장은 오른쪽 정보창)
const VERB_BRIEF = { damage: (m) => `피해 ${m}`, drain: (m) => `흡수 ${m}`, guard: (m) => `방어 +${m}`, heal: (m) => `회복 ${m}`, money: (m) => `골드 ${m}`, steal: (m) => `탈취 ${m}`, harvest: (m, t) => `${RES[t] || "자원"} +${m}`, grow: (m, t) => `${RES[t || "food"]} +${m}`, process: () => "가공", buff: (m, t) => `${BOOST_KO[t] || "피해"} +${m}%`, burn: (m) => `화상 ${m}`, debuff: () => "약화", control: () => "행동 불가", draw: () => "더 뽑기", recycle: () => "되돌림", trash: () => "폐기", peek: () => "엿보기", tempo: () => "마나 +1", energy: () => "마나 +", create: () => "생성", amplify: () => "다음 ×2", remove: () => "제거", transform: () => "변환" };
function brief(o) { if (o.scribble) return "낙서"; if (o.role === "move") return `${o.mv || 2}칸`; return (o.payload || []).filter((p) => p[0] !== "move").slice(0, 2).map(([v, m, t]) => (VERB_BRIEF[v] ? VERB_BRIEF[v](m, t) : v)).join(" · "); }
const bcostText = (o) => (o.role === "build" || (o.role === "summon" && !o.hostile)) && o.bcost ? `비용: ${RES[o.bcost[0]]} ${o.bcost[1]} + 골드 ${o.bcost[2]}` : "";

/* ---------- 흐름 ---------- */
async function newGame() {
  if (busy) return; busy = true; sel = null; pinned = null; prev = null; history = []; startState = null; pv = null;
  const v = await api("new", { stage_type: $("stype").value, job: $("job").value }); busy = false;
  if (v.error) return alert(v.error);
  st = v; $("over").hidden = true; $("app").hidden = false; resetMap(); render();
}
function render() {
  hideTip(); clearRange(); clearAoe();
  const setup = st.phase === "setup";
  $("setup").hidden = !setup; $("play").hidden = setup;
  if (setup) renderSetup();
  else { renderHud(); renderMap(); renderHand(); renderSide(); runDiff(); if (st.phase === "play") fetchPreview(); else { pv = null; renderPreview(); } }
  $("over").hidden = st.phase !== "over" && st.phase !== "exit"; if (st.phase === "over") renderOver(); else if (st.phase === "exit") renderExit();
  prev = st;
}

/* ---------- 구슬 만들기 ---------- */
function renderSetup() {
  const box = $("blanks"); box.innerHTML = "";
  st.blanks.forEach((b, i) => {
    const f = b.frag;
    const input = el("input", { type: "text", maxlength: String(b.max_typed), placeholder: `${b.max_typed}자까지`, "aria-label": `${b.tier} 빈 구슬 이름`, autocomplete: "off" });
    if (b.orb) input.disabled = true;
    const make = async () => {
      if (busy) return; if (!input.value.trim()) return toast("이름을 쓰세요");
      busy = true; btn.disabled = true; btn.textContent = "Jev가 읽는 중…";
      const v = await api("write", { idx: i, text: input.value }); busy = false;
      if (v.error) { toast(v.error); btn.disabled = false; btn.textContent = "구슬 만들기"; return; }
      st = v; renderSetup();
    };
    const btn = el("button", { class: "primary", type: "button", onclick: make }, "구슬 만들기");
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") make(); });
    if (b.orb) btn.hidden = true;
    const nm = el("div", { class: "namebox" });
    if (f && f.pos === "pre") nm.append(el("span", { class: "frag" }, f.t));
    nm.append(input);
    if (f && f.pos === "suf") nm.append(el("span", { class: "frag" }, (f.sp ? " " : "") + f.t));
    const h = b.hint, isHint = h && h.kind === "hint";       // 사전단어: 힌트(이름이 그 계열이면 ×1.2) 또는 변환(표대로 구슬을 바꿈)
    const card = el("div", { class: "blank" }, el("h3", {}, `${b.tier} 빈 구슬`, el("small", {}, `마나 한계 ${b.cap}${f ? (h ? (isHint ? " · 힌트가 붙어 있음" : " · 변환 말이 붙어 있음") : " · 새겨진 말이 붙어 있음") : " · 새겨진 말 없음"}`)), nm, btn);
    if (h && isHint) card.insertBefore(el("div", { class: "hintline" + (b.orb ? (b.orb.hint && b.orb.hint.ok ? " ok" : " miss") : "") }, el("b", {}, `힌트: ${h.label}`), ` — ${h.text}`, el("small", {}, b.orb ? (b.orb.hint && b.orb.hint.ok ? " ✓ 일치! 효과가 커졌습니다" : " ✗ 이번 이름은 이 계열이 아니었어요") : " · 따르지 않고 다른 이름을 써도 됩니다(시너지를 우선할 수 있어요)")), btn);
    if (h && !isHint) card.insertBefore(el("div", { class: "hintline mod" + (b.orb ? " ok" : "") }, el("b", {}, `새겨진 말 '${h.word}' → ${h.label}`), ` — ${h.text}`, el("small", {}, b.orb ? " ✓ 구슬에 적용됐습니다" : " · 이 말은 Jev가 읽지 않고, 내가 쓴 이름의 구슬을 표대로 바꿉니다")), btn);
    if (b.orb) card.append(el("div", { class: "made" + (b.orb.scribble ? " scr" : "") }, sphere(b.orb, orbSize(b.orb)), el("div", {}, el("b", {}, `${b.orb.name} · 마나 ${b.orb.mana}`), b.orb.text)));
    box.append(card);
  });
  document.querySelector(".bagbox summary").textContent = `가진 구슬 — ${st.job_name} (${st.bag_names.length}개)`;
  const jb = (st.jobs || []).find((j) => j.name === st.job_name); if (jb && st.stage_n === 1) $("setup-note").title = jb.desc;
  $("bagnames").replaceChildren(...st.bag_names.map((n) => el("span", {}, n)));
  const done = st.blanks.filter((b) => b.orb).length, nb = st.blanks.length;
  $("setup-note").textContent = `${st.stage_n}/${st.stages}스테이지${st.boss ? " (보스)" : ""} · 정산 ${st.due} · ` + (done < nb ? `만든 구슬 ${done}/${nb} · 건너뛰고 시작해도 됩니다` : "준비 완료");
  $("start").textContent = st.stage_n > 1 ? `${st.stage_n}스테이지 시작` : "스테이지 시작";
}

/* ---------- 상태 줄 ---------- */
function stat(name, label, ...kids) { return el("div", { class: "stat", "data-stat": name }, el("div", { class: "lb" }, label), ...kids); }
function renderHud() {
  const h = $("hud"); h.innerHTML = "";
  const cur = sel !== null ? st.hand.find((x) => x.idx === sel) : null, spend = cur ? cur.o.mana : 0;
  const hpPct = Math.max(0, st.hp) / st.max_hp * 100, goldPct = Math.min(100, st.gold / st.due * 100);
  const waveTurns = new Set((st.waves || []).map((w) => w[0]));
  const turns = el("div", { class: "turns", "aria-hidden": "true" });
  for (let t = 1; t <= st.turns; t++) turns.append(el("i", { class: (t < st.turn ? "done " : t === st.turn ? "now " : "") + (waveTurns.has(t) ? "wave" : ""), title: waveTurns.has(t) ? `${t}턴: 적이 몰려옵니다` : `${t}턴` }));
  const mana = el("div", { class: "mana", role: "img", "aria-label": `마나 ${st.mana}/${st.max_mana}` });
  for (let i = 0; i < Math.max(st.max_mana, st.mana); i++) mana.append(el("i", { class: i >= st.mana ? "off" : i >= st.mana - spend ? "spend" : "" }));
  h.append(
    stat("turn", `${st.stage_n}/${st.stages} ${st.stage_name}${st.boss ? " · 보스" : ""}`, el("div", { class: "v" }, `${Math.min(st.turn, st.turns)}턴`, el("small", {}, `/ ${st.turns}`)), turns),
    stat("hp", "체력", el("div", { class: "v" }, `${st.hp}`, el("small", {}, st.shield ? `방어 +${st.shield}` : `/ ${st.max_hp}`)), el("div", { class: "meter hp" + (hpPct < 30 ? " low" : "") }, el("i", { style: `width:${hpPct}%` }))),
    stat("mana", "마나", el("div", { class: "v" }, `${st.mana}`, el("small", {}, `/ ${st.max_mana}${spend ? ` (−${spend})` : ""}`)), mana),
    Object.assign(stat("gold", st.forecast && st.phase === "play" ? `골드 · 정산 예상 약 ${st.forecast.gold}` : "골드 · 정산까지", el("div", { class: "v" }, `${st.gold}`, el("small", {}, `/ ${st.due}${st.estates && st.estates.length ? ` · 영지 ${st.estates.length}` : ""}`)), el("div", { class: "meter gold" + (st.gold >= st.due ? " met" : "") }, el("i", { style: `width:${goldPct}%` }))), { className: "stat wide" }),
    stat("res", "자원", el("div", { class: "v res" }, el("span", { "data-stat": "wood" }, "🌲", el("b", {}, ` ${st.res.wood}`)), el("span", { "data-stat": "ore" }, "⛏", el("b", {}, ` ${st.res.ore}`)), el("span", { "data-stat": "food" }, "🌾", el("b", {}, ` ${st.res.food}`)))),
    stat("slots", "배치", el("div", { class: "v" }, `건물 ${st.buildings_n}/${st.caps.b}`, el("small", {}, `식물 ${st.plants_n}/${st.caps.p} · 소환 ${st.summons_n}/${st.caps.s}`))));
}

/* ---------- 지도 ---------- */
let hexLayer, rangeLayer, unitLayer, previewLayer, ghostLayer, fxLayer, floatLayer, units = new Map();
function resetMap() {
  const m = $("map"); m.innerHTML = ""; units = new Map();
  const defs = svg("defs", {}, svg("marker", { id: "arr", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" }, svg("path", { d: "M0,0 L10,5 L0,10 z", fill: "#ef7b7b" })));
  hexLayer = svg("g"); rangeLayer = svg("g"); unitLayer = svg("g"); previewLayer = svg("g", { class: "pvlayer" }); ghostLayer = svg("g", { class: "ghost" }); fxLayer = svg("g"); floatLayer = svg("g");
  m.append(defs, hexLayer, rangeLayer, unitLayer, previewLayer, ghostLayer, fxLayer, floatLayer);
}
function selCard() { return sel !== null && st ? st.hand.find((h) => h.idx === sel) : null; }
function renderMap() {
  const c = selCard();
  const ok = new Set(c ? c.tiles.map((t) => key(...t)) : []), hint = new Set(c ? c.hint.map((t) => key(...t)) : []);
  const res = new Map(st.tiles.map((t) => [key(t.q, t.r), t])), pos = st.pos || [0, 0];
  hexLayer.innerHTML = ""; ghostLayer.innerHTML = "";
  for (let q = -R; q <= R; q++) for (let r = Math.max(-R, -q - R); r <= Math.min(R, -q + R); r++) {
    const [x, y] = px(q, r), k = key(q, r), t = res.get(k);
    const cls = "hex" + (t ? " " + t.t : "") + (q === pos[0] && r === pos[1] ? " home" : "") + (ok.has(k) ? " ok" : "") + (hint.has(k) ? " hint" : "") + (c && c.need_target && hexd(q, r, pos[0], pos[1]) <= st.cast_range ? " cr" : "");
    const p = svg("polygon", { points: hexPts(x, y), class: cls });
    p.dataset.q = q; p.dataset.r = r;
    if (ok.has(k)) {
      p.addEventListener("click", () => playCard(sel, [q, r]));
      p.addEventListener("pointerenter", () => ghost(c, x, y)); p.addEventListener("pointerleave", () => ghostLayer.replaceChildren());
    } else if (t) p.addEventListener("pointerenter", () => inspectTile(t));
    hexLayer.append(p);
    if (t) hexLayer.append(svg("text", { x, y: y - 3, class: "mk" }, GLYPH[t.t]), svg("text", { x, y: y + 14, class: "amt" }, String(t.amt)));
    if (hint.has(k)) hexLayer.append(svg("text", { x: x + 17, y: y - 13, class: "star" }, "✦"));
  }
  syncUnits(); markTargets();
}
function ghost(c, x, y) {
  if (!c) return;
  const kd = kindOf(c.o), g = svg("g", { transform: `translate(${x},${y})` }, svg("rect", { x: -15, y: -15, width: 30, height: 30, rx: 8, class: kd === "build" ? "tok-b" : kd === "plant" ? "tok-g" : kd === "move" ? "tok-p" : "tok-s" }), svg("text", { y: 1, class: "glyph" }, { build: "🏠", plant: "🌱", move: "🧙" }[kd] || "🛡️"), svg("text", { y: 28, class: "ulab" }, c.o.name.slice(0, 5)));
  ghostLayer.replaceChildren(g);
}
// 유닛은 id로 이어 붙여 움직임이 부드럽게 보이게 한다.
function tokenFor(kind, d) {
  const g = svg("g", { class: "unit enter" });
  if (kind === "p") g.append(svg("circle", { r: 17, class: "tok-p" }), svg("text", { class: "glyph" }, "🧙"));
  else if (kind === "e") g.append(svg("circle", { r: d.boss ? 20 : 15, class: "tok-e" + (d.boss ? " boss" : "") }), svg("text", { class: "glyph", "data-g": "1" }, d.boss ? "🐉" : "👹"), svg("circle", { cx: 12, cy: -12, r: 8, fill: "#3a1418", stroke: "#ef7b7b", "stroke-width": 1.5 }), svg("text", { x: 12, y: -9, class: "badge" }, `${d.lvl}`));
  else if (kind === "s") g.append(svg("circle", { r: 15, class: "tok-s" }), svg("text", { class: "glyph" }, "🛡️"));
  else if (d.kind === "plant") g.append(svg("circle", { r: 15, class: "tok-g" }), svg("text", { class: "glyph", "data-pg": "1" }, "🌱"));
  else g.append(svg("rect", { x: -15, y: -15, width: 30, height: 30, rx: 8, class: "tok-b" }), svg("text", { class: "glyph" }, "🏠"));
  if (kind !== "p") {
    g.append(svg("rect", { x: -16, y: -26, width: 32, height: 5, rx: 2.5, class: "hpbg" }), svg("rect", { x: -16, y: -26, width: 32, height: 5, rx: 2.5, class: "hpfg " + (kind === "e" ? "e" : "a"), "data-hp": "1" }));
    if (kind !== "e") g.append(svg("text", { y: 28, class: "ulab" }, d.name.slice(0, 5)));
  }
  return g;
}
// 식물 모양: 씨앗 → 자라는 중 → 다 자라면 거두는 작물(식량 🌾 · 골드 🌻 · 나무 🌳)
const plantGlyph = (d) => (d.age === 0 ? "🌱" : d.age <= st.grow_turns ? "🌿" : { food: "🌾", gold: "🌻", wood: "🌳" }[d.mat] || "🌾");
function syncUnits() {
  const want = new Map();
  want.set("p", { kind: "p", d: { q: (st.pos || [0, 0])[0], r: (st.pos || [0, 0])[1] } });
  st.buildings.forEach((b) => want.set("b" + b.id, { kind: "b", d: b }));
  st.summons.forEach((u) => want.set("s" + u.id, { kind: "s", d: u }));
  st.enemies.forEach((e) => want.set("e" + e.id, { kind: "e", d: e }));
  for (const [id, u] of units) if (!want.has(id)) { u.g.classList.add("gone"); setTimeout(() => u.g.remove(), 350); units.delete(id); }
  for (const [id, { kind, d }] of want) {
    let u = units.get(id);
    const [x, y] = px(d.q, d.r), tf = `translate(${x}px,${y}px)`;
    if (!u) {
      u = { g: tokenFor(kind, d), kind }; units.set(id, u);
      u.g.style.transition = "none"; u.g.style.transform = tf; unitLayer.append(u.g);
      u.g.addEventListener("pointerenter", () => { inspectUnit(u); showRange(u); showAoe(u); }); u.g.addEventListener("pointerleave", () => { clearRange(); clearAoe(); });
      u.g.addEventListener("click", () => { const c = selCard(); if (c && c.need_target && u.kind === "e") return c.target_ids.includes(u.d.id) ? playCard(sel, null, u.d.id) : toast(`사거리(${st.cast_range}칸) 밖의 적입니다`); pinned = id; inspectUnit(u); });
      requestAnimationFrame(() => requestAnimationFrame(() => { u.g.style.transition = ""; u.g.classList.remove("enter"); }));
    } else u.g.style.transform = tf;
    u.d = d;
    const hp = u.g.querySelector("[data-hp]"); if (hp) hp.setAttribute("width", String(32 * Math.max(0, d.hp) / d.max));
    const gl = u.g.querySelector("[data-g]"); if (gl) gl.textContent = d.stun ? "💤" : d.boss ? "🐉" : "👹";
    const pg = u.g.querySelector("[data-pg]"); if (pg) pg.textContent = plantGlyph(d);
    u.g.dataset.uid = id;
  }
}
function floatAt(q, r, text, cls) {
  const [x, y] = px(q, r), t = svg("text", { x, y: y - 20, class: "float " + cls }, text);
  t.addEventListener("animationend", () => t.remove()); floatLayer.append(t);
}

/* ---------- 변화 알림(이전 상태와 비교) ---------- */
function runDiff() {
  if (!prev || prev.phase === "setup" || prev.stage_type !== st.stage_type || st.turn < prev.turn) return;
  const sign = (n) => (n > 0 ? "+" : "") + n;
  for (const [k, label] of [["enemies", "e"], ["buildings", "b"], ["summons", "s"]]) {
    const now = new Map(st[k].map((x) => [x.id, x]));
    for (const o of prev[k]) {
      const n = now.get(o.id);
      if (!n) floatAt(o.q, o.r, label === "e" ? "처치" : "파괴", label === "e" ? "kill" : "bad");
      else if (n.hp !== o.hp) floatAt(n.q, n.r, sign(n.hp - o.hp), n.hp < o.hp ? "dmg" : "heal");
    }
  }
  if (st.hp !== prev.hp) floatAt(0, 0, sign(st.hp - prev.hp), st.hp < prev.hp ? "dmg" : "heal");
  const pop = (name, d) => { const e = document.querySelector(`[data-stat="${name}"]`); if (e && d) { const s = el("span", { class: "pop " + (d > 0 ? "up" : "down") }, sign(d)); s.addEventListener("animationend", () => s.remove()); e.append(s); } };
  pop("gold", st.gold - prev.gold); for (const r of ["wood", "ore", "food"]) pop(r, st.res[r] - prev.res[r]);
}

/* ---------- 오른쪽 열 ---------- */
function inspectTile(t) { $("inspect").replaceChildren(el("b", {}, t.t === "tree" ? "나무 자원 칸" : "광석 자원 칸"), el("div", { class: "sub" }, `남은 양 ${t.amt}`), el("p", {}, "채집 건물을 이 칸 옆(1칸 이내)에 지으면 ×1.5로 모입니다.")); }
function inspectUnit(u) {
  const d = u.d, hp = `체력 ${d.hp}/${d.max}`;
  const box = $("inspect");
  if (u.kind === "p") box.replaceChildren(el("b", {}, "나"), el("div", { class: "sub" }, `체력 ${st.hp}/${st.max_hp}${st.shield ? ` · 방어 ${st.shield}` : ""}`), el("p", {}, "건물·식물·소환물은 내 주변 2칸 안에 놓을 수 있습니다. 이동 구슬로 자리를 옮길 수 있습니다."));
  else if (u.kind === "e") box.replaceChildren(el("b", {}, d.boss ? `보스 Lv${d.lvl}` : `적 Lv${d.lvl}`), el("div", { class: "sub" }, hp), el("p", {}, [d.stun ? "행동 불가" : "", d.weak ? "약화" : "", d.burn ? `화상 ${d.burn}` : ""].filter(Boolean).join(" · ") || "가장자리에서 걸어와 길을 막은 건물·소환물을 공격합니다."));
  else box.replaceChildren(...[el("b", {}, d.name), el("div", { class: "sub" }, `${d.kind === "plant" ? "식물" : u.kind === "b" ? "건물" : "소환물"} · ${hp}`), d.kind === "plant" ? el("p", {}, d.age <= st.grow_turns ? `자라는 중 — ${st.grow_turns + 1 - d.age}턴 뒤 수확 시작` : "다 자라서 매 턴 수확 중") : null, d.text ? el("p", { class: "sub" }, d.text) : null,
    u.kind === "b" && st.phase === "play" ? el("button", { type: "button", class: "mini", onclick: () => demolish(d.id), title: "마나 1, 재료 비용의 절반을 돌려받습니다" }, "철거 (마나 1)") : null].filter(Boolean));
}
let fxGroups = [];
const COND_KO = { hit: "피격 시", death: "사망 시", orb: "다른 구슬을 쓸 때", approach: "적이 다가오면", orb_attack: "공격 구슬을 쓸 때", orb_eco: "채집·수입 구슬을 쓸 때", orb_plant: "식물 구슬을 쓸 때", orb_build: "건물 구슬을 쓸 때", orb_summon: "소환 구슬을 쓸 때", orb_defense: "방어·회복 구슬을 쓸 때", kill: "적을 처치할 때", harvest: "자원을 거둘 때" };
const BOOST_KO = { dmg: "피해", burn: "화상", income: "골드 수입", growth: "채집·재배", defense: "방어·회복", unit: "건물·소환물" };
function groupFx() {
  const m = new Map(); st.fx.forEach((f) => { const k = f.name + "|" + f.kind; const g = m.get(k) || { f, n: 0 }; g.n++; m.set(k, g); }); return [...m.values()];
}
function fxInfo(g) {   // 작동 중인 효과 하나의 설명: 종류·남은 시간·발동 조건·문구
  const f = g.f, rows = [], kind = f.kind === "dur" ? "지속 효과" : f.kind === "trig" ? "조건부 효과" : f.kind === "mult" ? "증폭" : "대기 중인 효과";
  if (f.kind === "dur") { rows.push(["남은 시간", f.left == null ? "이번 스테이지가 끝날 때까지" : `${f.left}턴`]); if (f.charges != null && f.charges < 99) rows.push(["남은 횟수", `${f.charges}회`]); }
  if (f.kind === "trig") { rows.push(["발동 조건", COND_KO[f.cond] || f.cond]); if (f.uses != null && f.uses < 1000) rows.push(["남은 발동", `${f.uses}회`]); else rows.push(["남은 발동", "이번 스테이지가 끝날 때까지 (턴당 최대 2회)"]); }
  if (f.kind === "mult") { rows.push(["키우는 것", BOOST_KO[f.stat] || f.stat]); rows.push(["증폭", `+${f.pct}% (다른 구슬과 합산)`]); rows.push(["남은 시간", f.left == null ? "이번 스테이지가 끝날 때까지" : `${f.left}턴`]); }
  if (f.kind === "delay") rows.push(["발동", f.at - st.turn <= 0 ? "이번 턴 종료 시" : `${f.at - st.turn}턴 뒤 (${f.at}턴)`]);
  if (g.n > 1) rows.push(["겹침", `${g.n}개 (각각 따로 작동)`]);
  return { title: f.name, kind, rows, text: f.text };
}
function inspectFx(i) {
  const g = fxGroups[i]; if (!g) return false; const d = fxInfo(g);
  $("inspect").replaceChildren(el("b", {}, d.title), el("div", { class: "sub" }, d.kind), ...d.rows.map(([a, b]) => tipRow(a, b)), el("p", {}, d.text), el("p", { class: "sub" }, "같은 칩을 다시 누르면 닫힙니다.")); return true;
}
function renderSide() {
  fxGroups = groupFx();
  const c = selCard(), box = $("inspect");
  if (pinned && String(pinned).startsWith("fx:") && inspectFx(+String(pinned).slice(3))) { /* 작동 중인 효과를 눌러 둔 상태 */ }
  else if (pinned && units.get(pinned)) inspectUnit(units.get(pinned));
  else if (c) box.replaceChildren(el("b", {}, c.o.name), el("div", { class: "sub" }, `${ROLE[kindOf(c.o)] || c.o.role} · 마나 ${c.o.mana}`), el("p", {}, c.o.text), el("p", { class: "sub" }, c.need_tile ? (c.hint.length ? "초록 칸(✦)에 놓으면 보너스가 붙습니다. " : "노란 칸 중 하나를 고르세요. ") + "Enter(또는 더블클릭): 추천 칸에 바로 놓기 · 칸으로 끌어다 놓아도 됩니다." : c.need_target ? `지도의 적(금색 테두리, 내 위치에서 ${st.cast_range}칸 안)을 눌러 대상을 고르세요. Enter(또는 더블클릭): 가장 가까운 적.` : ""));
  else box.replaceChildren(el("b", {}, "정보"), el("p", { class: "sub" }, "구슬을 누르면 효과가, 지도 위의 칸·유닛에 올리면 상태가 여기에 보입니다."));
  const fx = $("effects"); fx.hidden = !fxGroups.length;
  if (fxGroups.length) fx.replaceChildren(el("h3", {}, "작동 중인 효과 (눌러서 보기)"), el("div", { class: "chips" }, ...fxGroups.map((g, i) => {
    const f = g.f, label = f.name + (f.kind === "delay" ? " (대기)" : f.kind === "trig" ? " (조건부)" : "") + (g.n > 1 ? ` ×${g.n}` : "");
    return el("button", { class: "chipbtn", type: "button", "data-fxi": String(i), "aria-pressed": String(pinned === "fx:" + i), onclick: () => { pinned = pinned === "fx:" + i ? null : "fx:" + i; renderSide(); } }, label);
  })));
  const nx = (st.waves || []).find((w) => w[0] > st.turn), f = $("forecast");
  f.replaceChildren(el("i"), el("span", {}, nx ? `다음 웨이브: ${nx[0] - st.turn}턴 뒤(${nx[0]}턴), 적 ${nx[1]}마리` : "남은 웨이브가 없습니다"));
  const lg = $("log"); lg.replaceChildren(...st.log.map((t) => el("div", {}, t))); lg.scrollTop = 1e6;
}

/* ---------- 손패 ---------- */
function renderHand() {
  const hd = $("hand"); hd.innerHTML = "";
  st.hand.forEach((h, n) => {
    const o = h.o, dis = !!h.why || st.phase !== "play", d = orbSize(o);
    let card0 = null;
    const card = el("div", { class: `orb r-${kindOf(o)}` + (dis ? " dis" : "") + (sel === h.idx ? " sel" : ""), style: `--d:${d}px`, "data-idx": String(h.idx), tabindex: "0", role: "listitem",
      "aria-label": `${o.name}, 마나 ${o.mana}, ${o.text}${h.why ? ", 쓸 수 없음: " + h.why : ""}`, "aria-disabled": String(dis),
      onclick: () => { if (dragMoved) { dragMoved = false; return; } if (dis) return toast(h.why || "지금은 쓸 수 없습니다"); playCard(h.idx); },
      onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); if (dis) toast(h.why || "지금은 쓸 수 없습니다"); else playCard(h.idx); } },
      onpointerenter: () => { if (sel === null && !pinned) peek(h); },
      onpointerdown: (e) => { if (!dis && (h.need_tile || h.need_target)) startDrag(e, h, card0); },
      ondblclick: () => { if (!dis && (h.need_tile || h.need_target)) quick(h); } },
      sphere(o, d), el("span", { class: "mbadge", "aria-hidden": "true" }, String(o.mana)));
    card0 = card;
    const cap = el("div", { class: "cap" }, el("span", { class: "role" }, ROLE[kindOf(o)] || o.role), brief(o));
    if (h.need_target) cap.append(el("span", { class: "cost" }, "대상을 직접 고름"));
    const bc = bcostText(o); if (bc) cap.append(el("span", { class: "cost" }, bc.replace("비용: ", "")));
    card.append(cap);
    if (h.why) card.append(el("div", { class: "why" }, h.why));
    if (n < 9) card.append(el("span", { class: "key", "aria-hidden": "true" }, String(n + 1)));
    hd.append(card);
  });
  if (!st.hand.length) hd.append(el("span", { class: "empty" }, "손패가 없습니다. 턴을 끝내면 새로 뽑습니다."));
  if (st.choice && st.phase === "play") hd.prepend(el("div", { class: "choice", role: "group", "aria-label": "구슬 고르기" }, el("b", {}, st.choice.kind === "exile" ? `${st.choice.src}: 이번 스테이지 동안 뺄 구슬 1개(${st.exile_word})` : `${st.choice.src}: 1개를 손패로`),
    ...st.choice.options.map((c) => el("button", { type: "button", title: c.text, onclick: () => pickChoice(c.k) }, `${c.name} · 마나 ${c.mana}`)), el("small", {}, "다른 구슬을 쓰거나 턴을 끝내면 사라집니다")));
  $("endturn").disabled = st.phase !== "play" || busy;
  const usable = st.hand.filter((h) => !h.why).length;
  $("endturn").classList.toggle("ready", st.phase === "play" && !usable);
  $("undo").disabled = busy || !history.length;
  $("piles").innerHTML = `주머니 ${st.bag} · 뽑을 것 ${st.draw} · 버린 것 ${st.disc}${st.exh ? ` · ${st.exile_word} ${st.exh}` : ""}<br><b>${usable ? `쓸 수 있는 구슬 ${usable}개 남음` : "더 쓸 구슬이 없어요"}</b>`;
}
function peek(h) { $("inspect").replaceChildren(el("b", {}, h.o.name), el("div", { class: "sub" }, `${ROLE[h.o.role] || h.o.role} · 마나 ${h.o.mana}`), el("p", {}, h.o.text)); }

/* ---------- 행동 ---------- */
async function playCard(idx, tile, target) {
  if (busy) return; const h = st.hand.find((x) => x.idx === idx); if (!h) return;
  pinned = null;
  if (h.need_tile && !tile) { sel = sel === idx ? null : idx; renderHud(); renderMap(); renderHand(); renderSide(); if (sel !== null) toast(h.o.role === "move" ? "이동할 칸을 고르세요" : h.hint.length ? "초록 칸(✦)을 추천합니다" : "놓을 칸을 고르세요"); return; }
  if (h.need_target && target === undefined) { sel = sel === idx ? null : idx; renderHud(); renderMap(); renderHand(); renderSide(); if (sel !== null) toast("공격할 적을 고르세요 (Enter: 가장 가까운 적)"); return; }
  busy = true; const v = await api("play", { idx, tile, target: typeof target === "number" ? target : undefined }); sel = null;
  if (v.error) { busy = false; return toast(v.error); }
  if (v.action && v.action.error) toast(v.action.error); else { pushHistory(); await playEvents(v.events); }
  busy = false; st = v; render();
}
async function endTurn() {
  if (busy || st.phase !== "play") return; busy = true; sel = null; pinned = null;
  $("endturn").disabled = true; $("endturn").firstChild.textContent = "적 행동 중…";
  const v = await api("end_turn"); $("endturn").firstChild.textContent = "턴 종료";
  if (v.error) { busy = false; toast(v.error); return render(); }
  pushHistory(); await playEvents(v.events); busy = false; st = v; render();
}
function renderOver() {
  const r = st.result, o = $("over");
  const rows = [["도달", `${r.stage} / ${r.stages}스테이지`], ["마지막 정산", r.clear ? "모두 통과" : r.died ? "쓰러짐 (런 종료)" : `골드 ${r.gold} / 필요 ${r.due}`], ["처치한 적(런 전체)", r.kills], ["골드 출처", `처치 ${r.src.g_bounty || 0} · 돈 구슬 ${r.src.g_money || 0} · 가공 ${r.src.g_process || 0} · 영지 ${r.src.g_estate || 0}`], ["영지", (st.estates || []).length + "곳"]];
  const t = el("table", {}); rows.forEach(([a, b]) => t.append(el("tr", {}, el("td", {}, a), el("td", {}, String(b)))));
  const again = el("button", { class: "primary big", type: "button", onclick: newGame }, "새 런 시작");
  o.replaceChildren(el("div", { class: "result", role: "dialog", "aria-modal": "true", "aria-label": "런 결과" }, el("h2", { class: r.clear ? "pass" : "fail" }, r.clear ? "런 클리어!" : "런 종료 — 처음부터 다시"), t, el("div", { class: "acts" }, el("button", { type: "button", onclick: () => { o.hidden = true; } }, "지도 보기"), startState ? el("button", { type: "button", title: "같은 맵·같은 주머니·같은 적 등장으로 다시 시작합니다", onclick: replay }, "같은 판 다시") : null, again)));
  setTimeout(() => again.focus(), 50);
}

function renderExit() {
  const r = st.result, o = $("over");
  const rows = [["낸 정산액", `${r.due}`], ["남은 골드", `${st.gold}`], ["자원(이월)", `🌲${st.res.wood} ⛏${st.res.ore} 🌾${st.res.food}`], ["영지", `${st.estates.length}곳 — 이후 스테이지마다 매 턴 생산`], ["다음 정산액", `${st.due_next}`]];
  if (r.sold) rows.splice(1, 0, ["모자란 골드", `자원 ${r.sold}개를 팔아 채움`]);
  const t = el("table", {}); rows.forEach(([a, b]) => t.append(el("tr", {}, el("td", {}, a), el("td", {}, String(b)))));
  const ex = el("div", { class: "exits" }, ...st.exits.map((x) => el("button", { type: "button", class: "exitbtn" + (x.boss ? " boss" : ""), onclick: () => goNext(x.i) },
    el("b", {}, `출구 ${x.i + 1}`), el("span", {}, `지형: ${x.type_hint}`), el("span", {}, `보상: ${x.reward_hint}`), x.boss ? el("span", { class: "down" }, "큰 그림자 — 보스") : null)));
  o.replaceChildren(el("div", { class: "result", role: "dialog", "aria-modal": "true", "aria-label": "정산 통과 — 출구 고르기" }, el("h2", { class: "pass" }, `${r.stage}스테이지 정산 통과`), t, el("h3", {}, "다음 스테이지로 갈 출구를 고르세요 (힌트는 일부만 보입니다)"), ex));
}
async function goNext(i) {
  if (busy) return; busy = true; const v = await api("next", { exit: i }); busy = false;
  if (v.error || (v.action && v.action.error)) return toast(v.error || v.action.error);
  st = v; history = []; startState = null; prev = null; resetMap(); render();
}
async function pickChoice(k) {
  if (busy) return; busy = true; const v = await api("pick", { k }); busy = false;
  if (v.error || (v.action && v.action.error)) return toast(v.error || v.action.error);
  pushHistory(); st = v; render();
}
async function demolish(id) {
  if (busy) return; busy = true; const v = await api("demolish", { id }); busy = false;
  if (v.error || (v.action && v.action.error)) return toast(v.error || v.action.error);
  pushHistory(); pinned = null; st = v; render(); toast("철거했습니다");
}

/* ---------- 입력 ---------- */
document.addEventListener("keydown", (e) => {
  if (!st || st.phase !== "play" || e.ctrlKey || e.metaKey || e.altKey) return;
  const tag = (e.target.tagName || "").toLowerCase(); if (tag === "input" || tag === "select") return;
  if (e.key >= "1" && e.key <= "9") { const h = st.hand[+e.key - 1]; if (h) { e.preventDefault(); if (h.why) toast(h.why); else if (sel === h.idx && h.need_tile) quick(h); else playCard(h.idx); } }
  else if (e.key === "z" || e.key === "Z" || e.key === "ㅋ") { e.preventDefault(); undo(); }
  else if (e.key === "Escape") { if (sel !== null) { sel = null; pinned = null; renderHud(); renderMap(); renderHand(); renderSide(); } }
  else if ((e.key === " " || e.key === "Enter") && tag !== "button" && !e.target.classList.contains("orb")) { e.preventDefault(); const c = selCard(); if (c) quick(c); else endTurn(); }
});
$("map").addEventListener("pointerleave", () => { if (st && st.phase === "play") renderSide(); });
$("newgame").addEventListener("click", newGame);
$("start").addEventListener("click", async () => { if (busy) return; busy = true; const v = await api("start"); busy = false; if (v.error) return toast(v.error); st = v; startState = v; history = []; resetMap(); render(); });
$("endturn").addEventListener("click", endTurn);
$("undo").addEventListener("click", undo);
document.addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && (e.key === "z" || e.key === "Z") && st && st.phase !== "setup") { e.preventDefault(); undo(); } });
newGame();


/* ---------- 되돌리기 · 같은 판 다시 ---------- */
function pushHistory() { history.push(st); if (history.length > 80) history.shift(); }
function undo() {
  if (busy || !st || st.phase === "setup") return;
  if (!history.length) return toast("되돌릴 행동이 없습니다");
  st = history.pop(); sel = null; pinned = null; prev = null; $("over").hidden = true; render(); toast("되돌렸습니다");
}
function replay() { if (!startState) return; st = startState; history = []; sel = null; pinned = null; prev = null; $("over").hidden = true; resetMap(); render(); }

/* ---------- 빠른 배치 · 끌어다 놓기 ---------- */
const bestTile = (c) => (c.hint.length ? c.hint[0] : c.tiles[0]);
function quick(h) { if (h.o.role === "move") return playCard(h.idx); if (h.need_target) return playCard(h.idx, null, "auto"); if (!h.tiles.length) return toast("놓을 수 있는 칸이 없습니다"); playCard(h.idx, bestTile(h)); }
function startDrag(e, h, cardEl) {
  if (e.button > 0 || busy) return;
  const x0 = e.clientX, y0 = e.clientY; let dragging = false, chip = null, over = null;
  const pick = (x, y) => {   // 칸을 놓는 구슬은 놓을 수 있는 칸, 대상을 고르는 구슬은 적
    const t = document.elementFromPoint(x, y); if (!t || !t.closest) return null;
    if (h.need_target) { const g = t.closest("g.unit"), id = g && g.dataset.uid || ""; return id[0] === "e" && h.target_ids.includes(+id.slice(1)) ? g : null; }
    return t.closest(".hex.ok");
  };
  const move = (ev) => {
    if (!dragging) {
      if (Math.hypot(ev.clientX - x0, ev.clientY - y0) < 8) return;
      dragging = true; dragMoved = true; sel = h.idx; renderHud(); renderMap(); renderSide();
      document.querySelectorAll(".orb.sel").forEach((n) => n.classList.remove("sel")); cardEl.classList.add("sel");
      chip = el("div", { class: "dragchip" }, sphere(h.o, 68)); document.body.append(chip); hideTip();
    }
    chip.style.transform = `translate(${ev.clientX - 34}px,${ev.clientY - 34}px)`;
    const t = pick(ev.clientX, ev.clientY);
    if (t !== over) { if (over) over.classList.remove("drop"); over = t; if (over) over.classList.add("drop"); clearAoe(); if (over && h.need_target) showAoe(units.get(over.dataset.uid)); }
  };
  const end = (ev) => {
    window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", end); window.removeEventListener("pointercancel", end);
    if (!dragging) return;
    if (chip) chip.remove(); clearAoe();
    const t = ev.type === "pointerup" ? pick(ev.clientX, ev.clientY) : null;
    setTimeout(() => { dragMoved = false; }, 0);
    if (t && h.need_target) playCard(h.idx, null, units.get(t.dataset.uid).d.id);
    else if (t) playCard(h.idx, [+t.dataset.q, +t.dataset.r]);
    else { sel = null; renderHud(); renderMap(); renderHand(); renderSide(); toast(h.need_target ? "적 위에 놓아야 합니다" : "칸 위에 놓아야 합니다"); }
  };
  window.addEventListener("pointermove", move); window.addEventListener("pointerup", end); window.addEventListener("pointercancel", end);
}

/* ---------- 턴 종료 예측 ---------- */
async function fetchPreview() {
  const my = ++pvSeq; if (previewLayer) previewLayer.innerHTML = ""; $("turnpreview").classList.add("stale");
  const v = await api("preview"); if (my !== pvSeq) return;
  pv = v && v.preview ? v.preview : null; $("turnpreview").classList.remove("stale"); renderPreview();
}
function renderPreview() {
  const box = $("turnpreview"), L = previewLayer; if (L) L.innerHTML = "";
  const head = el("div", { class: "pvhead" }, el("h3", {}, "턴 종료하면"), el("button", { type: "button", class: "mini", "aria-pressed": String(showPv), title: "지도에 적 이동·피해 예측을 겹쳐 보입니다", onclick: () => { showPv = !showPv; renderPreview(); } }, showPv ? "지도 표시 끄기" : "지도 표시 켜기"));
  if (!st || st.phase !== "play") { box.replaceChildren(head, el("p", { class: "sub" }, "플레이 중에 표시됩니다.")); return; }
  if (!pv) { box.replaceChildren(head, el("p", { class: "sub" }, "계산 중…")); return; }
  const sg = (n) => (n > 0 ? "+" : n < 0 ? "−" : "") + Math.abs(n);
  const rows = [];
  if (pv.over) {
    const r = pv.result; rows.push(el("div", { class: "pvrow" }, el("span", {}, "마지막 턴입니다 · 정산 예상"), el("b", { class: r.pass ? "up" : "down" }, `골드 ${r.gold} / ${r.due} ${r.pass ? "통과" : "실패"}`)));
    if (r.died) rows.push(el("div", { class: "pvrow" }, el("span", {}, "체력이 바닥나 쓰러집니다"), el("b", { class: "down" }, "골드 몰수")));
  } else {
    if (pv.gold) rows.push(el("div", { class: "pvrow" }, el("span", {}, "골드"), el("b", { class: pv.gold > 0 ? "up" : "down" }, sg(pv.gold))));
    const rs = ["wood", "ore", "food"].filter((k) => pv.res[k]).map((k) => `${{ wood: "🌲", ore: "⛏", food: "🌾" }[k]}${sg(pv.res[k])}`);
    if (rs.length) rows.push(el("div", { class: "pvrow" }, el("span", {}, "자원"), el("b", { class: "up" }, rs.join("  "))));
    if (pv.hp) rows.push(el("div", { class: "pvrow" }, el("span", {}, "체력"), el("b", { class: pv.hp > 0 ? "up" : "down" }, sg(pv.hp))));
    if (pv.kills) rows.push(el("div", { class: "pvrow" }, el("span", {}, "적 처치"), el("b", { class: "up" }, `${pv.kills}마리`)));
    for (const o of pv.own) rows.push(el("div", { class: "pvrow" }, el("span", {}, `${o.name} (${o.kind === "summons" ? "소환" : ((st.buildings.find((b) => b.id === o.id) || {}).kind === "plant" ? "식물" : "건물")})`), el("b", { class: "down" }, o.lost ? "파괴됨" : `피해 −${o.dmg}`)));
    if (pv.spawn) rows.push(el("div", { class: "pvrow" }, el("span", {}, "새 적 등장"), el("b", { class: "down" }, `${pv.spawn}마리`)));
  }
  if (!rows.length) rows.push(el("p", { class: "sub" }, "큰 변화가 없습니다."));
  box.replaceChildren(head, ...rows);
  if (!showPv || !L) return;
  for (const m of pv.moves) {
    const [x1, y1] = px(...m.from), [x2, y2] = px(...m.to), dx = x2 - x1, dy = y2 - y1, d = Math.hypot(dx, dy) || 1, k = 14 / d;
    L.append(svg("line", { x1: x1 + dx * k, y1: y1 + dy * k, x2: x2 - dx * k, y2: y2 - dy * k, class: "pv-arrow", "marker-end": "url(#arr)" }));
  }
  for (const [q, r] of pv.dead) { const [x, y] = px(q, r); L.append(svg("text", { x, y: y + 7, class: "pv-x gold" }, "✕")); }
  for (const [q, r] of pv.spawned) { const [x, y] = px(q, r); L.append(svg("polygon", { points: hexPts(x, y), class: "pv-spawn" })); }
  for (const o of pv.own) { const [x, y] = px(o.q, o.r); L.append(o.lost ? svg("text", { x, y: y + 7, class: "pv-x" }, "✕") : svg("text", { x: x + 15, y: y - 12, class: "pv-dmg" }, `−${o.dmg}`)); }
}


/* ---------- 툴팁: 구슬·유닛·칸에 마우스를 올리면 커서 옆에 뜬다(오른쪽 정보창은 그대로) ---------- */
let tipEl = null, tipKey = null;
function hideTip() { if (tipEl) tipEl.hidden = true; tipKey = null; }
function placeTip(e) {
  const w = tipEl.offsetWidth, h = tipEl.offsetHeight; let x = e.clientX + 16, y = e.clientY + 16;
  if (x + w > innerWidth - 8) x = e.clientX - w - 16; if (y + h > innerHeight - 8) y = innerHeight - h - 8; if (x < 8) x = 8;
  tipEl.style.transform = `translate(${x}px,${Math.max(8, y)}px)`;
}
function showTip(c, e) {
  if (!tipEl) return; if (tipKey !== c.key) { tipEl.replaceChildren(c.build()); tipKey = c.key; }
  tipEl.hidden = false; placeTip(e);
}
const tipRow = (label, val, cls = "") => el("div", { class: "tiprow" }, el("span", {}, label), el("b", { class: cls }, val));
function tipOrb(h) {
  const o = h.o, kd = kindOf(o), bc = bcostText(o).replace("비용: ", "");
  return { key: `o${h.idx}:${h.iid}:${st.mana}`, build: () => el("div", { class: "tipbox r-" + kd },
    el("div", { class: "tiph" }, el("b", {}, o.name), el("span", { class: "tipm" }, `마나 ${o.mana}`)),
    el("div", { class: "tipk" }, ROLE[kd] || o.role),
    el("p", {}, o.text),
    bc ? tipRow("재료", bc) : null,
    kd === "plant" ? tipRow("성장", `${st.grow_turns}턴 자란 뒤 수확`) : null,
    kd === "move" ? tipRow("이동", `주변 ${o.mv || 2}칸 안의 빈 칸`) : null,
    h.need_target ? tipRow("대상", "직접 고름") : null,
    o.role === "cast" && o.payload.some((p) => ENEMY_V.includes(p[0])) ? tipRow("사거리", `${st.cast_range}칸 (내 위치 기준)`) : null,
    h.why ? el("div", { class: "tipwhy" }, h.why) : el("div", { class: "tiphint" }, h.need_target ? "눌러서 대상 고르기 · 적에게 끌어다 놓기 · 더블클릭: 가장 가까운 적" : h.need_tile ? (kd === "move" ? "눌러서 이동할 칸 고르기" : "눌러서 칸 고르기 · 끌어다 놓기 · 더블클릭: 추천 칸") : "눌러서 바로 쓰기")) };
}
function tipUnit(u) {
  const d = u.d, hp = `${d.hp}/${d.max}`;
  return { key: `u${u.g.dataset.uid}:${d.hp}:${d.q},${d.r}:${pvSeq}:${d.age ?? ""}`, build: () => {
    if (u.kind === "p") return el("div", { class: "tipbox" }, el("div", { class: "tiph" }, el("b", {}, "나")), tipRow("체력", `${st.hp}/${st.max_hp}`), st.shield ? tipRow("방어", `+${st.shield}`) : null, tipRow("마나", `${st.mana}/${st.max_mana}`), el("p", {}, "건물·식물·소환물은 내 주변 2칸 안에 놓을 수 있습니다."));
    if (u.kind === "e") {
      const mv = pv && pv.moves.find((m) => m.id === d.id);
      return el("div", { class: "tipbox r-enemy" }, el("div", { class: "tiph" }, el("b", {}, d.boss ? `보스 Lv${d.lvl}` : `적 Lv${d.lvl}`)), tipRow("체력", hp, "down"), d.stun ? tipRow("상태", "행동 불가") : null, d.weak ? tipRow("상태", "약화(피해 ×1.5로 받음)") : null, d.burn ? tipRow("상태", `화상 ${d.burn}중첩 (턴마다 ${d.burn * 2} 피해)`, "down") : null,
        el("p", {}, d.stun ? "이번 턴에는 움직이지 못합니다." : "가장자리에서 걸어와 길을 막은 건물·식물·소환물을 공격합니다."), pv ? el("div", { class: "tiphint" }, mv ? "이번 턴 종료 시: 한 칸 이동" : "이번 턴 종료 시: 제자리(공격 중일 수 있음)") : null);
    }
    const hit = pv && pv.own.find((o) => o.id === d.id), plant = d.kind === "plant";
    const grow = plant ? (d.age <= st.grow_turns ? `자라는 중 — ${st.grow_turns + 1 - d.age}턴 뒤 수확 시작` : "다 자라서 매 턴 수확 중") : null;
    return el("div", { class: "tipbox r-" + (plant ? "plant" : u.kind === "s" ? "summon" : "build") }, el("div", { class: "tiph" }, el("b", {}, d.name), el("span", { class: "tipm" }, plant ? "식물" : u.kind === "s" ? "소환물" : "건물")),
      tipRow("체력", hp), grow ? tipRow("성장", grow, d.age <= st.grow_turns ? "" : "up") : null, ...rangeRows(d), d.text ? el("p", {}, d.text) : null,
      hit ? el("div", { class: "tipwhy" }, hit.lost ? "이번 턴 종료 시 파괴됩니다" : `이번 턴 종료 시 피해 −${hit.dmg}`) : null);
  } };
}
function tipTile(h) {
  const q = +h.dataset.q, r = +h.dataset.r, t = st.tiles.find((x) => x.q === q && x.r === r), ok = h.classList.contains("ok"), c = selCard();
  if (!t && !ok) return null;
  return { key: `t${q},${r}:${t ? t.amt : ""}:${ok}:${sel}`, build: () => el("div", { class: "tipbox" },
    t ? el("div", { class: "tiph" }, el("b", {}, t.t === "tree" ? "나무 자원 칸" : "광석 자원 칸")) : el("div", { class: "tiph" }, el("b", {}, c && c.o.role === "move" ? "이동할 수 있는 칸" : "놓을 수 있는 칸")),
    t ? tipRow("남은 양", String(t.amt)) : null,
    t ? el("p", {}, "채집 건물을 이 칸 옆(1칸 이내)에 지으면 ×1.5로 모입니다.") : null,
    ok && h.classList.contains("hint") ? el("div", { class: "tiphint" }, "보너스 칸: 맞는 자원 옆이거나 다른 계열 건물 옆") : null,
    ok && c ? el("div", { class: "tiphint" }, `${c.o.name} — ${c.o.role === "move" ? "여기로 이동" : "여기에 놓기"}`) : null) };
}
function wireTips() {
  tipEl = el("div", { id: "tip", role: "tooltip", hidden: "" }); document.body.append(tipEl);
  const track = (root, resolve) => { root.addEventListener("pointermove", (e) => { if (!st || e.buttons) return hideTip(); const c = resolve(e.target); if (c) showTip(c, e); else hideTip(); }); root.addEventListener("pointerleave", hideTip); };
  track($("map"), (t) => { const g = t.closest && t.closest("g.unit"); if (g && g.dataset.uid && units.get(g.dataset.uid)) return tipUnit(units.get(g.dataset.uid)); const hx = t.closest && t.closest(".hex"); return hx ? tipTile(hx) : null; });
  track($("hand"), (t) => { const c = t.closest && t.closest(".orb"); const h = c && st.hand.find((x) => String(x.idx) === c.dataset.idx); return h ? tipOrb(h) : null; });
}
wireTips();


/* ---------- 대상 고르기 표시 · 사거리 표시 ---------- */
const ENEMY_V = ["damage", "drain", "debuff", "control", "burn"];
const AUTO_TG = { single: "가장 가까운 적 1", line: "가까운 적 2", around: "가장 가까운 적 주변 무리(1칸)", wide: "사거리 안의 모든 적" };
const hexd = (q1, r1, q2, r2) => (Math.abs(q1 - q2) + Math.abs(r1 - r2) + Math.abs(q1 - q2 + r1 - r2)) / 2;
function rangeRows(d) {
  const v = d.verbs || [];
  if (v.some((x) => ENEMY_V.includes(x))) return [tipRow("사거리", `${d.range}칸`), tipRow("대상", AUTO_TG[d.rng] || "가장 가까운 적"), tipRow("행동", "매 턴 종료 시 자동으로 공격")];
  if (v.includes("harvest")) return [tipRow("채집 범위", "1칸 (자원 칸 옆)")];
  return [];
}
function showRange(u) {
  rangeLayer.innerHTML = ""; if (!st || (u.kind !== "b" && u.kind !== "s")) return;
  const d = u.d, v = d.verbs || [], atk = v.some((x) => ENEMY_V.includes(x)), eco = v.includes("harvest"), lim = atk ? d.range : eco ? 1 : 0; if (!lim) return;
  const res = new Set(st.tiles.map((t) => key(t.q, t.r)));
  for (let q = -R; q <= R; q++) for (let r = Math.max(-R, -q - R); r <= Math.min(R, -q + R); r++) {
    if (hexd(q, r, d.q, d.r) > lim) continue; const [x, y] = px(q, r);
    rangeLayer.append(svg("polygon", { points: hexPts(x, y), class: atk ? "rng" : res.has(key(q, r)) ? "rng-eco" : "rng-dim" }));
  }
}
function clearRange() { if (rangeLayer) rangeLayer.innerHTML = ""; }
function markTargets() {   // 고를 수 있는 적(사거리 안)은 금색 테두리, 사거리 밖의 적은 흐리게
  const c = selCard(), on = !!(c && c.need_target), ids = new Set(on ? c.target_ids.map((i) => "e" + i) : []);
  for (const [id, u] of units) { u.g.classList.toggle("tgt", on && ids.has(id)); u.g.classList.toggle("far", on && u.kind === "e" && !ids.has(id)); u.g.classList.remove("tgt-hit"); }
}
function aoeSet(c, e) {   // 서버의 targets()와 같은 규칙: 고른 적 + (두 명이면 그 옆의 가장 가까운 적 / 주변 무리면 1칸 안 / 전체면 모두)
  const rest = [...units.values()].filter((x) => x.kind === "e" && x.d.id !== e.id && c.target_ids.includes(x.d.id)).map((x) => x.d).sort((a, b) => hexd(a.q, a.r, e.q, e.r) - hexd(b.q, b.r, e.q, e.r) || a.id - b.id), rng = c.o.rng;
  if (rng === "single") return [e]; if (rng === "line") return [e, ...rest.slice(0, 1)];
  if (rng === "around") return [e, ...rest.filter((x) => hexd(x.q, x.r, e.q, e.r) <= 1)].slice(0, 6);
  return [e, ...rest];
}
function showAoe(u) {
  clearAoe(); const c = selCard(); if (!u || !c || !c.need_target || u.kind !== "e") return;
  const ids = new Set(aoeSet(c, u.d).map((x) => x.id)); for (const x of units.values()) if (x.kind === "e" && ids.has(x.d.id)) x.g.classList.add("tgt-hit");
}
function clearAoe() { for (const x of units.values()) x.g.classList.remove("tgt-hit"); }

/* ---------- 간단한 이펙트: 공격 줄·충격·생산 숫자·발동 표시 (서버가 돌려준 events를 순서대로) ---------- */
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const BOLT = { damage: "#ffd36b", burn: "#ef6a2b", drain: "#e0558a", debuff: "#a98cf5", control: "#6db7ea", enemy: "#ef7b7b" };
async function playEvents(evs) {
  if (!evs || !evs.length || !fxLayer) return;
  if (previewLayer) previewLayer.innerHTML = "";
  const n = evs.length, gap = Math.max(28, Math.min(130, 1000 / n));
  evs.forEach((e, i) => setTimeout(() => drawEvent(e), i * gap));
  await sleep(Math.min(1300, (n - 1) * gap + 360));
}
function drawEvent(e) {
  if (e.k === "hit" && e.b) {
    const [x1, y1] = px(...e.a), [x2, y2] = px(...e.b), col = BOLT[e.kind] || "#ffd36b", len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const line = svg("line", { x1, y1, x2, y2, class: "bolt", style: `stroke:${col};--len:${len.toFixed(0)}` }), dot = svg("circle", { cx: x2, cy: y2, r: 7, class: "impact", style: `fill:${col}` }), src = svg("circle", { cx: x1, cy: y1, r: 9, class: "muzzle", style: `stroke:${col}` });
    [line, dot, src].forEach((n) => { n.addEventListener("animationend", () => n.remove()); fxLayer.append(n); });
  } else if (e.k === "pop") floatAt(e.a[0], e.a[1], e.text, { up: "heal", down: "bad", trig: "trig" }[e.tone] || "gain");
}

function tipFx(i) {
  const g = fxGroups[i]; if (!g) return null; const d = fxInfo(g);
  return { key: `fx${i}:${d.title}:${st.turn}:${g.n}:${g.f.left}:${g.f.uses}`, build: () => el("div", { class: "tipbox r-cast" }, el("div", { class: "tiph" }, el("b", {}, d.title), el("span", { class: "tipm" }, d.kind)), ...d.rows.map(([a, b]) => tipRow(a, b)), el("p", {}, d.text), el("div", { class: "tiphint" }, "눌러서 오른쪽 정보창에 고정")) };
}
(function () { const root = $("effects"); root.addEventListener("pointermove", (e) => { const c = e.target.closest && e.target.closest("[data-fxi]"); const t = c && tipFx(+c.dataset.fxi); if (t) showTip(t, e); else hideTip(); }); root.addEventListener("pointerleave", hideTip); })();

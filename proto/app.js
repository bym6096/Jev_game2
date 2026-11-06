const S = 34, SQ3 = Math.sqrt(3), R = 5;
let st = null, prev = null, sel = null, busy = false, pinned = null;
let history = [], startState = null, pv = null, pvSeq = 0, showPv = true, dragMoved = false;
const $ = (id) => document.getElementById(id);
const px = (q, r) => [S * SQ3 * (q + r / 2), S * 1.5 * r];
const hexPts = (cx, cy, s = S - 1.5) => Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 180 * (60 * i - 30); return `${(cx + s * Math.cos(a)).toFixed(1)},${(cy + s * Math.sin(a)).toFixed(1)}`; }).join(" ");
const key = (q, r) => q + "," + r;
const ROLE = { cast: "시전", build: "건물", summon: "소환", move: "이동" };
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
const VERB_COLOR = { damage: "#d8503f", drain: "#b8325a", guard: "#4b86dc", heal: "#4cbf86", money: "#e0b03a", steal: "#c99a2e", process: "#d19a3e", grow: "#7cbf4f", buff: "#e5863a", debuff: "#8f6bd8", control: "#6c5fd0", draw: "#37b6c8", recycle: "#37b6c8", trash: "#6e8796", peek: "#58a8d8", tempo: "#3aa0e8", energy: "#3aa0e8", create: "#d36ec0", amplify: "#e060a0", remove: "#7a8a92", transform: "#c070d0" };
const MAT_COLOR = { wood: "#5fa84f", ore: "#8a97a8", food: "#9ab84a", gold: "#e0b03a" };
const PATTERN = { build: "repeating-radial-gradient(circle at 50% 50%,#fff9 0 1px,#fff0 1px 8px)", summon: "repeating-conic-gradient(from 12deg at 50% 50%,#fff9 0 5deg,#fff0 5deg 20deg)", move: "radial-gradient(circle at 50% 60%,#fff8 0,#fff0 58%)" };
const hash = (str) => { let h = 2166136261; for (const c of str) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
function hexToHsl(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255, g = parseInt(hex.slice(3, 5), 16) / 255, b = parseInt(hex.slice(5, 7), 16) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  let h = 0, sat = 0; if (d) { sat = d / (1 - Math.abs(2 * l - 1)); h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h *= 60; if (h < 0) h += 360; }
  return [h, sat * 100, l * 100];
}
function orbColor(o) {
  if (o.scribble) return "#777777";
  const verb = o.verb || (o.payload && o.payload[0] && o.payload[0][0]), mat = o.mat || (o.payload && o.payload[0] && o.payload[0][2]);
  const base = (verb === "harvest" ? MAT_COLOR[mat] : VERB_COLOR[verb]) || "#8a99a8", [h, sat, l] = hexToHsl(base), n = hash(o.name);
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
  return el("div", { class: "sphere" + (o.scribble ? " scribble" : ""), style: `--el:${orbColor(o)};--d:${d}px;--fs:${e.fs.toFixed(1)}px;--pat:${PATTERN[o.role] || "none"}` }, eng);
}
// 구슬 밑에 한 줄로 보이는 효과 요약(자세한 문장은 오른쪽 정보창)
const VERB_BRIEF = { damage: (m) => `피해 ${m}`, drain: (m) => `흡수 ${m}`, guard: (m) => `방어 +${m}`, heal: (m) => `회복 ${m}`, money: (m) => `골드 ${m}`, steal: (m) => `탈취 ${m}`, harvest: (m, t) => `${RES[t] || "자원"} +${m}`, grow: (m, t) => `${RES[t || "food"]} +${m}`, process: () => "가공", buff: () => "강화", debuff: () => "약화", control: () => "행동 불가", draw: () => "더 뽑기", recycle: () => "되돌림", trash: () => "폐기", peek: () => "엿보기", tempo: () => "마나 +1", energy: () => "마나 +", create: () => "생성", amplify: () => "다음 ×2", remove: () => "제거", transform: () => "변환" };
function brief(o) { if (o.scribble) return "낙서"; return (o.payload || []).slice(0, 2).map(([v, m, t]) => (VERB_BRIEF[v] ? VERB_BRIEF[v](m, t) : v)).join(" · "); }
const bcostText = (o) => o.role === "build" && o.bcost ? `비용: ${RES[o.bcost[0]]} ${o.bcost[1]} + 골드 ${o.bcost[2]}` : "";

/* ---------- 흐름 ---------- */
async function newGame() {
  if (busy) return; busy = true; sel = null; pinned = null; prev = null; history = []; startState = null; pv = null;
  const v = await api("new", { stage_type: $("stype").value }); busy = false;
  if (v.error) return alert(v.error);
  st = v; $("over").hidden = true; $("app").hidden = false; resetMap(); render();
}
function render() {
  const setup = st.phase === "setup";
  $("setup").hidden = !setup; $("play").hidden = setup;
  if (setup) renderSetup();
  else { renderHud(); renderMap(); renderHand(); renderSide(); runDiff(); if (st.phase === "play") fetchPreview(); else { pv = null; renderPreview(); } }
  $("over").hidden = st.phase !== "over"; if (st.phase === "over") renderOver();
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
    const card = el("div", { class: "blank" }, el("h3", {}, `${b.tier} 빈 구슬`, el("small", {}, `마나 한계 ${b.cap}${f ? " · 새겨진 말이 붙어 있음" : " · 새겨진 말 없음"}`)), nm, btn);
    if (b.orb) card.append(el("div", { class: "made" + (b.orb.scribble ? " scr" : "") }, sphere(b.orb, orbSize(b.orb)), el("div", {}, el("b", {}, `${b.orb.name} · 마나 ${b.orb.mana}`), b.orb.text)));
    box.append(card);
  });
  $("bagnames").replaceChildren(...st.bag_names.map((n) => el("span", {}, n)));
  const done = st.blanks.filter((b) => b.orb).length;
  $("setup-note").textContent = done < 2 ? `만든 구슬 ${done}/2 · 건너뛰고 시작해도 됩니다` : "준비 완료";
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
    stat("turn", st.stage_name, el("div", { class: "v" }, `${Math.min(st.turn, st.turns)}턴`, el("small", {}, `/ ${st.turns}`)), turns),
    stat("hp", "체력", el("div", { class: "v" }, `${st.hp}`, el("small", {}, st.shield ? `방어 +${st.shield}` : `/ ${st.max_hp}`)), el("div", { class: "meter hp" + (hpPct < 30 ? " low" : "") }, el("i", { style: `width:${hpPct}%` }))),
    stat("mana", "마나", el("div", { class: "v" }, `${st.mana}`, el("small", {}, `/ ${st.max_mana}${spend ? ` (−${spend})` : ""}`)), mana),
    Object.assign(stat("gold", "골드 · 정산까지", el("div", { class: "v" }, `${st.gold}`, el("small", {}, `/ ${st.due}`)), el("div", { class: "meter gold" + (st.gold >= st.due ? " met" : "") }, el("i", { style: `width:${goldPct}%` }))), { className: "stat wide" }),
    stat("res", "자원", el("div", { class: "v res" }, el("span", { "data-stat": "wood" }, "🌲", el("b", {}, ` ${st.res.wood}`)), el("span", { "data-stat": "ore" }, "⛏", el("b", {}, ` ${st.res.ore}`)), el("span", { "data-stat": "food" }, "🌾", el("b", {}, ` ${st.res.food}`)))),
    stat("slots", "배치", el("div", { class: "v" }, `건물 ${st.buildings_n}/${st.caps.b}`, el("small", {}, `소환 ${st.summons_n}/${st.caps.s}`))));
}

/* ---------- 지도 ---------- */
let hexLayer, unitLayer, previewLayer, ghostLayer, floatLayer, units = new Map();
function resetMap() {
  const m = $("map"); m.innerHTML = ""; units = new Map();
  const defs = svg("defs", {}, svg("marker", { id: "arr", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" }, svg("path", { d: "M0,0 L10,5 L0,10 z", fill: "#ef7b7b" })));
  hexLayer = svg("g"); unitLayer = svg("g"); previewLayer = svg("g", { class: "pvlayer" }); ghostLayer = svg("g", { class: "ghost" }); floatLayer = svg("g");
  m.append(defs, hexLayer, unitLayer, previewLayer, ghostLayer, floatLayer);
}
function selCard() { return sel !== null && st ? st.hand.find((h) => h.idx === sel) : null; }
function renderMap() {
  const c = selCard();
  const ok = new Set(c ? c.tiles.map((t) => key(...t)) : []), hint = new Set(c ? c.hint.map((t) => key(...t)) : []);
  const res = new Map(st.tiles.map((t) => [key(t.q, t.r), t]));
  hexLayer.innerHTML = ""; ghostLayer.innerHTML = "";
  for (let q = -R; q <= R; q++) for (let r = Math.max(-R, -q - R); r <= Math.min(R, -q + R); r++) {
    const [x, y] = px(q, r), k = key(q, r), t = res.get(k);
    const cls = "hex" + (t ? " " + t.t : "") + (q === 0 && r === 0 ? " home" : "") + (ok.has(k) ? " ok" : "") + (hint.has(k) ? " hint" : "");
    const p = svg("polygon", { points: hexPts(x, y), class: cls });
    if (ok.has(k)) {
      p.dataset.q = q; p.dataset.r = r;
      p.addEventListener("click", () => playCard(sel, [q, r]));
      p.addEventListener("pointerenter", () => ghost(c, x, y)); p.addEventListener("pointerleave", () => ghostLayer.replaceChildren());
    } else if (t) p.addEventListener("pointerenter", () => inspectTile(t));
    hexLayer.append(p);
    if (t) hexLayer.append(svg("text", { x, y: y - 3, class: "mk" }, GLYPH[t.t]), svg("text", { x, y: y + 14, class: "amt" }, String(t.amt)));
    if (hint.has(k)) hexLayer.append(svg("text", { x: x + 17, y: y - 13, class: "star" }, "✦"));
  }
  syncUnits();
}
function ghost(c, x, y) {
  if (!c) return;
  const g = svg("g", { transform: `translate(${x},${y})` }, svg("rect", { x: -15, y: -15, width: 30, height: 30, rx: 8, class: c.o.role === "build" ? "tok-b" : "tok-s" }), svg("text", { y: 1, class: "glyph" }, c.o.role === "build" ? "🏠" : "🛡️"), svg("text", { y: 28, class: "ulab" }, c.o.name.slice(0, 5)));
  ghostLayer.replaceChildren(g);
}
// 유닛은 id로 이어 붙여 움직임이 부드럽게 보이게 한다.
function tokenFor(kind, d) {
  const g = svg("g", { class: "unit enter" });
  if (kind === "p") g.append(svg("circle", { r: 17, class: "tok-p" }), svg("text", { class: "glyph" }, "🧙"));
  else if (kind === "e") g.append(svg("circle", { r: 15, class: "tok-e" }), svg("text", { class: "glyph", "data-g": "1" }, "👹"), svg("circle", { cx: 12, cy: -12, r: 8, fill: "#3a1418", stroke: "#ef7b7b", "stroke-width": 1.5 }), svg("text", { x: 12, y: -9, class: "badge" }, `${d.lvl}`));
  else if (kind === "s") g.append(svg("circle", { r: 15, class: "tok-s" }), svg("text", { class: "glyph" }, "🛡️"));
  else g.append(svg("rect", { x: -15, y: -15, width: 30, height: 30, rx: 8, class: "tok-b" }), svg("text", { class: "glyph" }, "🏠"));
  if (kind !== "p") {
    g.append(svg("rect", { x: -16, y: -26, width: 32, height: 5, rx: 2.5, class: "hpbg" }), svg("rect", { x: -16, y: -26, width: 32, height: 5, rx: 2.5, class: "hpfg " + (kind === "e" ? "e" : "a"), "data-hp": "1" }));
    if (kind !== "e") g.append(svg("text", { y: 28, class: "ulab" }, d.name.slice(0, 5)));
  }
  return g;
}
function syncUnits() {
  const want = new Map();
  want.set("p", { kind: "p", d: { q: 0, r: 0 } });
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
      u.g.addEventListener("pointerenter", () => inspectUnit(u)); u.g.addEventListener("click", () => { pinned = id; inspectUnit(u); });
      requestAnimationFrame(() => requestAnimationFrame(() => { u.g.style.transition = ""; u.g.classList.remove("enter"); }));
    } else u.g.style.transform = tf;
    u.d = d;
    const hp = u.g.querySelector("[data-hp]"); if (hp) hp.setAttribute("width", String(32 * Math.max(0, d.hp) / d.max));
    const gl = u.g.querySelector("[data-g]"); if (gl) gl.textContent = d.stun ? "💤" : "👹";
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
  if (u.kind === "p") box.replaceChildren(el("b", {}, "나"), el("div", { class: "sub" }, `체력 ${st.hp}/${st.max_hp}${st.shield ? ` · 방어 ${st.shield}` : ""}`), el("p", {}, "건물과 소환물은 내 주변 2칸 안에 놓을 수 있습니다."));
  else if (u.kind === "e") box.replaceChildren(el("b", {}, `적 Lv${d.lvl}`), el("div", { class: "sub" }, hp), el("p", {}, [d.stun ? "행동 불가" : "", d.weak ? "약화" : ""].filter(Boolean).join(" · ") || "가장자리에서 걸어와 길을 막은 건물·소환물을 공격합니다."));
  else box.replaceChildren(el("b", {}, d.name), el("div", { class: "sub" }, `${u.kind === "b" ? "건물" : "소환물"} · ${hp}`));
}
function renderSide() {
  const c = selCard(), box = $("inspect");
  if (pinned && units.get(pinned)) inspectUnit(units.get(pinned));
  else if (c) box.replaceChildren(el("b", {}, c.o.name), el("div", { class: "sub" }, `${ROLE[c.o.role] || c.o.role} · 마나 ${c.o.mana}`), el("p", {}, c.o.text), el("p", { class: "sub" }, c.need_tile ? (c.hint.length ? "초록 칸(✦)에 놓으면 보너스가 붙습니다. " : "노란 칸 중 하나를 고르세요. ") + "Enter(또는 더블클릭): 추천 칸에 바로 놓기 · 칸으로 끌어다 놓아도 됩니다." : ""));
  else box.replaceChildren(el("b", {}, "정보"), el("p", { class: "sub" }, "구슬을 누르면 효과가, 지도 위의 칸·유닛에 올리면 상태가 여기에 보입니다."));
  const fx = $("effects"); fx.hidden = !st.fx.length;
  if (st.fx.length) {
    const grp = new Map();
    st.fx.forEach((f) => { const t = f.name + (f.kind === "delay" ? " (대기)" : f.kind === "trig" ? " (조건부)" : ""); const g = grp.get(t) || { n: 0, cond: f.cond }; g.n++; grp.set(t, g); });
    fx.replaceChildren(el("h3", {}, "작동 중인 효과"), el("div", { class: "chips" }, ...[...grp].map(([t, g]) => el("span", { title: g.cond && g.cond !== "none" ? `발동 조건: ${g.cond}` : "" }, t + (g.n > 1 ? ` ×${g.n}` : "")))));
  }
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
    const card = el("div", { class: `orb r-${o.role}` + (dis ? " dis" : "") + (sel === h.idx ? " sel" : ""), style: `--d:${d}px`, tabindex: "0", role: "listitem", title: `${o.name} (마나 ${o.mana})\n${o.text}`,
      "aria-label": `${o.name}, 마나 ${o.mana}, ${o.text}${h.why ? ", 쓸 수 없음: " + h.why : ""}`, "aria-disabled": String(dis),
      onclick: () => { if (dragMoved) { dragMoved = false; return; } if (dis) return toast(h.why || "지금은 쓸 수 없습니다"); playCard(h.idx); },
      onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); if (dis) toast(h.why || "지금은 쓸 수 없습니다"); else playCard(h.idx); } },
      onpointerenter: () => { if (sel === null && !pinned) peek(h); },
      onpointerdown: (e) => { if (!dis && h.need_tile) startDrag(e, h, card0); },
      ondblclick: () => { if (!dis && h.need_tile) quick(h); } },
      sphere(o, d), el("span", { class: "mbadge", "aria-hidden": "true" }, String(o.mana)));
    card0 = card;
    const cap = el("div", { class: "cap" }, el("span", { class: "role" }, ROLE[o.role] || o.role), brief(o));
    const bc = bcostText(o); if (bc) cap.append(el("span", { class: "cost" }, bc.replace("비용: ", "")));
    card.append(cap);
    if (h.why) card.append(el("div", { class: "why" }, h.why));
    if (n < 9) card.append(el("span", { class: "key", "aria-hidden": "true" }, String(n + 1)));
    hd.append(card);
  });
  if (!st.hand.length) hd.append(el("span", { class: "empty" }, "손패가 없습니다. 턴을 끝내면 새로 뽑습니다."));
  $("endturn").disabled = st.phase !== "play" || busy;
  const usable = st.hand.filter((h) => !h.why).length;
  $("endturn").classList.toggle("ready", st.phase === "play" && !usable);
  $("undo").disabled = busy || !history.length;
  $("piles").innerHTML = `주머니 ${st.bag} · 뽑을 것 ${st.draw} · 버린 것 ${st.disc}<br><b>${usable ? `쓸 수 있는 구슬 ${usable}개 남음` : "더 쓸 구슬이 없어요"}</b>`;
}
function peek(h) { $("inspect").replaceChildren(el("b", {}, h.o.name), el("div", { class: "sub" }, `${ROLE[h.o.role] || h.o.role} · 마나 ${h.o.mana}`), el("p", {}, h.o.text)); }

/* ---------- 행동 ---------- */
async function playCard(idx, tile) {
  if (busy) return; const h = st.hand.find((x) => x.idx === idx); if (!h) return;
  pinned = null;
  if (h.need_tile && !tile) { sel = sel === idx ? null : idx; renderHud(); renderMap(); renderHand(); renderSide(); if (sel !== null) toast(h.hint.length ? "초록 칸(✦)을 추천합니다" : "놓을 칸을 고르세요"); return; }
  busy = true; const v = await api("play", { idx, tile }); busy = false; sel = null;
  if (v.error) return toast(v.error);
  if (v.action && v.action.error) toast(v.action.error);
  if (!(v.action && v.action.error)) pushHistory();
  st = v; render();
}
async function endTurn() {
  if (busy || st.phase !== "play") return; busy = true; sel = null; pinned = null;
  $("endturn").disabled = true; $("endturn").firstChild.textContent = "적 행동 중…";
  const v = await api("end_turn"); busy = false; $("endturn").firstChild.textContent = "턴 종료";
  if (v.error) { toast(v.error); return render(); }
  pushHistory(); st = v; render();
}
function renderOver() {
  const r = st.result, o = $("over");
  const rows = [["모은 골드", `${r.gold} / 필요 ${r.due}`], ["처치한 적", r.kills], ["진행한 턴", r.turns], ["쓰러졌는가", r.died ? "예 (이 스테이지의 골드 몰수)" : "아니오"], ["골드 출처", `처치 ${r.src.g_bounty || 0} · 돈 구슬 ${r.src.g_money || 0} · 가공 ${r.src.g_process || 0}`], ["인접 시너지 발동", r.src.adj_bonus || 0]];
  const t = el("table", {}); rows.forEach(([a, b]) => t.append(el("tr", {}, el("td", {}, a), el("td", {}, String(b)))));
  const again = el("button", { class: "primary big", type: "button", onclick: newGame }, "다시 하기");
  o.replaceChildren(el("div", { class: "result", role: "dialog", "aria-modal": "true", "aria-label": "스테이지 결과" }, el("h2", { class: r.pass ? "pass" : "fail" }, r.pass ? "정산 통과" : "정산 실패"), t, el("div", { class: "acts" }, el("button", { type: "button", onclick: () => { o.hidden = true; } }, "지도 보기"), startState ? el("button", { type: "button", title: "같은 맵·같은 주머니·같은 적 등장으로 다시 시작합니다", onclick: replay }, "같은 판 다시") : null, again)));
  setTimeout(() => again.focus(), 50);
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
function quick(h) { if (!h.tiles.length) return toast("놓을 수 있는 칸이 없습니다"); playCard(h.idx, bestTile(h)); }
function startDrag(e, h, cardEl) {
  if (e.button > 0 || busy) return;
  const x0 = e.clientX, y0 = e.clientY; let dragging = false, chip = null, over = null;
  const tileAt = (x, y) => { const t = document.elementFromPoint(x, y); return t && t.closest && t.closest(".hex.ok"); };
  const move = (ev) => {
    if (!dragging) {
      if (Math.hypot(ev.clientX - x0, ev.clientY - y0) < 8) return;
      dragging = true; dragMoved = true; sel = h.idx; renderHud(); renderMap(); renderSide();
      document.querySelectorAll(".orb.sel").forEach((n) => n.classList.remove("sel")); cardEl.classList.add("sel");
      chip = el("div", { class: "dragchip" }, sphere(h.o, 68)); document.body.append(chip);
    }
    chip.style.transform = `translate(${ev.clientX - 34}px,${ev.clientY - 34}px)`;
    const t = tileAt(ev.clientX, ev.clientY);
    if (t !== over) { if (over) over.classList.remove("drop"); over = t; if (over) over.classList.add("drop"); }
  };
  const end = (ev) => {
    window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", end); window.removeEventListener("pointercancel", end);
    if (!dragging) return;
    if (chip) chip.remove();
    const t = ev.type === "pointerup" ? tileAt(ev.clientX, ev.clientY) : null;
    setTimeout(() => { dragMoved = false; }, 0);
    if (t) playCard(h.idx, [+t.dataset.q, +t.dataset.r]);
    else { sel = null; renderHud(); renderMap(); renderHand(); renderSide(); toast("칸 위에 놓아야 합니다"); }
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
    for (const o of pv.own) rows.push(el("div", { class: "pvrow" }, el("span", {}, `${o.name} (${o.kind === "buildings" ? "건물" : "소환"})`), el("b", { class: "down" }, o.lost ? "파괴됨" : `피해 −${o.dmg}`)));
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

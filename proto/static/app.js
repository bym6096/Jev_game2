const S = 30, SQ3 = Math.sqrt(3);
let st = null, sel = null, busy = false;
const $ = (id) => document.getElementById(id);
const px = (q, r) => [S * SQ3 * (q + r / 2), S * 1.5 * r];
const hexPts = (cx, cy, s = S - 1.5) => Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 180 * (60 * i - 30); return `${(cx + s * Math.cos(a)).toFixed(1)},${(cy + s * Math.sin(a)).toFixed(1)}`; }).join(" ");
const key = (q, r) => q + "," + r;
async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return res.json();
}
function toast(t) { const e = $("toast"); e.textContent = t; e.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => e.classList.remove("show"), 2200); }
function el(tag, attrs = {}, ...kids) { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); } for (const k of kids) e.append(k); return e; }
function svg(tag, attrs = {}, ...kids) { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); for (const k of kids) e.append(k); return e; }

async function newGame() {
  sel = null; const v = await api("/api/new", { stage_type: $("stype").value }); st = v; $("app").hidden = false; render();
}
function render() {
  $("setup").hidden = st.phase !== "setup"; $("play").hidden = st.phase !== "play" && st.phase !== "over"; $("over").hidden = st.phase !== "over";
  if (st.phase === "setup") renderSetup(); else { renderHud(); renderMap(); renderHand(); renderLog(); }
  if (st.phase === "over") renderOver();
}
function renderSetup() {
  const box = $("blanks"); box.innerHTML = "";
  st.blanks.forEach((b, i) => {
    const f = b.frag, input = el("input", { type: "text", maxlength: String(b.max_typed), placeholder: `이름 (${b.max_typed}자까지)`, "aria-label": `빈 구슬 ${i + 1} 이름` });
    if (b.orb) input.disabled = true;
    const btn = el("button", { class: "primary", onclick: async () => {
      if (!input.value.trim()) return toast("이름을 쓰세요");
      btn.disabled = true; btn.textContent = "Jev가 읽는 중…";
      const v = await api("/api/write", { sid: st.sid, idx: i, text: input.value });
      if (v.error) { toast(v.error); btn.disabled = false; btn.textContent = "구슬 만들기"; return; }
      st = v; renderSetup();
    } }, "구슬 만들기");
    if (b.orb) btn.hidden = true;
    const nm = el("div", { class: "namebox" });
    if (f && f.pos === "pre") nm.append(el("span", { class: "frag" }, f.t));
    nm.append(input);
    if (f && f.pos === "suf") nm.append(el("span", { class: "frag" }, (f.sp ? " " : "") + f.t));
    const card = el("div", { class: "blank" }, el("h3", {}, `${b.tier} 빈 구슬 `, el("span", { class: "tier" }, `마나 한계 ${b.cap}${f ? "" : " · 새겨진 말 없음"}`)), nm, el("div", { class: "row" }, btn));
    if (b.orb) card.append(el("div", { class: "made" + (b.orb.scribble ? " scr" : "") }, el("b", {}, `${b.orb.name}  (마나 ${b.orb.mana})`), b.orb.text));
    box.append(card);
  });
  $("bagnames").replaceChildren(...st.bag_names.map((n) => el("span", {}, n)));
  const done = st.blanks.filter((b) => b.orb).length; $("setup-note").textContent = done < 2 ? `만든 구슬 ${done}/2 — 건너뛰고 시작할 수도 있습니다` : "준비 완료";
}
function renderHud() {
  const h = $("hud"); h.innerHTML = "";
  const pct = Math.max(0, st.hp) / st.max_hp * 100;
  const mana = el("span", { class: "mana" }); for (let i = 0; i < Math.max(st.max_mana, st.mana); i++) mana.append(el("i", { class: i < st.mana ? "" : "off" }));
  h.append(
    el("div", { class: "stat" }, `${st.stage_name}`, el("span", { class: "hint", style: "margin:0" }, `턴 ${Math.min(st.turn, st.turns)}/${st.turns}`)),
    el("div", { class: "stat" }, "체력 ", el("span", { class: "bar" }, el("i", { style: `width:${pct}%` })), `${st.hp}`, st.shield ? ` +방어 ${st.shield}` : ""),
    el("div", { class: "stat" }, "마나 ", mana),
    el("div", { class: "stat" }, `골드 ${st.gold}`, el("span", { class: "hint", style: "margin:0" }, `/ 정산 ${st.due}`)),
    el("div", { class: "stat" }, `🌲${st.res.wood}  ⛏${st.res.ore}  🌾${st.res.food}`),
    el("div", { class: "stat" }, `주머니 ${st.bag} (뽑을 것 ${st.draw} · 버린 것 ${st.disc})`),
    el("div", { class: "stat" }, `건물 ${st.buildings_n}/${st.caps.b}  소환 ${st.summons_n}/${st.caps.s}`));
  $("legend").textContent = "노란 칸: 놓을 수 있는 칸 · 초록 칸: 자원 옆/다른 계열 건물 옆(보너스). 구슬을 누른 뒤 칸을 누르세요.";
}
function renderMap() {
  const m = $("map"); m.innerHTML = "";
  const R = 5, selCard = sel !== null ? st.hand.find((h) => h.idx === sel) : null;
  const ok = new Set(selCard ? selCard.tiles.map((t) => key(...t)) : []), hint = new Set(selCard ? selCard.hint.map((t) => key(...t)) : []);
  const res = new Map(st.tiles.map((t) => [key(t.q, t.r), t]));
  for (let q = -R; q <= R; q++) for (let r = Math.max(-R, -q - R); r <= Math.min(R, -q + R); r++) {
    const [x, y] = px(q, r), t = res.get(key(q, r)), k = key(q, r);
    const cls = "hex " + (t ? t.t : "plain") + (ok.has(k) ? " ok" : "") + (hint.has(k) ? " hint" : "");
    const p = svg("polygon", { points: hexPts(x, y), class: cls });
    if (ok.has(k)) p.addEventListener("click", () => playCard(sel, [q, r]));
    m.append(p);
    if (t) m.append(svg("text", { x, y: y - 2, "text-anchor": "middle", "font-size": 20 }, t.t === "tree" ? "🌲" : "⛏"), svg("text", { x, y: y + 15, "text-anchor": "middle", class: "unit-label" }, String(t.amt)));
  }
  const unit = (q, r, icon, label, hp, max, good) => {
    const [x, y] = px(q, r); const g = svg("g", {});
    g.append(svg("text", { x, y: y + 6, "text-anchor": "middle", "font-size": 22 }, icon));
    if (label) g.append(svg("text", { x, y: y + 20, "text-anchor": "middle", class: "unit-label" }, label));
    if (max) { g.append(svg("rect", { x: x - 14, y: y - 22, width: 28, height: 4, fill: "rgba(0,0,0,.25)", rx: 2 }), svg("rect", { x: x - 14, y: y - 22, width: 28 * Math.max(0, hp) / max, height: 4, class: "hpbar" + (good ? " b" : ""), rx: 2 })); }
    const tt = svg("title", {}, `${label || ""} 체력 ${hp}/${max}`); g.append(tt); m.append(g);
  };
  st.buildings.forEach((b) => unit(b.q, b.r, "🏠", b.name.slice(0, 4), b.hp, b.max, true));
  st.summons.forEach((u) => unit(u.q, u.r, "🛡️", u.name.slice(0, 4), u.hp, u.max, true));
  st.enemies.forEach((e) => unit(e.q, e.r, e.stun ? "💤" : "👹", `Lv${e.lvl}`, e.hp, e.max, false));
  const [x0, y0] = px(0, 0); m.append(svg("text", { x: x0, y: y0 + 8, "text-anchor": "middle", "font-size": 26 }, "🧙"));
}
function renderHand() {
  const hd = $("hand"); hd.innerHTML = "";
  st.hand.forEach((h) => {
    const o = h.o, dis = !!h.why || st.phase !== "play";
    const card = el("div", { class: "orb" + (dis ? " dis" : "") + (sel === h.idx ? " sel" : ""), tabindex: "0", role: "button", "aria-label": o.name, onclick: () => !dis && playCard(h.idx), onkeydown: (e) => { if ((e.key === "Enter" || e.key === " ") && !dis) { e.preventDefault(); playCard(h.idx); } } },
      el("div", { class: "nm" }, o.name), el("div", { class: "mn" }, String(o.mana)),
      el("div", { class: "tx" }, el("span", { class: "role" }, { cast: "시전", build: "건물", summon: "소환", move: "이동" }[o.role] || o.role), o.text));
    if (o.role === "build" && o.bcost) card.append(el("div", { class: "why", style: "color:var(--mute)" }, `비용: ${o.bcost[0] === "gold" ? "골드" : { wood: "나무", ore: "광석", food: "식량" }[o.bcost[0]]} ${o.bcost[1]} + 골드 ${o.bcost[2]}`));
    if (h.why) card.append(el("div", { class: "why" }, h.why));
    hd.append(card);
  });
  if (!st.hand.length) hd.append(el("span", { class: "hint" }, "손패가 없습니다"));
  $("endturn").disabled = st.phase !== "play";
}
function renderLog() { $("log").replaceChildren(...st.log.map((t) => el("div", {}, t))); $("log").scrollTop = 1e6; }
async function playCard(idx, tile) {
  if (busy) return; const h = st.hand.find((x) => x.idx === idx); if (!h) return;
  if (h.need_tile && !tile) { sel = sel === idx ? null : idx; renderMap(); renderHand(); if (sel !== null) toast(h.hint.length ? "초록 칸을 추천합니다" : "놓을 칸을 고르세요"); return; }
  busy = true; const v = await api("/api/play", { sid: st.sid, idx, tile }); busy = false; sel = null;
  if (v.action && v.action.error) toast(v.action.error);
  st = v; render();
}
async function endTurn() { if (busy) return; busy = true; sel = null; const v = await api("/api/end_turn", { sid: st.sid }); busy = false; st = v; render(); }
function renderOver() {
  const r = st.result, o = $("over");
  o.innerHTML = ""; o.append(el("h2", { class: r.pass ? "pass" : "fail" }, r.pass ? "정산 통과!" : "정산 실패"));
  const rows = [["모은 골드", `${r.gold} / 필요 ${r.due}`], ["처치한 적", r.kills], ["진행한 턴", r.turns], ["쓰러졌는가", r.died ? "예 (이 스테이지의 골드 몰수)" : "아니오"], ["골드 출처", `처치 ${r.src.g_bounty || 0} · 돈 구슬 ${r.src.g_money || 0} · 가공 ${r.src.g_process || 0}`], ["인접 시너지 발동", r.src.adj_bonus || 0]];
  const t = el("table", {}); rows.forEach(([a, b]) => t.append(el("tr", {}, el("td", {}, a), el("td", {}, String(b))))); o.append(t, el("button", { class: "primary", onclick: newGame }, "다시 하기")); setTimeout(() => o.scrollIntoView({ behavior: "smooth", block: "center" }), 100);
}
$("newgame").addEventListener("click", newGame); $("start").addEventListener("click", async () => { st = await api("/api/start", { sid: st.sid }); render(); }); $("endturn").addEventListener("click", endTurn);
newGame();

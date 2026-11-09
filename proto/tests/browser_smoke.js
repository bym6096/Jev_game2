// 브라우저 연기 시험: 15턴 전체를 자동으로 플레이하고(칸이 필요한 구슬은 추천 칸, 대상이 필요한 구슬은 Enter=가장 가까운 적), 모바일 폭(390px)에서 가로 넘침이 없는지 본다.
// 사용: NODE_PATH=<playwright가 있는 node_modules> node proto/tests/browser_smoke.js [주소=http://localhost:8010] [스크린샷 폴더]
// (이 클라우드 환경에서는 NODE_PATH=/opt/node-tools/node_modules). 서버: python proto/server.py. 오류가 있으면 종료 코드 1.
const { chromium } = require('playwright'); const os = require('os'), fs = require('fs');
const url = process.argv[2] || 'http://localhost:8010/', out = process.argv[3] || fs.mkdtempSync(os.tmpdir() + '/proto-smoke-');
(async () => {
  const b = await chromium.launch(); const errs = [];
  const p = await (await b.newContext({ viewport: { width: 1366, height: 768 } })).newPage();
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.goto(url); await p.waitForSelector('#setup:not([hidden])'); await p.click('#start'); await p.waitForSelector('#play:not([hidden])');
  for (let turn = 0; turn < 20 && !(await p.isVisible('#over')); turn++) {
    for (let k = 0; k < 5; k++) {
      const card = await p.$('.orb:not(.dis)'); if (!card) break;
      await card.click(); await p.waitForTimeout(120);
      const ok = await p.$$('.hex.ok');
      if (ok.length) await ((await p.$('.hex.hint')) || ok[0]).click(); else if (await p.$('g.unit.tgt')) await p.keyboard.press('Enter');
      await p.waitForFunction(() => !busy, null, { timeout: 8000 }); await p.waitForTimeout(80);
    }
    await p.keyboard.press('Space'); await p.waitForFunction(() => !busy, null, { timeout: 8000 }); await p.waitForTimeout(300);
  }
  await p.waitForSelector('#over:not([hidden])', { timeout: 8000 }); await p.screenshot({ path: out + '/over.png' });
  let next = '런 종료(정산 실패)';
  if (await p.$('#over .exitbtn')) {      // 정산 통과 → 출구 고르기 → 2스테이지 준비 → 시작
    await p.click('#over .exitbtn'); await p.waitForSelector('#setup:not([hidden])'); await p.click('#start'); await p.waitForSelector('#play:not([hidden])');
    next = await p.evaluate(() => `${st.stage_n}스테이지 진입(정산 ${st.due}, 적 Lv${st.lvl}, 마나 ${st.max_mana})`);
  } else { await p.click('#over .primary'); await p.waitForSelector('#setup:not([hidden])'); }   // 결과 창의 "새 런 시작" await p.click('#start'); await p.waitForSelector('#play:not([hidden])');
  await p.setViewportSize({ width: 390, height: 844 }); await p.waitForTimeout(400); await p.screenshot({ path: out + '/mobile.png' });
  const overflow = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  console.log('15턴 완주 OK | ' + next + ' | 모바일 가로 넘침:', overflow, '| 콘솔 오류:', JSON.stringify(errs), '| 스크린샷:', out); await b.close();
  process.exit(errs.length || overflow ? 1 : 0);
})();

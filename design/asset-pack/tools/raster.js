const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const jobs = JSON.parse(fs.readFileSync(path.join(__dirname, 'raster_jobs.json')));
(async () => { const b = await chromium.launch();
  for (const j of jobs) { const svg = fs.readFileSync(j.svg, 'utf8'); const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
    const p = await (await b.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: j.scale || 1 })).newPage();
    await p.setContent(`<style>html,body{margin:0}svg{display:block}</style>${svg}`); await p.screenshot({ path: j.out, omitBackground: !!j.transparent }); await p.context().close(); }
  await b.close(); })();

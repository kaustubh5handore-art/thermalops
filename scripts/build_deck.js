const pptxgen = require("pptxgenjs");

const BG = "0E1218";
const SURFACE = "161C25";
const SURFACE2 = "1D2530";
const BORDER = "2A3341";
const TEXT = "EAEEF3";
const DIM = "8C99AB";
const FAINT = "5C6879";
const HEAT = "FF5A36";
const AMBER = "FFB238";
const COOL = "17B9A8";
const COOL2 = "7EE8DC";

const FONT = "Arial";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
const PW = 13.33, PH = 7.5;

function bgSlide(s, opts = {}) {
  s.background = { color: BG };
}

function eyebrow(s, text, x, y, color = COOL2) {
  s.addText(text.toUpperCase(), {
    x, y, w: 8, h: 0.35, fontFace: FONT, fontSize: 11, color, bold: true,
    charSpacing: 2, margin: 0,
  });
}

function pageNum(s, n) {
  s.addText(`${n}`, { x: PW - 0.7, y: PH - 0.5, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 9, color: FAINT, align: "right", margin: 0 });
  s.addText("THERMALOPS", { x: 0.5, y: PH - 0.5, w: 3, h: 0.3, fontFace: FONT, fontSize: 9, color: FAINT, charSpacing: 1, margin: 0 });
}

function card(s, x, y, w, h, opts = {}) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: opts.fill || SURFACE },
    line: { color: opts.line || BORDER, width: 1 },
    shadow: opts.shadow === false ? undefined : { type: "outer", color: "000000", opacity: 0.4, blur: 18, offset: 10, angle: 90 },
  });
}

// ---------------- SLIDE 1: TITLE ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  s.addImage({ path: "assets/glow_teal.png", x: 8.6, y: -1.8, w: 7, h: 7 });
  s.addImage({ path: "assets/glow_heat.png", x: -2.5, y: 4.2, w: 6, h: 6 });

  s.addText("FORTYGUARD HACKATHON '26 · COMMERCIAL SUBMISSION", {
    x: 0.9, y: 0.85, w: 10, h: 0.4, fontFace: FONT, fontSize: 12, color: COOL2, bold: true, charSpacing: 2, margin: 0,
  });
  s.addText([
    { text: "ThermalOps", options: { color: TEXT, bold: true, fontSize: 60 } },
  ], { x: 0.85, y: 1.5, w: 11.5, h: 1.3, fontFace: FONT, margin: 0 });
  s.addText("Enterprise Temperature Intelligence — for the people, freight, and facilities that heat puts at risk.", {
    x: 0.9, y: 2.85, w: 8.6, h: 0.8, fontFace: FONT, fontSize: 18, color: DIM, margin: 0,
  });

  s.addImage({ path: "assets/thermal_bar.png", x: 0.9, y: 3.85, w: 4.2, h: 0.09 });

  s.addText("Powered by the FortyGuard Temperature API", {
    x: 0.9, y: 4.15, w: 6, h: 0.4, fontFace: FONT, fontSize: 13, color: FAINT, italic: true, margin: 0,
  });

  const pillars = [
    ["Workforce Safety", "Outdoor & floor-level crews"],
    ["Logistics & Cold Chain", "Fleet, freight & last-mile"],
    ["Data Centers", "Cooling & facility risk"],
  ];
  let px = 0.9;
  pillars.forEach(([t, d], i) => {
    card(s, px, 5.1, 3.7, 1.55, {});
    s.addText(t, { x: px + 0.25, y: 5.28, w: 3.2, h: 0.4, fontFace: FONT, fontSize: 14, color: TEXT, bold: true, margin: 0 });
    s.addText(d, { x: px + 0.25, y: 5.7, w: 3.2, h: 0.7, fontFace: FONT, fontSize: 11.5, color: DIM, margin: 0 });
    px += 3.95;
  });
}

// ---------------- SLIDE 2: PROBLEM ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "The Problem", 0.9, 0.6);
  s.addText("Heat is already costing three different budgets — and none of them see it coming.", {
    x: 0.9, y: 1.0, w: 11.4, h: 1.1, fontFace: FONT, fontSize: 30, color: TEXT, bold: true, margin: 0,
  });

  const rows = [
    { t: "Workforce", c: HEAT, body: "Outdoor and floor-level crews work through heat stress because supervisors have no real-time, site-specific risk signal — only a generic city forecast, checked manually if at all." },
    { t: "Logistics", c: AMBER, body: "Cold-chain and last-mile freight is routed against static seasonal assumptions, so ambient heat spikes on a specific corridor show up as a spoilage claim after the fact, not a warning before dispatch." },
    { t: "Data Centers", c: COOL, body: "Facilities teams track internal thermal telemetry closely but treat external ambient heat load as background noise — until it becomes the reason cooling capacity is suddenly tight." },
  ];
  let y = 2.4;
  rows.forEach(r => {
    s.addShape("rect", { x: 0.9, y: y + 0.06, w: 0.06, h: 1.15, fill: { color: r.c } });
    s.addText(r.t, { x: 1.2, y: y, w: 2.6, h: 1.25, fontFace: FONT, fontSize: 17, color: TEXT, bold: true, valign: "top", margin: 0 });
    s.addText(r.body, { x: 3.9, y: y, w: 8.5, h: 1.25, fontFace: FONT, fontSize: 13.5, color: DIM, valign: "top", margin: 0 });
    y += 1.5;
  });
  pageNum(s, 2);
}

// ---------------- SLIDE 3: MARKET SIZE ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "Market Analysis", 0.9, 0.6);
  s.addText("A large, converging market: heat-exposed operations need software, not just data.", {
    x: 0.9, y: 1.0, w: 11.4, h: 1.0, fontFace: FONT, fontSize: 26, color: TEXT, bold: true, margin: 0,
  });

  // Three concentric-style boxes representing TAM/SAM/SOM (avoiding literal chart for narrative clarity)
  const tiers = [
    { label: "TAM", title: "Global climate-risk & workplace-safety software", note: "Every heat-exposed enterprise vertical, worldwide", color: BORDER, w: 10.6, x: 0.9 },
    { label: "SAM", title: "Heat-exposed enterprise operations", note: "Workforce safety + logistics + facilities software buyers in hot-climate regions", color: COOL, w: 7.6, x: 2.4 },
    { label: "SOM", title: "Gulf & South Asia industrial + logistics", note: "ThermalOps' Year 1–3 go-to-market focus, riding FortyGuard's existing regional footprint", color: HEAT, w: 4.6, x: 3.9 },
  ];
  let ty = 2.05;
  tiers.forEach((t, i) => {
    s.addShape("roundRect", { x: t.x, y: ty, w: t.w, h: 1.0, rectRadius: 0.08, fill: { color: SURFACE }, line: { color: t.color, width: 1.5 } });
    s.addText(t.label, { x: t.x + 0.3, y: ty + 0.08, w: 1.5, h: 0.35, fontFace: FONT, fontSize: 12, color: t.color, bold: true, charSpacing: 1, margin: 0 });
    s.addText(t.title, { x: t.x + 0.3, y: ty + 0.4, w: t.w - 0.6, h: 0.3, fontFace: FONT, fontSize: 13, color: TEXT, bold: true, margin: 0 });
    s.addText(t.note, { x: t.x + 0.3, y: ty + 0.68, w: t.w - 0.6, h: 0.28, fontFace: FONT, fontSize: 9.5, color: DIM, margin: 0 });
    ty += 1.2;
  });

  s.addText("Why now", { x: 0.9, y: 5.75, w: 3, h: 0.3, fontFace: FONT, fontSize: 12, color: COOL2, bold: true, margin: 0 });
  s.addText("Rising average heat-stress days, tightening workplace heat regulation in hot-climate regions, and FortyGuard's hyperlocal (2m-resolution) API making site-level accuracy newly affordable for mid-market operators, not just enterprises with private weather contracts.", {
    x: 0.9, y: 6.05, w: 11.4, h: 0.55, fontFace: FONT, fontSize: 10.5, color: DIM, margin: 0,
  });
  pageNum(s, 3);
}

// ---------------- SLIDE 4: SOLUTION ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "The Solution", 0.9, 0.6);
  s.addText("ThermalOps: the operations layer on top of FortyGuard's temperature data.", {
    x: 0.9, y: 1.0, w: 11.4, h: 0.9, fontFace: FONT, fontSize: 26, color: TEXT, bold: true, margin: 0,
  });

  const cols = [
    { t: "Score", d: "Convert raw heat index, forecast, and solar/AQI data into a WBGT-style risk score per site, route, or facility." },
    { t: "Alert", d: "Route breaches automatically to supervisors and dispatchers over WhatsApp, SMS, Slack, or a TMS/WMS webhook." },
    { t: "Prove", d: "Log every threshold, alert, and acknowledgement into an audit trail for compliance, insurance, and ESG reporting." },
  ];
  let cx = 0.9;
  cols.forEach((c, i) => {
    card(s, cx, 2.2, 3.75, 3.0, {});
    s.addText(`0${i + 1}`, { x: cx + 0.3, y: 2.45, w: 1.5, h: 0.5, fontFace: FONT, fontSize: 22, color: [COOL2, AMBER, HEAT][i], bold: true, margin: 0 });
    s.addText(c.t, { x: cx + 0.3, y: 3.0, w: 3.2, h: 0.4, fontFace: FONT, fontSize: 18, color: TEXT, bold: true, margin: 0 });
    s.addText(c.d, { x: cx + 0.3, y: 3.45, w: 3.2, h: 1.6, fontFace: FONT, fontSize: 12.5, color: DIM, margin: 0 });
    cx += 4.0;
  });

  s.addText("Built on FortyGuard's NVIDIA-recognized Temperature API — hyperlocal, 2-meter-resolution, forecast up to 12 hours ahead.", {
    x: 0.9, y: 5.55, w: 11, h: 0.5, fontFace: FONT, fontSize: 12.5, color: COOL2, italic: true, margin: 0,
  });
  pageNum(s, 4);
}

// ---------------- SLIDE 5: PRODUCT / DEMO ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "Product Walkthrough", 0.9, 0.5);
  s.addText("Portfolio Overview — one screen across every vertical", {
    x: 0.9, y: 0.9, w: 11.4, h: 0.6, fontFace: FONT, fontSize: 24, color: TEXT, bold: true, margin: 0,
  });

  // mock dashboard frame
  card(s, 0.9, 1.75, 11.5, 5.2, { fill: SURFACE2 });
  s.addShape("roundRect", { x: 1.15, y: 2.0, w: 2.6, h: 4.7, rectRadius: 0.06, fill: { color: SURFACE }, line: { color: BORDER, width: 1 } });
  const navItems = ["Portfolio overview", "Employee safety", "Logistics & fleet", "Data centers", "Risk thresholds", "Alert routing", "Compliance exports"];
  let ny = 2.25;
  navItems.forEach((n, i) => {
    if (i === 0) s.addShape("roundRect", { x: 1.3, y: ny - 0.06, w: 2.3, h: 0.4, rectRadius: 0.05, fill: { color: SURFACE2 }, line: { color: BORDER, width: 0.75 } });
    s.addText(n, { x: 1.45, y: ny, w: 2.1, h: 0.3, fontFace: FONT, fontSize: 10.5, color: i === 0 ? TEXT : DIM, margin: 0 });
    ny += 0.58;
  });

  // KPI row
  const kpis = [["Sites critical", "3", HEAT], ["Active alerts", "7", TEXT], ["Workers protected", "1,240", COOL2], ["Avg heat index", "38.4°C", TEXT]];
  let kx = 4.0;
  const kpiW = 1.35, kpiStep = 1.48;
  kpis.forEach(([l, v, c]) => {
    s.addShape("roundRect", { x: kx, y: 2.0, w: kpiW, h: 0.85, rectRadius: 0.05, fill: { color: SURFACE }, line: { color: BORDER, width: 0.75 } });
    s.addText(l.toUpperCase(), { x: kx + 0.12, y: 2.1, w: kpiW - 0.2, h: 0.25, fontFace: FONT, fontSize: 7.5, color: FAINT, margin: 0 });
    s.addText(v, { x: kx + 0.12, y: 2.35, w: kpiW - 0.2, h: 0.4, fontFace: FONT, fontSize: 14, color: c, bold: true, margin: 0 });
    kx += kpiStep;
  });

  // Alert table
  const tblRows = [
    [{ text: "Site / Route", options: { bold: true, color: FAINT, fontSize: 9 } }, { text: "Vertical", options: { bold: true, color: FAINT, fontSize: 9 } }, { text: "Heat Index", options: { bold: true, color: FAINT, fontSize: 9 } }, { text: "Status", options: { bold: true, color: FAINT, fontSize: 9 } }],
    [{ text: "DXB–WH07 Loading Yard" }, { text: "Workforce" }, { text: "46.8°C" }, { text: "CRITICAL", options: { color: HEAT, bold: true } }],
    [{ text: "Route 14 — Last Mile North" }, { text: "Logistics" }, { text: "41.2°C" }, { text: "WARNING", options: { color: AMBER, bold: true } }],
    [{ text: "DC-02 Cooling Zone B" }, { text: "Data Center" }, { text: "33.5°C" }, { text: "NORMAL", options: { color: COOL2, bold: true } }],
    [{ text: "Construction Site — Sector 9" }, { text: "Workforce" }, { text: "44.1°C" }, { text: "CRITICAL", options: { color: HEAT, bold: true } }],
  ];
  s.addTable(tblRows, {
    x: 4.0, y: 3.05, w: 5.8, h: 2.5,
    fontFace: FONT, fontSize: 10.5, color: DIM,
    border: { type: "solid", color: BORDER, pt: 0.5 },
    fill: { color: SURFACE },
    autoPage: false,
    colW: [2.4, 1.2, 1.1, 1.1],
    valign: "middle",
  });

  // side alert feed
  s.addShape("roundRect", { x: 10.05, y: 2.0, w: 2.2, h: 4.7, rectRadius: 0.06, fill: { color: SURFACE }, line: { color: BORDER, width: 1 } });
  s.addText("LIVE ALERT FEED", { x: 10.2, y: 2.15, w: 2, h: 0.3, fontFace: FONT, fontSize: 8.5, color: FAINT, charSpacing: 1, margin: 0 });
  const feed = [
    ["Heat threshold breached", HEAT, "DXB–WH07 crossed 46°C. Work-pause sent to 18 crew."],
    ["Route risk rising", AMBER, "Route 14 nearing cold-chain tolerance."],
    ["Forecast updated", COOL2, "12h FortyGuard forecast ingested."],
  ];
  let fy = 2.55;
  feed.forEach(([t, c, m]) => {
    s.addShape("roundRect", { x: 10.2, y: fy, w: 1.9, h: 1.15, rectRadius: 0.05, fill: { color: SURFACE2 }, line: { color: BORDER, width: 0.5 } });
    s.addText(t, { x: 10.3, y: fy + 0.08, w: 1.7, h: 0.3, fontFace: FONT, fontSize: 9.5, color: c, bold: true, margin: 0 });
    s.addText(m, { x: 10.3, y: fy + 0.4, w: 1.7, h: 0.65, fontFace: FONT, fontSize: 8.5, color: DIM, margin: 0 });
    fy += 1.3;
  });
  pageNum(s, 5);
}

// ---------------- SLIDE 6: ARCHITECTURE ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "How It's Built", 0.9, 0.6);
  s.addText("A thin, auditable layer on top of the FortyGuard Temperature API", {
    x: 0.9, y: 1.0, w: 11.4, h: 0.7, fontFace: FONT, fontSize: 24, color: TEXT, bold: true, margin: 0,
  });

  const nodes = [
    ["FortyGuard API", "POST /v1/env_params — heat index, AQI, solar irradiance"],
    ["Monitoring Agent", "Polls activity status per site / route / facility"],
    ["Risk Engine", "WBGT-style scoring, configurable per vertical"],
    ["Alert Routing", "WhatsApp, SMS, Slack, TMS/WMS webhooks"],
    ["Compliance Log", "Immutable record for audits & ESG reporting"],
  ];
  let ax = 0.9;
  const aw = 2.15, gap = 0.28;
  nodes.forEach((n, i) => {
    card(s, ax, 3.0, aw, 1.9, {});
    s.addText(n[0], { x: ax + 0.18, y: 3.25, w: aw - 0.36, h: 0.6, fontFace: FONT, fontSize: 12.5, color: TEXT, bold: true, margin: 0 });
    s.addText(n[1], { x: ax + 0.18, y: 3.8, w: aw - 0.36, h: 1.0, fontFace: FONT, fontSize: 9.5, color: DIM, margin: 0 });
    if (i < nodes.length - 1) {
      s.addText("→", { x: ax + aw, y: 3.65, w: gap, h: 0.5, fontFace: FONT, fontSize: 16, color: FAINT, align: "center", margin: 0 });
    }
    ax += aw + gap;
  });

  s.addText("Judging-rubric alignment", { x: 0.9, y: 5.15, w: 4, h: 0.3, fontFace: FONT, fontSize: 12, color: COOL2, bold: true, margin: 0 });
  const rubric = [
    ["Impact & Relevance (40%)", "Three revenue-adjacent verticals, each with a measurable pilot metric"],
    ["Technical Execution (35%)", "Live FortyGuard API integration, polling agent, alert routing"],
    ["Innovation (15%)", "Cross-vertical risk engine, not a single-use-case wrapper"],
    ["Communication (10%)", "Product site, live demo, market deck, and video walkthrough"],
  ];
  let ry = 5.48;
  rubric.forEach(([t, d]) => {
    s.addText(t, { x: 0.9, y: ry, w: 3.6, h: 0.32, fontFace: FONT, fontSize: 10, color: TEXT, bold: true, margin: 0 });
    s.addText(d, { x: 4.6, y: ry, w: 7.7, h: 0.32, fontFace: FONT, fontSize: 10, color: DIM, margin: 0 });
    ry += 0.35;
  });
  pageNum(s, 6);
}

// ---------------- SLIDE 7: BUSINESS MODEL ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "Business Model", 0.9, 0.6);
  s.addText("Per-site subscription, priced like an operations tool — not a data feed.", {
    x: 0.9, y: 1.0, w: 11.4, h: 0.7, fontFace: FONT, fontSize: 24, color: TEXT, bold: true, margin: 0,
  });

  const tiers = [
    { name: "Starter", price: "$149", unit: "/site/mo", who: "Single-vertical pilots, up to 5 sites", feats: ["1 vertical", "Hourly risk scoring", "WhatsApp + SMS alerts"], accent: BORDER },
    { name: "Enterprise", price: "$399", unit: "/site/mo", who: "Multi-vertical portfolios, 5–200 sites", feats: ["All 3 verticals unified", "Sub-hourly + 12h forecast", "TMS/WMS/Slack webhooks", "Audit-grade reporting"], accent: COOL },
    { name: "Platform", price: "Custom", unit: "", who: "200+ sites, government & multi-country", feats: ["Custom regulation packs", "Private deployment", "SLA-backed delivery"], accent: HEAT },
  ];
  let px = 0.9;
  tiers.forEach(t => {
    s.addShape("roundRect", { x: px, y: 2.1, w: 3.75, h: 4.4, rectRadius: 0.08, fill: { color: SURFACE }, line: { color: t.accent, width: t.name === "Enterprise" ? 1.75 : 1 } });
    s.addText(t.name.toUpperCase(), { x: px + 0.3, y: 2.35, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 11, color: DIM, bold: true, charSpacing: 1, margin: 0 });
    s.addText([{ text: t.price, options: { fontSize: 26, bold: true, color: TEXT } }, { text: " " + t.unit, options: { fontSize: 11, color: FAINT } }], { x: px + 0.3, y: 2.65, w: 3.2, h: 0.55, fontFace: FONT, margin: 0 });
    s.addText(t.who, { x: px + 0.3, y: 3.2, w: 3.2, h: 0.55, fontFace: FONT, fontSize: 10.5, color: DIM, margin: 0 });
    let fy = 3.85;
    t.feats.forEach(f => {
      s.addText(`•  ${f}`, { x: px + 0.3, y: fy, w: 3.2, h: 0.3, fontFace: FONT, fontSize: 10.5, color: TEXT, margin: 0 });
      fy += 0.38;
    });
    px += 3.95;
  });
  pageNum(s, 7);
}

// ---------------- SLIDE 8: PILOT RESULTS ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "Modeled Pilot Impact", 0.9, 0.6);
  s.addText("What each vertical moves, measured the way that vertical already measures itself.", {
    x: 0.9, y: 1.0, w: 11.4, h: 0.9, fontFace: FONT, fontSize: 24, color: TEXT, bold: true, margin: 0,
  });

  const metrics = [
    { n: "−31%", l: "Modeled heat-incident rate", sub: "Workforce safety pilot cohort, work-pause automation vs. manual checks", c: COOL2 },
    { n: "4.2×", l: "Faster spoilage-risk detection", sub: "Route-level scoring vs. static seasonal thresholds", c: AMBER },
    { n: "18–72h", l: "Earlier cooling-stress warning", sub: "External heat-load forecast layered onto internal DC telemetry", c: HEAT },
  ];
  let mx = 0.9;
  metrics.forEach(m => {
    card(s, mx, 2.3, 3.75, 2.6, {});
    s.addText(m.n, { x: mx + 0.3, y: 2.55, w: 3.2, h: 0.9, fontFace: FONT, fontSize: 38, color: m.c, bold: true, margin: 0 });
    s.addText(m.l, { x: mx + 0.3, y: 3.5, w: 3.2, h: 0.4, fontFace: FONT, fontSize: 13, color: TEXT, bold: true, margin: 0 });
    s.addText(m.sub, { x: mx + 0.3, y: 3.9, w: 3.2, h: 0.9, fontFace: FONT, fontSize: 10, color: DIM, margin: 0 });
    mx += 4.0;
  });

  s.addText("Note: figures are modeled from FortyGuard trial-cohort data and public occupational-heat research; validated pilot numbers will replace these as live customer deployments complete.", {
    x: 0.9, y: 5.3, w: 11.4, h: 0.6, fontFace: FONT, fontSize: 10, italic: true, color: FAINT, margin: 0,
  });
  pageNum(s, 8);
}

// ---------------- SLIDE 9: ROADMAP / ASK ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  eyebrow(s, "Roadmap & Ask", 0.9, 0.6);
  s.addText("From hackathon build to Gulf-region pilot in three steps.", {
    x: 0.9, y: 1.0, w: 11.4, h: 0.7, fontFace: FONT, fontSize: 26, color: TEXT, bold: true, margin: 0,
  });

  const steps = [
    ["Now", "Working prototype on FortyGuard's live API — portfolio dashboard, WhatsApp alert routing, 3 verticals modeled."],
    ["Next 90 days", "First paid pilot with one logistics or industrial operator per vertical; replace modeled metrics with real ones."],
    ["6–12 months", "Regional threshold packs (regulatory work-rest rules), TMS/WMS integrations, and FortyGuard co-sell motion."],
  ];
  let sy = 2.3;
  steps.forEach(([t, d], i) => {
    s.addShape("roundRect", { x: 0.9, y: sy, w: 1.7, h: 0.5, rectRadius: 0.25, fill: { color: [COOL, AMBER, HEAT][i] } });
    s.addText(t, { x: 0.9, y: sy, w: 1.7, h: 0.5, fontFace: FONT, fontSize: 11, color: BG, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(d, { x: 2.85, y: sy - 0.05, w: 9.5, h: 0.6, fontFace: FONT, fontSize: 12.5, color: DIM, valign: "middle", margin: 0 });
    sy += 0.95;
  });

  s.addText("What we're asking FortyGuard for", { x: 0.9, y: 5.5, w: 6, h: 0.35, fontFace: FONT, fontSize: 13, color: COOL2, bold: true, margin: 0 });
  s.addText("Extended trial credits across the pilot period, an intro to one logistics or industrial FortyGuard customer for a design partnership, and feedback from the FortyGuard team on regional threshold accuracy.", {
    x: 0.9, y: 5.9, w: 11.2, h: 0.7, fontFace: FONT, fontSize: 12, color: DIM, margin: 0,
  });
  pageNum(s, 9);
}

// ---------------- SLIDE 10: CLOSE ----------------
{
  const s = pres.addSlide(); bgSlide(s);
  s.addImage({ path: "assets/glow_teal.png", x: -2, y: -2, w: 7, h: 7 });
  s.addImage({ path: "assets/glow_heat.png", x: 9, y: 3, w: 6, h: 6 });
  s.addText("Heat is a business risk.", { x: 0.9, y: 2.6, w: 11.4, h: 0.9, fontFace: FONT, fontSize: 36, color: TEXT, bold: true, margin: 0 });
  s.addText("ThermalOps manages it like one.", { x: 0.9, y: 3.35, w: 11.4, h: 0.9, fontFace: FONT, fontSize: 36, color: COOL2, bold: true, margin: 0 });
  s.addImage({ path: "assets/thermal_bar.png", x: 0.9, y: 4.4, w: 4.2, h: 0.09 });
  s.addText("Built on the FortyGuard Temperature API  ·  FortyGuard Hackathon '26", {
    x: 0.9, y: 4.65, w: 9, h: 0.4, fontFace: FONT, fontSize: 13, color: FAINT, italic: true, margin: 0,
  });
  s.addText("github.com/<team>/thermalops   ·   linkedin.com/in/<you>", {
    x: 0.9, y: 6.6, w: 9, h: 0.35, fontFace: FONT, fontSize: 12, color: DIM, margin: 0,
  });
}

pres.writeFile({ fileName: "../docs/ThermalOps_MarketAnalysis_Deck.pptx" }).then(() => {
  console.log("done");
});

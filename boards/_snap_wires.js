#!/usr/bin/env node
'use strict';
/**
 * Snap schematic LINE endpoints onto nearby pin hotspots (ortho-preserving).
 */
const fs = require('fs');
const path = require('path');
const E = require(path.join(process.env.USERPROFILE, '.cursor', 'skills', 'easyeda-eprj3', 'scripts', 'lib', 'eprj3'));

const file = process.argv[2];
const maxGap = Number(process.argv[3] || 12);
if (!file) {
  console.error('usage: node _snap_wires.js <P1.esch2> [maxGap]');
  process.exit(1);
}

function rotPt(x, y, deg) {
  const r = (deg * Math.PI) / 180;
  return { x: x * Math.cos(r) - y * Math.sin(r), y: x * Math.sin(r) + y * Math.cos(r) };
}
function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

const raw = fs.readFileSync(file, 'utf8');
const recs = raw.split(/\r?\n/).filter((l) => l.trim()).map((l) => ({ line: l, rec: E.parseRecord(l) }));

const docs = [];
let cur = null;
for (const item of recs) {
  if (!item.rec) continue;
  if (item.rec.type === 'DOCHEAD') {
    cur = { uuid: item.rec.body.uuid, docType: item.rec.body.docType, recs: [] };
    docs.push(cur);
  } else if (cur) cur.recs.push(item.rec);
}

const symbols = new Map();
for (const d of docs) {
  if (d.docType !== 'SYMBOL') continue;
  const pins = d.recs.filter((r) => r.type === 'PIN').map((r) => ({
    x: r.body.x != null ? r.body.x : r.body.dotX,
    y: r.body.y != null ? r.body.y : r.body.dotY
  }));
  symbols.set(d.uuid, pins);
}

const page = docs[docs.length - 1];
const attrs = new Map();
for (const r of page.recs) {
  if (r.type === 'ATTR' && r.body.parentId) {
    if (!attrs.has(r.body.parentId)) attrs.set(r.body.parentId, []);
    attrs.get(r.body.parentId).push(r.body);
  }
}

const pins = [];
for (const r of page.recs) {
  if (r.type !== 'COMPONENT') continue;
  const a = attrs.get(r.id) || [];
  const symId = (a.find((x) => x.key === 'Symbol') || {}).value;
  const pinsLocal = symbols.get(symId) || [];
  for (const p of pinsLocal) {
    const lp = rotPt(p.x, p.y, r.body.rotation || 0);
    pins.push({
      x: Math.round((r.body.x + lp.x) * 100) / 100,
      y: Math.round((r.body.y + lp.y) * 100) / 100
    });
  }
}

function nearestPin(pt) {
  let best = { d: Infinity, pin: null };
  for (const p of pins) {
    const d = dist(pt, p);
    if (d < best.d) best = { d, pin: p };
  }
  return best;
}

function snapPoint(x, y) {
  const n = nearestPin({ x, y });
  if (!n.pin || n.d < 0.05 || n.d > maxGap) return { x, y, moved: false, d: n.d };
  const dx = Math.abs(n.pin.x - x);
  const dy = Math.abs(n.pin.y - y);
  // Prefer axis-aligned snap so wires stay orthogonal.
  if (dy < 0.51) return { x: n.pin.x, y, moved: n.pin.x !== x, d: n.d };
  if (dx < 0.51) return { x, y: n.pin.y, moved: n.pin.y !== y, d: n.d };
  return { x: n.pin.x, y: n.pin.y, moved: true, d: n.d };
}

let moved = 0;
const out = recs.map((item) => {
  const r = item.rec;
  if (!r || r.type !== 'LINE' || r.body.lineGroup == null) return item.line;
  const s = snapPoint(r.body.startX, r.body.startY);
  const e = snapPoint(r.body.endX, r.body.endY);
  if (!s.moved && !e.moved) return item.line;
  r.body.startX = s.x;
  r.body.startY = s.y;
  r.body.endX = e.x;
  r.body.endY = e.y;
  moved++;
  return E.formatRecord({ type: r.type, ticket: r.ticket, id: r.id }, r.body);
});

fs.writeFileSync(file, out.join('\n') + '\n');
console.log(`snapped ${moved} LINE(s) in ${file}`);

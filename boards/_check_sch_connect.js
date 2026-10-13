#!/usr/bin/env node
'use strict';
/**
 * Report schematic pins that do not coincide with a wire endpoint.
 */
const path = require('path');
const E = require(path.join(
  process.env.USERPROFILE,
  '.cursor', 'skills', 'easyeda-eprj3', 'scripts', 'lib', 'eprj3'
));

const file = process.argv[2];
const tol = Number(process.argv[3] || 1.5);
if (!file) {
  console.error('usage: node _check_sch_connect.js <P1.esch2> [tol]');
  process.exit(1);
}

function rotPt(x, y, deg) {
  const r = (deg * Math.PI) / 180;
  return { x: x * Math.cos(r) - y * Math.sin(r), y: x * Math.sin(r) + y * Math.cos(r) };
}

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

const lines = E.readLines(file);
const docs = [];
let cur = null;
for (const l of lines) {
  const r = E.parseRecord(l);
  if (!r) continue;
  if (r.type === 'DOCHEAD') {
    cur = { uuid: r.body.uuid, docType: r.body.docType, recs: [] };
    docs.push(cur);
  } else if (cur) {
    cur.recs.push(r);
  }
}

const symbols = new Map();
for (const d of docs) {
  if (d.docType !== 'SYMBOL') continue;
  const meta = d.recs.find((r) => r.type === 'META');
  const pins = d.recs.filter((r) => r.type === 'PIN').map((r) => {
    const b = r.body;
    const numAttr = d.recs.find((a) => a.type === 'ATTR' && a.body.parentId === r.id && a.body.key === 'Pin Number');
    const nameAttr = d.recs.find((a) => a.type === 'ATTR' && a.body.parentId === r.id && a.body.key === 'Pin Name');
    return {
      id: r.id,
      x: b.x != null ? b.x : b.dotX,
      y: b.y != null ? b.y : b.dotY,
      rot: b.rotation || 0,
      length: b.length || 10,
      num: numAttr && numAttr.body.value,
      name: nameAttr && nameAttr.body.value
    };
  });
  symbols.set(d.uuid, { title: meta && meta.body.title, pins });
}

const page = docs[docs.length - 1];
const comps = [];
const attrByParent = new Map();
for (const r of page.recs) {
  if (r.type === 'ATTR' && r.body.parentId) {
    if (!attrByParent.has(r.body.parentId)) attrByParent.set(r.body.parentId, []);
    attrByParent.get(r.body.parentId).push(r.body);
  }
}
for (const r of page.recs) {
  if (r.type !== 'COMPONENT') continue;
  const attrs = attrByParent.get(r.id) || [];
  const get = (k) => {
    const a = attrs.find((x) => x.key === k);
    return a && a.value;
  };
  const dn = r.body.attrs && r.body.attrs.DeviceName;
  let dname = '';
  try { dname = dn ? JSON.parse(dn).name : ''; } catch {}
  comps.push({
    id: r.id,
    x: r.body.x,
    y: r.body.y,
    rot: r.body.rotation || 0,
    ref: get('Designator') || get('Name') || dname || r.id.slice(0, 8),
    symbol: get('Symbol'),
    name: get('Name') || dname
  });
}

const pins = [];
for (const c of comps) {
  const sym = symbols.get(c.symbol);
  if (!sym) continue;
  for (const p of sym.pins) {
    const lp = rotPt(p.x, p.y, c.rot);
    pins.push({
      ref: c.ref,
      pin: p.num || p.name,
      name: p.name,
      x: Math.round((c.x + lp.x) * 100) / 100,
      y: Math.round((c.y + lp.y) * 100) / 100,
      cx: c.x,
      cy: c.y
    });
  }
}

const ends = [];
for (const r of page.recs) {
  if (r.type !== 'LINE' || r.body.lineGroup == null) continue;
  ends.push({ x: r.body.startX, y: r.body.startY, wire: r.body.lineGroup, id: r.id });
  ends.push({ x: r.body.endX, y: r.body.endY, wire: r.body.lineGroup, id: r.id });
}

function nearestEnd(pt) {
  let best = Infinity;
  let hit = null;
  for (const e of ends) {
    const d = dist(pt, e);
    if (d < best) { best = d; hit = e; }
  }
  return { d: best, hit };
}

const danglingPins = [];
for (const p of pins) {
  const n = nearestEnd(p);
  if (n.d > tol) danglingPins.push({ ...p, gap: Math.round(n.d * 100) / 100, near: n.hit });
}

const danglingEnds = [];
for (const e of ends) {
  let best = Infinity;
  for (const p of pins) best = Math.min(best, dist(e, p));
  // also consider other wire ends as junctions
  for (const o of ends) {
    if (o === e) continue;
    const d = dist(e, o);
    if (d < 1e-6) { best = 0; break; }
    best = Math.min(best, d);
  }
  if (best > tol) danglingEnds.push({ ...e, gap: Math.round(best * 100) / 100 });
}

console.log(`file ${file}`);
console.log(`components ${comps.length}  pins ${pins.length}  wire-ends ${ends.length}  tol ${tol}`);
console.log(`\nPINS not hit by a wire (gap > ${tol}): ${danglingPins.length}`);
for (const p of danglingPins.sort((a, b) => b.gap - a.gap)) {
  console.log(`  ${p.ref}.${p.pin}(${p.name}) @ ${p.x},${p.y}  gap=${p.gap}  nearest ${p.near.x},${p.near.y}`);
}

const lonely = danglingEnds.filter((e) => {
  // only report ends that are not on another wire junction and not near a pin
  return e.gap > tol;
});
console.log(`\nWIRE ENDS not on a pin/junction (gap > ${tol}): ${lonely.length}`);
for (const e of lonely.slice(0, 40)) {
  console.log(`  ${e.x},${e.y}  gap=${e.gap}  line ${e.id}`);
}
if (lonely.length > 40) console.log(`  ... ${lonely.length - 40} more`);

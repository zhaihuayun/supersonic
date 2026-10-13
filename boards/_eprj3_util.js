'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SKILL = process.env.EASYEDA_EPRJ3_SKILL
  || path.join(process.env.USERPROFILE, '.cursor', 'skills', 'easyeda-eprj3');

function run(script, args) {
  const file = path.join(SKILL, 'scripts', script);
  const r = spawnSync(process.execPath, [file, ...args], { encoding: 'utf8' });
  if (r.status !== 0) {
    console.error(r.stdout || '');
    console.error(r.stderr || '');
    throw new Error(`${script} ${args.join(' ')} failed (${r.status})`);
  }
  const out = (r.stdout || '').trim();
  if (out) console.log(out);
  return out;
}

function tipLocal(px, py, length, prot) {
  const rad = (prot * Math.PI) / 180;
  return { x: px - length * Math.cos(rad), y: py - length * Math.sin(rad) };
}
function rotPt(x, y, deg) {
  const r = (deg * Math.PI) / 180;
  return { x: x * Math.cos(r) - y * Math.sin(r), y: x * Math.sin(r) + y * Math.cos(r) };
}
function pinTip(ox, oy, crot, px, py) {
  // PIN (px,py) is the hotspot — wires must land here, not at the outer stub.
  const p = rotPt(px, py, crot);
  return { x: Math.round((ox + p.x) * 100) / 100, y: Math.round((oy + p.y) * 100) / 100 };
}
function padAt(ox, oy, ang, px, py) {
  const p = rotPt(px, py, ang);
  return { x: Math.round((ox + p.x) * 10) / 10, y: Math.round((oy + p.y) * 10) / 10 };
}
function segs(...pts) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    out.push(`${pts[i].x},${pts[i].y},${pts[i + 1].x},${pts[i + 1].y}`);
  }
  return out.join(';');
}

/** EasyEDA drawing-frame sizes (schematic units). A4 is the init.js default. */
const SHEET_SIZES = {
  A4: { width: 1170, height: 825, xReg: 6, yReg: 4 },
  A3: { width: 1654, height: 1169, xReg: 8, yReg: 6 },
  A2: { width: 2340, height: 1654, xReg: 8, yReg: 6 }
};

/**
 * Patch the placed drawing-frame Width/Height/Size after init.js.
 * EasyEDA Pro regenerates the visible border from these attributes.
 */
function setSheetSize(dir, sch, sheet, sizeName) {
  const spec = SHEET_SIZES[sizeName];
  if (!spec) throw new Error(`unknown sheet size ${sizeName}`);
  const file = path.join(dir, 'sch', sch, `${sheet}.esch2`);
  let s = fs.readFileSync(file, 'utf8');
  const before = s;
  s = s.replace(/"value":"A4","keyVisible":null,"valueVisible":null,"key":"Page Size"/g,
    `"value":"${sizeName}","keyVisible":null,"valueVisible":null,"key":"Page Size"`);
  s = s.replace(/"value":"A4","keyVisible":null,"valueVisible":null,"key":"Size"/g,
    `"value":"${sizeName}","keyVisible":null,"valueVisible":null,"key":"Size"`);
  s = s.replace(/"value":"1170","keyVisible":null,"valueVisible":null,"key":"Width"/g,
    `"value":"${spec.width}","keyVisible":null,"valueVisible":null,"key":"Width"`);
  s = s.replace(/"value":"825","keyVisible":null,"valueVisible":null,"key":"Height"/g,
    `"value":"${spec.height}","keyVisible":null,"valueVisible":null,"key":"Height"`);
  s = s.replace(/"value":"6","keyVisible":null,"valueVisible":null,"key":"X Region Count"/g,
    `"value":"${spec.xReg}","keyVisible":null,"valueVisible":null,"key":"X Region Count"`);
  s = s.replace(/"value":"4","keyVisible":null,"valueVisible":null,"key":"Y Region Count"/g,
    `"value":"${spec.yReg}","keyVisible":null,"valueVisible":null,"key":"Y Region Count"`);
  s = s.replace(/"Page Size":"A4"/g, `"Page Size":"${sizeName}"`);
  s = s.replace(/"Size":"A4"/g, `"Size":"${sizeName}"`);
  s = s.replace(/"Width":"1170"/g, `"Width":"${spec.width}"`);
  s = s.replace(/"Height":"825"/g, `"Height":"${spec.height}"`);
  s = s.replace(/"X Region Count":"6"/g, `"X Region Count":"${spec.xReg}"`);
  s = s.replace(/"Y Region Count":"4"/g, `"Y Region Count":"${spec.yReg}"`);
  if (before.includes(`"Size":"${sizeName}"`) && before.includes(`"Width":"${spec.width}"`)) {
    console.log(`sheet ${sheet} already ${sizeName} ${spec.width}x${spec.height}`);
    return;
  }
  if (s === before) throw new Error(`setSheetSize: no A4 frame attrs found in ${file}`);
  fs.writeFileSync(file, s);
  console.log(`sheet ${sheet} size ${sizeName} ${spec.width}x${spec.height}`);
}

/**
 * Wipe and recreate a PCB document in-place (same uuid/title in the index).
 * Does not touch schematic sheets.
 */
function resetPcb(dir, pcbName, outline) {
  const E = require(path.join(SKILL, 'scripts/lib/eprj3'));
  const project = E.Project.load(dir);
  const pcb = project.requirePcb(pcbName);
  const file = project.pcbFile(pcb);
  if (fs.existsSync(file)) fs.unlinkSync(file);
  project.ensurePcbDocument(pcbName, { outline });
  console.log(`reset PCB ${pcbName} -> ${file}`);
  return file;
}

module.exports = {
  SKILL, run, pinTip, padAt, segs, setSheetSize, SHEET_SIZES, resetPcb
};

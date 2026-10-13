#!/usr/bin/env node
'use strict';
/**
 * Rebuild TX PCB from the current schematic. Does NOT touch P1.esch2.
 * Placement Unique IDs follow schematic gge1..gge13:
 *   J1 J2 U1 Rg Q1 Rgs D1 T1 L1 Cmatch J3 C1 C2
 */
const path = require('path');
const E = require(path.join(
  process.env.EASYEDA_EPRJ3_SKILL
    || path.join(process.env.USERPROFILE, '.cursor', 'skills', 'easyeda-eprj3'),
  'scripts/lib/eprj3'
));
const { run, padAt, resetPcb } = require('./_eprj3_util');

const DIR = path.resolve(__dirname, 'AIsonic_TX_Driver_V1');
const PCB = 'PCB1';

run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'TC4427', '--designator', 'U',
  '--description', 'TC4427 dual MOSFET driver SOIC-8',
  '--pins', '1:NC:-20:15:0;2:INA:-20:5:0;3:GND:-20:-5:0;4:INB:-20:-15:0;5:OUTB:20:-15:180;6:VDD:20:-5:180;7:OUTA:20:5:180;8:NC:20:15:180',
  '--pitch', '10']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'NMOSET', '--designator', 'Q',
  '--description', 'N-MOSFET G/D/S',
  '--pins', '1:G:-20:0:0;2:D:20:10:180;3:S:20:-10:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'XFMR4', '--designator', 'T',
  '--description', 'EE19 1:8 pulse transformer',
  '--pins', '1:PRI+:-20:10:0;2:PRI-:-20:-10:0;3:SEC+:20:10:180;4:SEC-:20:-10:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'CONN2R', '--designator', 'J',
  '--description', '2-pin connector pins on right',
  '--pins', '1:1:20:10:180;2:2:20:-10:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'CONN2L', '--designator', 'J',
  '--description', '2-pin connector pins on left',
  '--pins', '1:1:-20:20:0;2:2:-20:-20:0']);

run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'SOIC8', '--designator', 'U',
  '--pads', '1:-110:75:70:22;2:-110:25:70:22;3:-110:-25:70:22;4:-110:-75:70:22;5:110:-75:70:22;6:110:-25:70:22;7:110:25:70:22;8:110:75:70:22',
  '--outline', 'R,0,0,196,157',
  '--silk', 'rect,-98,-90,98,90;path,-98,70,-120,70']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'TO220', '--designator', 'Q',
  '--pads', '1:-100:0:80:80:40;2:0:0:80:80:40;3:100:0:80:80:40',
  '--outline', 'R,0,180,400,360',
  '--silk', 'rect,-160,-50,160,360']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'EE19', '--designator', 'T',
  '--pads', '1:-200:100:80:80:40;2:-200:-100:80:80:40;3:200:100:80:80:40;4:200:-100:80:80:40',
  '--outline', 'R,0,0,750,550',
  '--silk', 'rect,-280,-220,280,220']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'R0805', '--designator', 'R',
  '--pads', '1:-45:0:48:60;2:45:0:48:60',
  '--outline', 'R,0,0,80,50',
  '--silk', 'rect,-50,-32,50,32']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'C0805', '--designator', 'C',
  '--pads', '1:-45:0:48:60;2:45:0:48:60',
  '--outline', 'R,0,0,80,50',
  '--silk', 'rect,-50,-32,50,32']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'L1010', '--designator', 'L',
  '--pads', '1:-180:0:90:140;2:180:0:90:140',
  '--outline', 'R,0,0,400,400',
  '--silk', 'rect,-200,-200,200,200']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'C_HV', '--designator', 'C',
  '--pads', '1:-100:0:70:70:32;2:100:0:70:70:32',
  '--outline', 'R,0,0,280,120',
  '--silk', 'rect,-140,-70,140,70']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'KF381', '--designator', 'J',
  '--pads', '1:0:0:90:90:51;2:150:0:90:90:51',
  '--outline', 'R,75,80,320,240',
  '--silk', 'rect,-40,-40,190,200']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'KF508', '--designator', 'J',
  '--pads', '1:0:0:100:100:51;2:200:0:100:100:51',
  '--outline', 'R,100,90,400,260',
  '--silk', 'rect,-50,-50,250,230']);

resetPcb(DIR, PCB, E.rectPath(0, 0, 4000, 2800));

function addFp(symbol, fp, x, y, refdes, name, nets, angle) {
  const args = ['--dir', DIR, '--pcb', PCB, '--symbol', symbol, '--footprint', fp,
    '--x', String(x), '--y', String(y), '--refdes', refdes, '--name', name, '--nets', nets];
  if (angle) args.push('--angle', String(angle));
  run('add-footprint.js', args);
}

const P = {
  J1: { x: 250, y: 2400 },
  J2: { x: 250, y: 400 },
  U1: { x: 1100, y: 1850 },
  C1: { x: 850, y: 1400 },
  C2: { x: 1100, y: 1400 },
  Rg: { x: 1550, y: 1880 },
  Rgs: { x: 1800, y: 1500 },
  Q1: { x: 2050, y: 1850 },
  D1: { x: 2050, y: 1350 },
  T1: { x: 2850, y: 1850 },
  L1: { x: 3550, y: 2200 },
  Cm: { x: 3550, y: 1500 },
  J3: { x: 3550, y: 450 }
};

// Unique ID order MUST match schematic: gge1..gge13
addFp('CONN2R', 'KF381', P.J1.x, P.J1.y, 'J1', 'KF2EDG-3.81', '1:PWM,2:GND');
addFp('CONN2R', 'KF508', P.J2.x, P.J2.y, 'J2', 'KF2EDG-5.08', '1:+12V,2:GND');
addFp('TC4427', 'SOIC8', P.U1.x, P.U1.y, 'U1', 'TC4427AEOA713', '2:PWM,3:GND,4:GND,6:+12V,7:GATE_DRV');
addFp('RES', 'R0805', P.Rg.x, P.Rg.y, 'Rg', '10R', '1:GATE_DRV,2:GATE');
addFp('NMOSET', 'TO220', P.Q1.x, P.Q1.y, 'Q1', 'IRL540NPBF', '1:GATE,2:DRAIN,3:GND');
addFp('RES', 'R0805', P.Rgs.x, P.Rgs.y, 'Rgs', '10k', '1:GND,2:GATE', 90);
addFp('DIODE', 'SMA', P.D1.x, P.D1.y, 'D1', 'SMBJ100A', '1:DRAIN,2:GND');
addFp('XFMR4', 'EE19', P.T1.x, P.T1.y, 'T1', 'EE19 1:8', '1:+12V,2:DRAIN,3:SEC+,4:TX-');
addFp('IND', 'L1010', P.L1.x, P.L1.y, 'L1', '330uH', '1:SEC+,2:LC_MID');
addFp('CAP', 'C_HV', P.Cm.x, P.Cm.y, 'Cmatch', '2nF 1kV', '1:LC_MID,2:TX+');
addFp('CONN2L', 'KF508', P.J3.x, P.J3.y, 'J3', 'KF2EDG-5.08', '1:TX+,2:TX-');
addFp('CAP', 'C0805', P.C1.x, P.C1.y, 'C1', '100nF', '1:GND,2:+12V', 90);
addFp('CAP', 'C0805', P.C2.x, P.C2.y, 'C2', '10uF 25V', '1:GND,2:+12V', 90);

function trk(net, x1, y1, x2, y2, width) {
  run('add-track.js', ['--dir', DIR, '--pcb', PCB, '--net', net,
    '--x1', String(x1), '--y1', String(y1), '--x2', String(x2), '--y2', String(y2),
    '--width', String(width || 12)]);
}
function via(net, x, y) {
  run('add-via.js', ['--dir', DIR, '--pcb', PCB, '--net', net, '--x', String(x), '--y', String(y)]);
}

const uINA = padAt(P.U1.x, P.U1.y, 0, -110, 25);
const uOUTA = padAt(P.U1.x, P.U1.y, 0, 110, 25);
const uGND = padAt(P.U1.x, P.U1.y, 0, -110, -25);
const uINB = padAt(P.U1.x, P.U1.y, 0, -110, -75);
const uVDD = padAt(P.U1.x, P.U1.y, 0, 110, -25);
const j1p = padAt(P.J1.x, P.J1.y, 0, 0, 0);
const j1g = padAt(P.J1.x, P.J1.y, 0, 150, 0);
const j2p = padAt(P.J2.x, P.J2.y, 0, 0, 0);
const rg1 = padAt(P.Rg.x, P.Rg.y, 0, -45, 0);
const rg2 = padAt(P.Rg.x, P.Rg.y, 0, 45, 0);
const qG = padAt(P.Q1.x, P.Q1.y, 0, -100, 0);
const qD = padAt(P.Q1.x, P.Q1.y, 0, 0, 0);
const rgsG2 = padAt(P.Rgs.x, P.Rgs.y, 90, 45, 0);
const dK = padAt(P.D1.x, P.D1.y, 0, -86.615, 0);
const tPriP = padAt(P.T1.x, P.T1.y, 0, -200, 100);
const tPriN = padAt(P.T1.x, P.T1.y, 0, -200, -100);
const tSecP = padAt(P.T1.x, P.T1.y, 0, 200, 100);
const tSecN = padAt(P.T1.x, P.T1.y, 0, 200, -100);
const lA = padAt(P.L1.x, P.L1.y, 0, -180, 0);
const lB = padAt(P.L1.x, P.L1.y, 0, 180, 0);
const cA = padAt(P.Cm.x, P.Cm.y, 0, -100, 0);
const cB = padAt(P.Cm.x, P.Cm.y, 0, 100, 0);
const j3p = padAt(P.J3.x, P.J3.y, 0, 0, 0);
const j3n = padAt(P.J3.x, P.J3.y, 0, 200, 0);
const c1b = padAt(P.C1.x, P.C1.y, 90, 45, 0);
const c2b = padAt(P.C2.x, P.C2.y, 90, 45, 0);

trk('PWM', j1p.x, j1p.y, j1p.x, uINA.y, 12);
trk('PWM', j1p.x, uINA.y, uINA.x, uINA.y, 12);
trk('GND', j1g.x, j1g.y, uGND.x, j1g.y, 20);
trk('GND', uGND.x, j1g.y, uGND.x, uGND.y, 20);
trk('GND', uGND.x, uINB.y, uINB.x, uINB.y, 12);
trk('GATE_DRV', uOUTA.x, uOUTA.y, rg1.x, uOUTA.y, 12);
trk('GATE_DRV', rg1.x, uOUTA.y, rg1.x, rg1.y, 12);
trk('GATE', rg2.x, rg2.y, qG.x, rg2.y, 12);
trk('GATE', qG.x, rg2.y, qG.x, qG.y, 12);
trk('GATE', qG.x, qG.y, rgsG2.x, qG.y, 12);
trk('GATE', rgsG2.x, qG.y, rgsG2.x, rgsG2.y, 12);
trk('DRAIN', qD.x, qD.y, qD.x, tPriN.y, 25);
trk('DRAIN', qD.x, tPriN.y, tPriN.x, tPriN.y, 25);
trk('DRAIN', qD.x, qD.y, dK.x, qD.y, 20);
trk('DRAIN', dK.x, qD.y, dK.x, dK.y, 20);
trk('+12V', j2p.x, j2p.y, tPriP.x, j2p.y, 30);
trk('+12V', tPriP.x, j2p.y, tPriP.x, tPriP.y, 30);
trk('+12V', uVDD.x, uVDD.y, uVDD.x, c2b.y, 20);
trk('+12V', uVDD.x, c2b.y, c2b.x, c2b.y, 20);
trk('+12V', c2b.x, c2b.y, tPriP.x, c2b.y, 20);
trk('+12V', c1b.x, c1b.y, c2b.x, c1b.y, 20);
trk('SEC+', tSecP.x, tSecP.y, tSecP.x, lA.y, 20);
trk('SEC+', tSecP.x, lA.y, lA.x, lA.y, 20);
trk('LC_MID', lB.x, lB.y, lB.x, cA.y, 20);
trk('LC_MID', lB.x, cA.y, cA.x, cA.y, 20);
trk('TX+', cB.x, cB.y, j3p.x, cB.y, 20);
trk('TX+', j3p.x, cB.y, j3p.x, j3p.y, 20);
trk('TX-', tSecN.x, tSecN.y, tSecN.x, j3n.y, 20);
trk('TX-', tSecN.x, j3n.y, j3n.x, j3n.y, 20);

via('GND', 500, 1000);
via('GND', 800, 2000);
via('GND', 1500, 1000);
via('GND', 2200, 900);
via('GND', 3000, 900);
via('GND', 3700, 1100);
via('+12V', 600, 700);
via('+12V', 1400, 1100);

run('add-pour.js', ['rect', '--dir', DIR, '--pcb', PCB, '--net', 'GND', '--layer', '1',
  '--x', '50', '--y', '50', '--w', '3900', '--h', '2700']);
run('add-pour.js', ['rect', '--dir', DIR, '--pcb', PCB, '--net', 'GND', '--layer', '2',
  '--x', '50', '--y', '50', '--w', '3900', '--h', '2700']);

run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'AIsonic TX V1', '--x', '2000', '--y', '2680', '--layer', '3', '--size', '80']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'PWM', '--x', '250', '--y', '2550', '--layer', '3', '--size', '50']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', '+12V', '--x', '250', '--y', '220', '--layer', '3', '--size', '50']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'TX PZT', '--x', '3600', '--y', '280', '--layer', '3', '--size', '50']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'HV KEEP CLEAR', '--x', '3300', '--y', '1100', '--layer', '3', '--size', '40']);

run('validate.js', ['--dir', DIR]);
run('cleanup.js', ['--dir', DIR]);
console.log('\nTX PCB rebuilt', DIR);

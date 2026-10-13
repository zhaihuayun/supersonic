#!/usr/bin/env node
'use strict';
/**
 * Build AIsonic RX analog frontend board (.eprj3) via official EasyEDA scripts.
 * Chain: PZT → protect → OPA320 LNA → RC BPF → AD8338 VGA → ADC bias
 */
const fs = require('fs');
const path = require('path');
const { run, pinTip, padAt, segs, setSheetSize } = require('./_eprj3_util');

const DIR = path.resolve(__dirname, 'AIsonic_RX_Frontend_V1');
const SCH = 'Schematic1';
const SHEET = 'P1';
const PCB = 'PCB1';
const L = 10;

if (fs.existsSync(DIR)) {
  fs.rmSync(DIR, { recursive: true, force: true });
}
fs.mkdirSync(path.dirname(DIR), { recursive: true });

// PCB 90.0 mm x 55.0 mm — snap to 3600 x 2200 mil. Schematic A2.
run('init.js', ['--dir', DIR, '--name', 'AIsonic_RX_Frontend_V1', '--sheet', SHEET, '--board-w', '3600', '--board-h', '2200']);
setSheetSize(DIR, SCH, SHEET, 'A2');

run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'OPA320', '--designator', 'U',
  '--description', 'OPA320 RRIO opamp SOT-23-5',
  '--pins', '3:IN+:-20:10:0;4:IN-:-20:-10:0;1:OUT:20:0:180;5:VDD:20:15:180;2:VSS:20:-15:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'AD8338', '--designator', 'U',
  '--description', 'AD8338 VGA LFCSP-16',
  '--pins', [
    '1:INPR:-20:35:0', '2:INPD:-20:25:0', '3:INMD:-20:15:0', '4:INMR:-20:5:0',
    '5:COMM:-20:-5:0', '6:MODE:-20:-15:0', '7:GAIN:-20:-25:0', '8:DETO:-20:-35:0',
    '16:VREF:20:35:180', '15:VBAT:20:25:180', '14:OFSN:20:15:180', '13:VAGC:20:5:180',
    '12:FBKP:20:-5:180', '11:OUTP:20:-15:180', '10:OUTM:20:-25:180', '9:FBKM:20:-35:180'
  ].join(';')]);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'BAT54S', '--designator', 'D',
  '--description', 'BAT54S series dual diode SOT-23',
  '--pins', '1:A1:-20:-10:0;3:COM:-20:10:0;2:C2:20:0:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'CONN2R', '--designator', 'J',
  '--description', '2-pin connector pins on right',
  '--pins', '1:1:20:10:180;2:2:20:-10:180']);
run('generate-symbol.js', ['from-pins', '--dir', DIR, '--name', 'CONN4L', '--designator', 'J',
  '--description', '4-pin connector pins on left',
  '--pins', '1:1:-20:15:0;2:2:-20:5:0;3:3:-20:-5:0;4:4:-20:-15:0']);

run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'SOT235', '--designator', 'U',
  '--pads', '1:-37:-45:32:48;2:0:-45:32:48;3:37:-45:32:48;4:37:45:32:48;5:-37:45:32:48',
  '--outline', 'R,0,0,114,63',
  '--silk', 'rect,-50,-55,50,55;path,-50,40,-65,40']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'SOT23', '--designator', 'D',
  '--pads', '1:-37:-45:32:48;2:37:-45:32:48;3:0:45:32:48',
  '--outline', 'R,0,0,114,51',
  '--silk', 'rect,-50,-55,50,55;path,-50,-40,-65,-40']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'LFCSP16', '--designator', 'U',
  '--pads', [
    '1:-67:29.5:32:14', '2:-67:9.8:32:14', '3:-67:-9.8:32:14', '4:-67:-29.5:32:14',
    '5:-29.5:-67:14:32', '6:-9.8:-67:14:32', '7:9.8:-67:14:32', '8:29.5:-67:14:32',
    '9:67:-29.5:32:14', '10:67:-9.8:32:14', '11:67:9.8:32:14', '12:67:29.5:32:14',
    '13:29.5:67:14:32', '14:9.8:67:14:32', '15:-9.8:67:14:32', '16:-29.5:67:14:32',
    '17:0:0:70:70'
  ].join(';'),
  '--outline', 'R,0,0,118,118',
  '--silk', 'rect,-59,-59,59,59;path,-59,40,-80,40']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'R0805', '--designator', 'R',
  '--pads', '1:-45:0:48:60;2:45:0:48:60',
  '--outline', 'R,0,0,80,50',
  '--silk', 'rect,-50,-32,50,32']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'C0805', '--designator', 'C',
  '--pads', '1:-45:0:48:60;2:45:0:48:60',
  '--outline', 'R,0,0,80,50',
  '--silk', 'rect,-50,-32,50,32']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'FB0805', '--designator', 'FB',
  '--pads', '1:-45:0:48:60;2:45:0:48:60',
  '--outline', 'R,0,0,80,50',
  '--silk', 'rect,-50,-32,50,32']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'KF381', '--designator', 'J',
  '--pads', '1:0:0:90:90:51;2:150:0:90:90:51',
  '--outline', 'R,75,80,320,240',
  '--silk', 'rect,-40,-40,190,200']);
run('generate-footprint.js', ['from-pads', '--dir', DIR, '--name', 'KF381_4', '--designator', 'J',
  '--pads', '1:0:0:90:90:51;2:150:0:90:90:51;3:300:0:90:90:51;4:450:0:90:90:51',
  '--outline', 'R,225,80,560,240',
  '--silk', 'rect,-40,-40,490,200']);

run('load-library.js', ['power', '--dir', DIR, '--net', '+3V3', '--style', 'up', '--name', 'P3V3']);

const J1 = { x: 220, y: -400 };
const Cin = { x: 420, y: -390 };
const Rser = { x: 580, y: -390 };
const D2 = { x: 640, y: -560 };
const U2 = { x: 820, y: -400 };
const Rf = { x: 820, y: -250 };
const Rg = { x: 700, y: -560 };
const Rb1 = { x: 500, y: -180 };
const Rb2 = { x: 620, y: -180 };
const Cvref = { x: 560, y: -80 };
const Rp1 = { x: 1080, y: -390 };
const Cp1 = { x: 1080, y: -560 };
const Rp2 = { x: 1240, y: -390 };
const Cp2 = { x: 1240, y: -560 };
const U3 = { x: 1550, y: -400 };
const Cadc = { x: 1860, y: -415 };
const Radc = { x: 1860, y: -560 };
const J2 = { x: 2100, y: -400 };
const J3 = { x: 220, y: -180 };
const FB1 = { x: 820, y: -80 };
const C3v = { x: 960, y: -80 };
const C3b = { x: 1080, y: -80 };
const Cdec = { x: 1550, y: -80 };
const Cref = { x: 1700, y: -80 };

const t = {
  J1_1: pinTip(J1.x, J1.y, 0, 20, 10, L, 180),
  J1_2: pinTip(J1.x, J1.y, 0, 20, -10, L, 180),
  Cin1: pinTip(Cin.x, Cin.y, 0, -20, 0, L, 0),
  Cin2: pinTip(Cin.x, Cin.y, 0, 20, 0, L, 180),
  Rs1: pinTip(Rser.x, Rser.y, 0, -20, 0, L, 0),
  Rs2: pinTip(Rser.x, Rser.y, 0, 20, 0, L, 180),
  DA1: pinTip(D2.x, D2.y, 0, -20, -10, L, 0),
  DCOM: pinTip(D2.x, D2.y, 0, -20, 10, L, 0),
  DC2: pinTip(D2.x, D2.y, 0, 20, 0, L, 180),
  INP: pinTip(U2.x, U2.y, 0, -20, 10, L, 0),
  INM: pinTip(U2.x, U2.y, 0, -20, -10, L, 0),
  OUT: pinTip(U2.x, U2.y, 0, 20, 0, L, 180),
  VDD: pinTip(U2.x, U2.y, 0, 20, 15, L, 180),
  VSS: pinTip(U2.x, U2.y, 0, 20, -15, L, 180),
  Rf1: pinTip(Rf.x, Rf.y, 0, -20, 0, L, 0),
  Rf2: pinTip(Rf.x, Rf.y, 0, 20, 0, L, 180),
  Rg1: pinTip(Rg.x, Rg.y, 0, -20, 0, L, 0),
  Rg2: pinTip(Rg.x, Rg.y, 0, 20, 0, L, 180),
  Rb1a: pinTip(Rb1.x, Rb1.y, 0, -20, 0, L, 0),
  Rb1b: pinTip(Rb1.x, Rb1.y, 0, 20, 0, L, 180),
  Rb2a: pinTip(Rb2.x, Rb2.y, 0, -20, 0, L, 0),
  Rb2b: pinTip(Rb2.x, Rb2.y, 0, 20, 0, L, 180),
  Cv1: pinTip(Cvref.x, Cvref.y, 0, -20, 0, L, 0),
  Cv2: pinTip(Cvref.x, Cvref.y, 0, 20, 0, L, 180),
  Rp1a: pinTip(Rp1.x, Rp1.y, 0, -20, 0, L, 0),
  Rp1b: pinTip(Rp1.x, Rp1.y, 0, 20, 0, L, 180),
  Cp1a: pinTip(Cp1.x, Cp1.y, 0, -20, 0, L, 0),
  Cp1b: pinTip(Cp1.x, Cp1.y, 0, 20, 0, L, 180),
  Rp2a: pinTip(Rp2.x, Rp2.y, 0, -20, 0, L, 0),
  Rp2b: pinTip(Rp2.x, Rp2.y, 0, 20, 0, L, 180),
  Cp2a: pinTip(Cp2.x, Cp2.y, 0, -20, 0, L, 0),
  Cp2b: pinTip(Cp2.x, Cp2.y, 0, 20, 0, L, 180),
  INPR: pinTip(U3.x, U3.y, 0, -20, 35, L, 0),
  INMR: pinTip(U3.x, U3.y, 0, -20, 5, L, 0),
  COMM: pinTip(U3.x, U3.y, 0, -20, -5, L, 0),
  MODE: pinTip(U3.x, U3.y, 0, -20, -15, L, 0),
  GAIN: pinTip(U3.x, U3.y, 0, -20, -25, L, 0),
  DETO: pinTip(U3.x, U3.y, 0, -20, -35, L, 0),
  VREF15: pinTip(U3.x, U3.y, 0, 20, 35, L, 180),
  VBAT: pinTip(U3.x, U3.y, 0, 20, 25, L, 180),
  OFSN: pinTip(U3.x, U3.y, 0, 20, 15, L, 180),
  VAGC: pinTip(U3.x, U3.y, 0, 20, 5, L, 180),
  OUTP: pinTip(U3.x, U3.y, 0, 20, -15, L, 180),
  Ca1: pinTip(Cadc.x, Cadc.y, 0, -20, 0, L, 0),
  Ca2: pinTip(Cadc.x, Cadc.y, 0, 20, 0, L, 180),
  Ra1: pinTip(Radc.x, Radc.y, 0, -20, 0, L, 0),
  Ra2: pinTip(Radc.x, Radc.y, 0, 20, 0, L, 180),
  J2_1: pinTip(J2.x, J2.y, 0, -20, 15, L, 0),
  J2_2: pinTip(J2.x, J2.y, 0, -20, 5, L, 0),
  J2_3: pinTip(J2.x, J2.y, 0, -20, -5, L, 0),
  J2_4: pinTip(J2.x, J2.y, 0, -20, -15, L, 0),
  J3_1: pinTip(J3.x, J3.y, 0, 20, 10, L, 180),
  J3_2: pinTip(J3.x, J3.y, 0, 20, -10, L, 180),
  FB1a: pinTip(FB1.x, FB1.y, 0, -20, 0, 3, 0),
  FB1b: pinTip(FB1.x, FB1.y, 0, 20, 0, 3, 180),
  C3a: pinTip(C3v.x, C3v.y, 0, -20, 0, L, 0),
  C3b: pinTip(C3v.x, C3v.y, 0, 20, 0, L, 180),
  Cb1: pinTip(C3b.x, C3b.y, 0, -20, 0, L, 0),
  Cb2: pinTip(C3b.x, C3b.y, 0, 20, 0, L, 180),
  Cd1: pinTip(Cdec.x, Cdec.y, 0, -20, 0, L, 0),
  Cd2: pinTip(Cdec.x, Cdec.y, 0, 20, 0, L, 180),
  Cr1: pinTip(Cref.x, Cref.y, 0, -20, 0, L, 0),
  Cr2: pinTip(Cref.x, Cref.y, 0, 20, 0, L, 180)
};

function addSym(symbol, fp, x, y, refdes, name, rotation) {
  const args = ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--symbol', symbol, '--x', String(x), '--y', String(y), '--refdes', refdes];
  if (fp) args.push('--footprint', fp);
  if (name) args.push('--name', name);
  if (rotation) args.push('--rotation', String(rotation));
  run('add-symbol.js', args);
}
function addPwr(symbol, x, y) {
  run('add-symbol.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--symbol', symbol, '--x', String(x), '--y', String(y)]);
}
function wire(net, ...pts) {
  run('add-wire.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--net', net, '--segs', segs(...pts)]);
}
function box(x1, y1, x2, y2, title) {
  run('add-shape.js', ['rect', '--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x1', String(x1), '--y1', String(y1), '--x2', String(x2), '--y2', String(y2)]);
  run('add-text.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x', String(x1 + 5), '--y', String(y1 + 15), '--value', title]);
}

run('add-text.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x', '200', '--y', '-40',
  '--value', 'AIsonic RX Frontend V1.0  |  200kHz  |  BAT54S + OPA320 + RC-BPF + AD8338']);

box(160, -120, 400, -280, 'J3 AGC  |  J1 RX PZT');
box(400, -300, 1000, -680, 'PROTECT + U2 OPA320 LNA ~20dB');
box(1020, -300, 1380, -680, 'RC BPF 200kHz');
box(1400, -280, 1780, -680, 'U3 AD8338 VGA');
box(1800, -300, 2260, -680, 'ADC BIAS + J2 MCU');
box(430, -50, 1200, -230, 'VREF 1.65V  |  +3V3');

addSym('CONN2R', 'KF381', J1.x, J1.y, 'J1', 'KF2EDG-3.81 RX+/RX-');
addSym('CONN2R', 'KF381', J3.x, J3.y, 'J3', 'KF2EDG-3.81 AGC/GND');
addSym('CAP', 'C0805', Cin.x, Cin.y, 'Cin', '100nF');
addSym('RES', 'R0805', Rser.x, Rser.y, 'Rser', '100R');
addSym('BAT54S', 'SOT23', D2.x, D2.y, 'D2', 'BAT54S');
addSym('OPA320', 'SOT235', U2.x, U2.y, 'U2', 'OPA320AIDBVT');
addSym('RES', 'R0805', Rf.x, Rf.y, 'Rf', '100k');
addSym('RES', 'R0805', Rg.x, Rg.y, 'Rg_lna', '10k');
addSym('RES', 'R0805', Rb1.x, Rb1.y, 'Rbias1', '10k');
addSym('RES', 'R0805', Rb2.x, Rb2.y, 'Rbias2', '10k');
addSym('CAP', 'C0805', Cvref.x, Cvref.y, 'Cvref', '100nF');
addSym('RES', 'R0805', Rp1.x, Rp1.y, 'Rbpf1', '3.9k');
addSym('CAP', 'C0805', Cp1.x, Cp1.y, 'Cbpf1', '2.2nF');
addSym('RES', 'R0805', Rp2.x, Rp2.y, 'Rbpf2', '3.9k');
addSym('CAP', 'C0805', Cp2.x, Cp2.y, 'Cbpf2', '2.2nF');
addSym('AD8338', 'LFCSP16', U3.x, U3.y, 'U3', 'AD8338ACPZ-R7');
addSym('CAP', 'C0805', Cadc.x, Cadc.y, 'Cadc', '100nF');
addSym('RES', 'R0805', Radc.x, Radc.y, 'Radc', '10k');
addSym('CONN4L', 'KF381_4', J2.x, J2.y, 'J2', 'KF2EDG-3.81 MCU');
addSym('IND', 'FB0805', FB1.x, FB1.y, 'FB1', '600R@100MHz');
addSym('CAP', 'C0805', C3v.x, C3v.y, 'C3', '100nF');
addSym('CAP', 'C0805', C3b.x, C3b.y, 'C4', '10uF 16V');
addSym('CAP', 'C0805', Cdec.x, Cdec.y, 'C5', '100nF');
addSym('CAP', 'C0805', Cref.x, Cref.y, 'C6', '100nF');

addPwr('P3V3', t.Rb1a.x - 30, t.Rb1a.y + 40);
addPwr('P3V3', t.DC2.x + 40, t.DC2.y + 40);
addPwr('P3V3', t.VDD.x + 40, t.VDD.y + 40);
addPwr('P3V3', t.MODE.x - 40, t.MODE.y);
addPwr('P3V3', t.VBAT.x + 40, t.VBAT.y + 40);
addPwr('P3V3', t.J2_3.x - 30, t.J2_3.y);
addPwr('GND', t.J1_2.x, t.J1_2.y - 70);
addPwr('GND', t.J3_2.x, t.J3_2.y - 50);
addPwr('GND', t.DA1.x - 20, t.DA1.y - 40);
addPwr('GND', t.VSS.x + 40, t.VSS.y - 30);
addPwr('GND', t.Rb2b.x + 20, t.Rb2b.y - 40);
addPwr('GND', t.Cp1b.x, t.Cp1b.y - 40);
addPwr('GND', t.Cp2b.x, t.Cp2b.y - 40);
addPwr('GND', t.COMM.x - 30, t.COMM.y - 20);
addPwr('GND', t.DETO.x - 30, t.DETO.y - 20);
addPwr('GND', t.OFSN.x + 40, t.OFSN.y);
addPwr('GND', t.J2_4.x - 30, t.J2_4.y - 40);
addPwr('GND', t.INMR.x - 50, t.INMR.y);

wire('RX+', t.J1_1, { x: t.Cin1.x, y: t.J1_1.y }, t.Cin1);
wire('GND', t.J1_2, { x: t.J1_2.x, y: t.J1_2.y - 70 });
wire('AC_IN', t.Cin2, { x: t.Rs1.x, y: t.Cin2.y }, t.Rs1);
wire('CLAMP', t.Rs2, { x: t.INP.x, y: t.Rs2.y }, t.INP);
wire('CLAMP', t.DCOM, { x: t.DCOM.x - 15, y: t.DCOM.y }, { x: t.DCOM.x - 15, y: t.INP.y }, t.INP);
wire('GND', t.DA1, { x: t.DA1.x - 20, y: t.DA1.y }, { x: t.DA1.x - 20, y: t.DA1.y - 40 });
wire('+3V3', t.DC2, { x: t.DC2.x + 40, y: t.DC2.y }, { x: t.DC2.x + 40, y: t.DC2.y + 40 });
wire('LNA_OUT', t.OUT, { x: t.Rf2.x + 30, y: t.OUT.y }, { x: t.Rf2.x + 30, y: t.Rf2.y }, t.Rf2);
wire('LNA_FB', t.INM, { x: t.INM.x - 25, y: t.INM.y }, { x: t.INM.x - 25, y: t.Rf1.y }, t.Rf1);
wire('LNA_FB', t.INM, { x: t.Rg2.x, y: t.INM.y }, t.Rg2);
wire('VREF', t.Rg1, { x: t.Rg1.x, y: t.Rb2a.y }, { x: t.Rb2a.x, y: t.Rb2a.y });
wire('+3V3', t.VDD, { x: t.VDD.x + 40, y: t.VDD.y }, { x: t.VDD.x + 40, y: t.VDD.y + 40 });
wire('GND', t.VSS, { x: t.VSS.x + 40, y: t.VSS.y }, { x: t.VSS.x + 40, y: t.VSS.y - 30 });
wire('+3V3', t.Rb1a, { x: t.Rb1a.x - 30, y: t.Rb1a.y }, { x: t.Rb1a.x - 30, y: t.Rb1a.y + 40 });
wire('VREF', t.Rb1b, { x: t.Rb2a.x, y: t.Rb1b.y }, t.Rb2a);
wire('GND', t.Rb2b, { x: t.Rb2b.x + 20, y: t.Rb2b.y }, { x: t.Rb2b.x + 20, y: t.Rb2b.y - 40 });
wire('VREF', t.Cv1, { x: t.Cv1.x, y: t.Rb1b.y });
wire('GND', t.Cv2, { x: t.Cv2.x, y: t.Cv2.y + 30 }, { x: t.Rb2b.x + 20, y: t.Cv2.y + 30 });
wire('LNA_OUT', t.OUT, { x: t.Rp1a.x, y: t.OUT.y }, t.Rp1a);
wire('BPF1', t.Rp1b, { x: t.Rp2a.x, y: t.Rp1b.y }, t.Rp2a);
wire('BPF1', t.Cp1a, { x: t.Cp1a.x, y: t.Rp1b.y });
wire('GND', t.Cp1b, { x: t.Cp1b.x, y: t.Cp1b.y - 40 });
wire('VGA_IN', t.Rp2b, { x: t.INPR.x, y: t.Rp2b.y }, { x: t.INPR.x, y: t.INPR.y }, t.INPR);
wire('VGA_IN', t.Cp2a, { x: t.Cp2a.x, y: t.Rp2b.y });
wire('GND', t.Cp2b, { x: t.Cp2b.x, y: t.Cp2b.y - 40 });
wire('GND', t.INMR, { x: t.INMR.x - 50, y: t.INMR.y });
wire('GND', t.COMM, { x: t.COMM.x - 30, y: t.COMM.y }, { x: t.COMM.x - 30, y: t.COMM.y - 20 });
wire('+3V3', t.MODE, { x: t.MODE.x - 40, y: t.MODE.y });
wire('AGC_CTRL', t.J3_1, { x: t.GAIN.x - 60, y: t.J3_1.y }, { x: t.GAIN.x - 60, y: t.GAIN.y }, t.GAIN);
wire('GND', t.J3_2, { x: t.J3_2.x, y: t.J3_2.y - 50 });
wire('GND', t.DETO, { x: t.DETO.x - 30, y: t.DETO.y }, { x: t.DETO.x - 30, y: t.DETO.y - 20 });
wire('VREF_1V5', t.VREF15, { x: t.VAGC.x + 25, y: t.VREF15.y }, { x: t.VAGC.x + 25, y: t.VAGC.y }, t.VAGC);
wire('+3V3', t.VBAT, { x: t.VBAT.x + 40, y: t.VBAT.y }, { x: t.VBAT.x + 40, y: t.VBAT.y + 40 });
wire('GND', t.OFSN, { x: t.OFSN.x + 40, y: t.OFSN.y });
wire('VGA_OUT', t.OUTP, { x: t.Ca1.x, y: t.OUTP.y }, t.Ca1);
wire('ADC_OUT', t.Ca2, { x: t.J2_1.x, y: t.Ca2.y }, { x: t.J2_1.x, y: t.J2_1.y }, t.J2_1);
wire('ADC_OUT', t.Ra2, { x: t.Ra2.x, y: t.Ca2.y });
wire('VREF', t.Ra1, { x: t.Ra1.x - 40, y: t.Ra1.y }, { x: t.Ra1.x - 40, y: t.Rb2a.y }, { x: t.Rb2a.x, y: t.Rb2a.y });
wire('VREF', t.J2_2, { x: t.J2_2.x - 40, y: t.J2_2.y }, { x: t.J2_2.x - 40, y: t.Ra1.y - 20 }, { x: t.Ra1.x - 40, y: t.Ra1.y - 20 });
wire('+3V3', t.J2_3, { x: t.J2_3.x - 30, y: t.J2_3.y });
wire('GND', t.J2_4, { x: t.J2_4.x - 30, y: t.J2_4.y }, { x: t.J2_4.x - 30, y: t.J2_4.y - 40 });
wire('+3V3', t.FB1a, { x: t.FB1a.x, y: t.FB1a.y + 30 }, { x: t.Rb1a.x - 30, y: t.FB1a.y + 30 });
wire('+3V3', t.FB1b, { x: t.C3a.x, y: t.FB1b.y }, t.C3a);
wire('+3V3', t.Cb1, { x: t.C3a.x, y: t.Cb1.y });
wire('GND', t.C3b, { x: t.C3b.x, y: t.C3b.y + 25 }, { x: t.Cb2.x, y: t.C3b.y + 25 }, t.Cb2);
wire('+3V3', t.Cd1, { x: t.VBAT.x + 40, y: t.Cd1.y }, { x: t.VBAT.x + 40, y: t.VBAT.y });
wire('GND', t.Cd2, { x: t.Cd2.x, y: t.Cd2.y + 25 }, { x: t.Cr2.x, y: t.Cd2.y + 25 }, t.Cr2);
wire('VREF_1V5', t.Cr1, { x: t.Cr1.x, y: t.VREF15.y }, t.VREF15);

run('add-text.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x', '200', '--y', '-720',
  '--value', 'J2: 1 ADC_OUT  2 VREF 1.65V  3 +3V3  4 GND   |   J3: 1 AGC_CTRL (DAC 0.1~1.1V)  2 GND']);
run('add-text.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x', '200', '--y', '-750',
  '--value', 'MODE=+3V3 (gain rises with GAIN)  |  DETO/OFSN/INMR=GND  |  VAGC=VREF 1.5V  |  LCSC: C206063 / C578701 / C727126']);
run('add-text.js', ['--dir', DIR, '--sch', SCH, '--sheet', SHEET, '--x', '200', '--y', '-780',
  '--value', 'BPF 3.9k+2.2nF is a starting point — tune to 170~230 kHz on the bench.  FBKP/FBKM/INPD/INMD/OUTM left open (internal default).']);

function addFp(symbol, fp, x, y, refdes, name, nets, angle) {
  const args = ['--dir', DIR, '--pcb', PCB, '--symbol', symbol, '--footprint', fp,
    '--x', String(x), '--y', String(y), '--refdes', refdes, '--name', name, '--nets', nets];
  if (angle) args.push('--angle', String(angle));
  run('add-footprint.js', args);
}

const P = {
  J1: { x: 200, y: 400 },
  J3: { x: 200, y: 1800 },
  Cin: { x: 550, y: 500 },
  Rser: { x: 750, y: 500 },
  D2: { x: 750, y: 800 },
  U2: { x: 1100, y: 700 },
  Rf: { x: 1100, y: 450 },
  Rg: { x: 900, y: 950 },
  Rb1: { x: 500, y: 1600 },
  Rb2: { x: 700, y: 1600 },
  Cvref: { x: 600, y: 1350 },
  Rp1: { x: 1450, y: 600 },
  Cp1: { x: 1450, y: 900 },
  Rp2: { x: 1650, y: 600 },
  Cp2: { x: 1650, y: 900 },
  U3: { x: 2100, y: 1100 },
  Cadc: { x: 2550, y: 1100 },
  Radc: { x: 2550, y: 1400 },
  J2: { x: 2900, y: 900 },
  FB1: { x: 500, y: 1100 },
  C3: { x: 1100, y: 1600 },
  C4: { x: 1300, y: 1600 },
  C5: { x: 2100, y: 1600 },
  C6: { x: 2300, y: 1600 }
};

addFp('CONN2R', 'KF381', P.J1.x, P.J1.y, 'J1', 'KF2EDG-3.81', '1:RX+,2:GND');
addFp('CONN2R', 'KF381', P.J3.x, P.J3.y, 'J3', 'KF2EDG-3.81', '1:AGC_CTRL,2:GND');
addFp('CAP', 'C0805', P.Cin.x, P.Cin.y, 'Cin', '100nF', '1:RX+,2:AC_IN');
addFp('RES', 'R0805', P.Rser.x, P.Rser.y, 'Rser', '100R', '1:AC_IN,2:CLAMP');
addFp('BAT54S', 'SOT23', P.D2.x, P.D2.y, 'D2', 'BAT54S', '1:GND,2:+3V3,3:CLAMP');
addFp('OPA320', 'SOT235', P.U2.x, P.U2.y, 'U2', 'OPA320AIDBVT', '1:LNA_OUT,2:GND,3:CLAMP,4:LNA_FB,5:+3V3');
addFp('RES', 'R0805', P.Rf.x, P.Rf.y, 'Rf', '100k', '1:LNA_FB,2:LNA_OUT');
addFp('RES', 'R0805', P.Rg.x, P.Rg.y, 'Rg_lna', '10k', '1:VREF,2:LNA_FB');
addFp('RES', 'R0805', P.Rb1.x, P.Rb1.y, 'Rbias1', '10k', '1:+3V3,2:VREF');
addFp('RES', 'R0805', P.Rb2.x, P.Rb2.y, 'Rbias2', '10k', '1:VREF,2:GND');
addFp('CAP', 'C0805', P.Cvref.x, P.Cvref.y, 'Cvref', '100nF', '1:VREF,2:GND', 90);
addFp('RES', 'R0805', P.Rp1.x, P.Rp1.y, 'Rbpf1', '3.9k', '1:LNA_OUT,2:BPF1');
addFp('CAP', 'C0805', P.Cp1.x, P.Cp1.y, 'Cbpf1', '2.2nF', '1:BPF1,2:GND', 90);
addFp('RES', 'R0805', P.Rp2.x, P.Rp2.y, 'Rbpf2', '3.9k', '1:BPF1,2:VGA_IN');
addFp('CAP', 'C0805', P.Cp2.x, P.Cp2.y, 'Cbpf2', '2.2nF', '1:VGA_IN,2:GND', 90);
addFp('AD8338', 'LFCSP16', P.U3.x, P.U3.y, 'U3', 'AD8338ACPZ-R7',
  '1:VGA_IN,4:GND,5:GND,6:+3V3,7:AGC_CTRL,8:GND,11:VGA_OUT,13:VREF_1V5,14:GND,15:+3V3,16:VREF_1V5,17:GND');
addFp('CAP', 'C0805', P.Cadc.x, P.Cadc.y, 'Cadc', '100nF', '1:VGA_OUT,2:ADC_OUT');
addFp('RES', 'R0805', P.Radc.x, P.Radc.y, 'Radc', '10k', '1:VREF,2:ADC_OUT', 90);
addFp('CONN4L', 'KF381_4', P.J2.x, P.J2.y, 'J2', 'KF2EDG-3.81', '1:ADC_OUT,2:VREF,3:+3V3,4:GND');
addFp('IND', 'FB0805', P.FB1.x, P.FB1.y, 'FB1', '600R@100MHz', '1:+3V3,2:+3V3');
addFp('CAP', 'C0805', P.C3.x, P.C3.y, 'C3', '100nF', '1:+3V3,2:GND', 90);
addFp('CAP', 'C0805', P.C4.x, P.C4.y, 'C4', '10uF 16V', '1:+3V3,2:GND', 90);
addFp('CAP', 'C0805', P.C5.x, P.C5.y, 'C5', '100nF', '1:+3V3,2:GND', 90);
addFp('CAP', 'C0805', P.C6.x, P.C6.y, 'C6', '100nF', '1:VREF_1V5,2:GND', 90);

function trk(net, x1, y1, x2, y2, width) {
  run('add-track.js', ['--dir', DIR, '--pcb', PCB, '--net', net,
    '--x1', String(x1), '--y1', String(y1), '--x2', String(x2), '--y2', String(y2), '--width', String(width || 10)]);
}
function via(net, x, y) {
  run('add-via.js', ['--dir', DIR, '--pcb', PCB, '--net', net, '--x', String(x), '--y', String(y)]);
}

const j1p = padAt(P.J1.x, P.J1.y, 0, 0, 0);
const cinA = padAt(P.Cin.x, P.Cin.y, 0, -45, 0);
const cinB = padAt(P.Cin.x, P.Cin.y, 0, 45, 0);
const rsA = padAt(P.Rser.x, P.Rser.y, 0, -45, 0);
const rsB = padAt(P.Rser.x, P.Rser.y, 0, 45, 0);
const dCom = padAt(P.D2.x, P.D2.y, 0, 0, 45);
const uInP = padAt(P.U2.x, P.U2.y, 0, 37, -45);
const uInM = padAt(P.U2.x, P.U2.y, 0, 37, 45);
const uOut = padAt(P.U2.x, P.U2.y, 0, -37, -45);
const rfA = padAt(P.Rf.x, P.Rf.y, 0, -45, 0);
const rfB = padAt(P.Rf.x, P.Rf.y, 0, 45, 0);
const rgB = padAt(P.Rg.x, P.Rg.y, 0, 45, 0);
const rp1A = padAt(P.Rp1.x, P.Rp1.y, 0, -45, 0);
const rp1B = padAt(P.Rp1.x, P.Rp1.y, 0, 45, 0);
const rp2A = padAt(P.Rp2.x, P.Rp2.y, 0, -45, 0);
const rp2B = padAt(P.Rp2.x, P.Rp2.y, 0, 45, 0);
const u3in = padAt(P.U3.x, P.U3.y, 0, -67, 29.5);
const u3out = padAt(P.U3.x, P.U3.y, 0, 67, 9.8);
const u3gain = padAt(P.U3.x, P.U3.y, 0, -9.8, -67);
const caA = padAt(P.Cadc.x, P.Cadc.y, 0, -45, 0);
const caB = padAt(P.Cadc.x, P.Cadc.y, 0, 45, 0);
const j2adc = padAt(P.J2.x, P.J2.y, 0, 0, 0);
const j3agc = padAt(P.J3.x, P.J3.y, 0, 0, 0);
const rb1A = padAt(P.Rb1.x, P.Rb1.y, 0, -45, 0);
const rb1B = padAt(P.Rb1.x, P.Rb1.y, 0, 45, 0);
const rb2A = padAt(P.Rb2.x, P.Rb2.y, 0, -45, 0);

trk('RX+', j1p.x, j1p.y, cinA.x, j1p.y, 12);
trk('RX+', cinA.x, j1p.y, cinA.x, cinA.y, 12);
trk('AC_IN', cinB.x, cinB.y, rsA.x, cinB.y, 10);
trk('AC_IN', rsA.x, cinB.y, rsA.x, rsA.y, 10);
trk('CLAMP', rsB.x, rsB.y, uInP.x, rsB.y, 10);
trk('CLAMP', uInP.x, rsB.y, uInP.x, uInP.y, 10);
trk('CLAMP', rsB.x, rsB.y, dCom.x, rsB.y, 10);
trk('CLAMP', dCom.x, rsB.y, dCom.x, dCom.y, 10);
trk('LNA_OUT', uOut.x, uOut.y, uOut.x, rfB.y, 10);
trk('LNA_OUT', uOut.x, rfB.y, rfB.x, rfB.y, 10);
trk('LNA_FB', rfA.x, rfA.y, uInM.x, rfA.y, 10);
trk('LNA_FB', uInM.x, rfA.y, uInM.x, uInM.y, 10);
trk('LNA_FB', uInM.x, uInM.y, rgB.x, uInM.y, 10);
trk('LNA_FB', rgB.x, uInM.y, rgB.x, rgB.y, 10);
trk('LNA_OUT', rfB.x, rfB.y, rp1A.x, rfB.y, 10);
trk('LNA_OUT', rp1A.x, rfB.y, rp1A.x, rp1A.y, 10);
trk('BPF1', rp1B.x, rp1B.y, rp2A.x, rp1B.y, 10);
trk('BPF1', rp2A.x, rp1B.y, rp2A.x, rp2A.y, 10);
trk('VGA_IN', rp2B.x, rp2B.y, u3in.x, rp2B.y, 10);
trk('VGA_IN', u3in.x, rp2B.y, u3in.x, u3in.y, 10);
trk('VGA_OUT', u3out.x, u3out.y, caA.x, u3out.y, 10);
trk('VGA_OUT', caA.x, u3out.y, caA.x, caA.y, 10);
trk('ADC_OUT', caB.x, caB.y, j2adc.x, caB.y, 10);
trk('ADC_OUT', j2adc.x, caB.y, j2adc.x, j2adc.y, 10);
trk('AGC_CTRL', j3agc.x, j3agc.y, u3gain.x, j3agc.y, 10);
trk('AGC_CTRL', u3gain.x, j3agc.y, u3gain.x, u3gain.y, 10);
trk('VREF', rb1B.x, rb1B.y, rb2A.x, rb1B.y, 10);
trk('+3V3', rb1A.x, rb1A.y, rb1A.x, rb1A.y - 80, 12);

via('GND', 400, 700);
via('GND', 900, 1200);
via('GND', 1500, 1300);
via('GND', 2100, 500);
via('GND', 2700, 1600);
via('+3V3', 600, 1200);
via('+3V3', 1200, 1300);
via('VREF', 800, 1400);

run('add-pour.js', ['rect', '--dir', DIR, '--pcb', PCB, '--net', 'GND', '--layer', '1',
  '--x', '50', '--y', '50', '--w', '3500', '--h', '2100']);
run('add-pour.js', ['rect', '--dir', DIR, '--pcb', PCB, '--net', 'GND', '--layer', '2',
  '--x', '50', '--y', '50', '--w', '3500', '--h', '2100']);

run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'AIsonic RX V1', '--x', '1800', '--y', '2100', '--layer', '3', '--size', '70']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'RX PZT', '--x', '200', '--y', '220', '--layer', '3', '--size', '40']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'MCU', '--x', '3000', '--y', '700', '--layer', '3', '--size', '40']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'AGC', '--x', '200', '--y', '2050', '--layer', '3', '--size', '40']);
run('add-pcb-text.js', ['--dir', DIR, '--pcb', PCB, '--value', 'KEEP AWAY FROM TX', '--x', '1800', '--y', '200', '--layer', '3', '--size', '40']);

setSheetSize(DIR, SCH, SHEET, 'A2');
run('validate.js', ['--dir', DIR]);
run('cleanup.js', ['--dir', DIR]);
console.log('\nPROJECT', DIR);

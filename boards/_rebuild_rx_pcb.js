#!/usr/bin/env node
'use strict';
/**
 * Rebuild RX PCB from the current schematic. Does NOT touch P1.esch2.
 * Unique IDs follow schematic gge1..gge24.
 */
const path = require('path');
const E = require(path.join(
  process.env.EASYEDA_EPRJ3_SKILL
    || path.join(process.env.USERPROFILE, '.cursor', 'skills', 'easyeda-eprj3'),
  'scripts/lib/eprj3'
));
const { run, padAt, resetPcb } = require('./_eprj3_util');

const DIR = path.resolve(__dirname, 'AIsonic_RX_Frontend_V1');
const PCB = 'PCB1';

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

resetPcb(DIR, PCB, E.rectPath(0, 0, 3600, 2200));

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
    '--x1', String(x1), '--y1', String(y1), '--x2', String(x2), '--y2', String(y2),
    '--width', String(width || 10)]);
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

run('validate.js', ['--dir', DIR]);
run('cleanup.js', ['--dir', DIR]);
console.log('\nRX PCB rebuilt', DIR);

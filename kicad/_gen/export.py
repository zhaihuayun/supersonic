"""Export fabrication / review outputs for a design module into <project>/output/."""
import importlib
import os
import shutil
import subprocess
import sys
import zipfile

import build_sch
import render

LAYERS = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'


def run(*args):
    r = subprocess.run(list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(' '.join(args) + '\n' + r.stdout + r.stderr)
    return r


def main(modname):
    mod = importlib.import_module(modname)
    d = build_sch.project_dir(mod)
    out = os.path.join(d, 'output')
    name = mod.PROJECT
    sch = os.path.join(d, name + '.kicad_sch')
    pcb = os.path.join(d, name + '.kicad_pcb')

    run('kicad-cli', 'sch', 'export', 'pdf', '-o', os.path.join(out, name + '_schematic.pdf'), sch)
    run('kicad-cli', 'sch', 'export', 'svg', '-o', out, sch)
    svg = os.path.join(out, name + '.svg')
    if os.path.exists(svg):
        os.replace(svg, os.path.join(out, name + '_schematic.svg'))
    run('kicad-cli', 'sch', 'export', 'bom', '--fields', 'Reference,Value,Footprint,LCSC,MPN,${QUANTITY}',
        '--labels', 'Designator,Value,Footprint,LCSC,MPN,Quantity', '--group-by', 'Value,Footprint,LCSC',
        '--exclude-dnp', '-o', os.path.join(out, name + '_BOM.csv'), sch)

    gdir = os.path.join(out, 'gerber')
    shutil.rmtree(gdir, ignore_errors=True)
    os.makedirs(gdir)
    run('kicad-cli', 'pcb', 'export', 'gerbers', '--layers', LAYERS, '--subtract-soldermask', '-o', gdir + '/', pcb)
    run('kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th',
        '--generate-map', '--map-format', 'pdf', '-o', gdir + '/', pcb)
    zpath = os.path.join(out, name + '_gerber.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(gdir)):
            z.write(os.path.join(gdir, f), f)
    shutil.rmtree(gdir)
    run('kicad-cli', 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'front',
        '--exclude-dnp', '-o', os.path.join(out, name + '_pos_top.csv'), pcb)
    w, h = mod.BOARD
    for side, layers in (('top', 'F.Cu,F.Silkscreen,Edge.Cuts'), ('bottom', 'B.Cu,Edge.Cuts')):
        base = os.path.join(out, '%s_pcb_%s' % (name, side))
        render.render(pcb, base, w, h, layers, 200)
        os.remove(base + '.pdf')
    for side in ('top', 'bottom'):
        try:
            run('kicad-cli', 'pcb', 'render', '--side', side, '--quality', 'high', '--width', '1600', '--height',
                '1100', '--background', 'opaque', '-o', os.path.join(out, '%s_3d_%s.png' % (name, side)), pcb)
        except RuntimeError as e:
            print('3D render skipped:', str(e).splitlines()[-1])
    print('exported', sorted(os.listdir(out)))


if __name__ == '__main__':
    main(sys.argv[1])

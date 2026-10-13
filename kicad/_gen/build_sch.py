"""Write KiCad project + schematic for a design module, then run ERC and netlist check."""
import importlib
import json
import os
import subprocess
import sys

import symlib
from schgen import POWER

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def project_dir(mod):
    return os.path.join(ROOT, mod.PROJECT)


def pcb_net(net):
    return net if net in POWER else '/' + net


def write_project(mod, d):
    pro = {
        'meta': {'filename': mod.PROJECT + '.kicad_pro', 'version': 3},
        'board': {'design_settings': {'defaults': {}, 'rules': {
            'min_clearance': 0.2, 'min_track_width': 0.2, 'min_via_diameter': 0.6,
            'min_through_hole_diameter': 0.3, 'min_copper_edge_clearance': 0.3}}},
        'net_settings': {
            'classes': [{'name': 'Default', 'clearance': 0.2, 'track_width': 0.3, 'via_diameter': 0.7,
                         'via_drill': 0.35, 'diff_pair_width': 0.2, 'diff_pair_gap': 0.25,
                         'microvia_diameter': 0.3, 'microvia_drill': 0.1, 'wire_width': 6, 'bus_width': 12,
                         'line_style': 0, 'schematic_color': 'rgba(0, 0, 0, 0.000)',
                         'pcb_color': 'rgba(0, 0, 0, 0.000)', 'priority': 2147483647}] + [
                {'name': n, 'clearance': v['clearance'], 'track_width': v['width'], 'via_diameter': 1.0,
                 'via_drill': 0.5, 'diff_pair_width': 0.2, 'diff_pair_gap': 0.25, 'microvia_diameter': 0.3,
                 'microvia_drill': 0.1, 'wire_width': 6, 'bus_width': 12, 'line_style': 0,
                 'schematic_color': 'rgba(0, 0, 0, 0.000)', 'pcb_color': 'rgba(0, 0, 0, 0.000)', 'priority': i}
                for i, (n, v) in enumerate(mod.NETCLASSES.items())],
            'meta': {'version': 4},
            'netclass_patterns': [{'netclass': n, 'pattern': pcb_net(net)}
                                  for n, v in mod.NETCLASSES.items() for net in v['nets']],
        },
        'schematic': {'legacy_lib_dir': '', 'legacy_lib_list': []},
        'sheets': [],
        'text_variables': {},
    }
    with open(os.path.join(d, mod.PROJECT + '.kicad_pro'), 'w') as f:
        json.dump(pro, f, indent=2)
    with open(os.path.join(d, 'sym-lib-table'), 'w') as f:
        f.write('(sym_lib_table\n  (version 7)\n  (lib (name "AIsonic")(type "KiCad")(uri "${KIPRJMOD}/AIsonic.kicad_sym")(options "")(descr "AIsonic project symbols"))\n)\n')
    with open(os.path.join(d, 'fp-lib-table'), 'w') as f:
        f.write('(fp_lib_table\n  (version 7)\n  (lib (name "AIsonic")(type "KiCad")(uri "${KIPRJMOD}/AIsonic.pretty")(options "")(descr "AIsonic project footprints"))\n)\n')
    symlib.write_symbol_lib(os.path.join(d, 'AIsonic.kicad_sym'))
    symlib.write_ee19_footprint(os.path.join(d, 'AIsonic.pretty'))


def check_netlist(sch, d, name):
    xml = os.path.join(d, 'output', name + '.net.xml')
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', xml,
                    os.path.join(d, name + '.kicad_sch')], check=True, capture_output=True)
    import xml.etree.ElementTree as ET
    got = {}
    for net in ET.parse(xml).getroot().find('nets'):
        nodes = sorted((n.get('ref'), n.get('pin')) for n in net.findall('node'))
        nm = net.get('name').lstrip('/')
        if nm.startswith('unconnected-'):
            continue
        got[nm] = nodes
    want = {k: sorted(v) for k, v in sch.netlist().items()}
    bad = []
    for k, v in want.items():
        if got.get(k) != v:
            bad.append((k, v, got.get(k)))
    for k in got:
        if k not in want:
            bad.append((k, None, got[k]))
    os.remove(xml)
    return bad


def main(modname):
    mod = importlib.import_module(modname)
    d = project_dir(mod)
    os.makedirs(os.path.join(d, 'output'), exist_ok=True)
    write_project(mod, d)
    sch = mod.build()
    path = os.path.join(d, mod.PROJECT + '.kicad_sch')
    sch.write(path)
    bad = check_netlist(sch, d, mod.PROJECT)
    for b in bad:
        print('NETLIST MISMATCH', b)
    erc = os.path.join(d, 'output', 'erc.rpt')
    subprocess.run(['kicad-cli', 'sch', 'erc', '--severity-all', '-o', erc, path], capture_output=True)
    print(open(erc).read()[-3000:])
    return sch, bad


if __name__ == '__main__':
    main(sys.argv[1])

"""Generate a KiCad 9 .kicad_sch from a net-annotated component list.

Every connected pin gets a short wire stub ending in a net label or a power
symbol, so connectivity is defined purely by net names (single source of truth
shared with the PCB generator).
"""
import math
import uuid

import symlib
from sexp import Sym, dump, find, find1, parse, q

STD = '/usr/share/kicad/symbols/'
POWER = {'GND': 'power:GND', '+12V': 'power:+12V', '+3V3': 'power:+3V3'}
G = 2.54

_lib_cache = {}


def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'aisonic/' + '/'.join(str(p) for p in parts)))


def lib_symbol(lib_id):
    lib, name = lib_id.split(':')
    if lib == 'AIsonic':
        return symlib.custom_symbol_nodes()[name]
    if lib not in _lib_cache:
        _lib_cache[lib] = parse(open(STD + lib + '.kicad_sym', encoding='utf-8').read())
    for s in find(_lib_cache[lib], 'symbol'):
        if s[1] == name:
            if find1(s, 'extends'):
                raise ValueError('%s uses extends; not supported' % lib_id)
            return s
    raise KeyError(lib_id)


def pins_of(lib_id):
    out = []

    def walk(n):
        for x in n:
            if isinstance(x, list) and x:
                if x[0] == 'pin':
                    at = find1(x, 'at')
                    out.append(dict(num=find1(x, 'number')[1], name=find1(x, 'name')[1], type=str(x[1]),
                                    x=float(at[1]), y=float(at[2]), ang=int(float(at[3]))))
                elif x[0] == 'symbol':
                    walk(x)
    walk(lib_symbol(lib_id))
    return out


def xform(px, py, rot, mirror):
    if mirror:
        px = -px
    r = math.radians(rot)
    qx = px * math.cos(r) - py * math.sin(r)
    qy = px * math.sin(r) + py * math.cos(r)
    return qx, -qy


def out_dir(ang, rot, mirror):
    a = ang + 180
    if mirror:
        a = 180 - a
    return (a + rot) % 360


DIRV = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}


def r2(v):
    return round(v, 2)


class Comp:
    def __init__(self, ref, lib_id, value, footprint, at, rot=0, nets=None, mirror=False, fields=None,
                 ref_pos=None, in_bom=True, power_side=False):
        self.ref, self.lib_id, self.value, self.footprint = ref, lib_id, value, footprint
        self.x, self.y = at[0] * G, at[1] * G
        self.rot, self.mirror = rot, mirror
        self.nets = nets or {}
        self.fields = fields or {}
        self.ref_pos = ref_pos
        self.in_bom = in_bom
        self.power_side = power_side


class Schematic:
    def __init__(self, project, title, paper='A3', rev='V1.0', comments=()):
        self.project, self.title, self.paper, self.rev, self.comments = project, title, paper, rev, comments
        self.root = uid(project, 'root')
        self.comps = []
        self.items = []
        self.used_libs = {}
        self.pwr_n = 0
        self.paths = []
        self.wired = set()

    def add(self, c):
        self.comps.append(c)
        return c

    def box(self, x1, y1, x2, y2, title, color=(0, 0, 194)):
        self.items.append('(rectangle (start %s %s) (end %s %s) (stroke (width 0.3) (type dash) (color %d %d %d 1)) '
                          '(fill (type none)) (uuid %s))' % (r2(x1 * G), r2(y1 * G), r2(x2 * G), r2(y2 * G),
                                                             *color, q(uid(self.project, 'box', x1, y1))))
        self.text(x1 + 0.5, y1 + 1.2, title, 2.0, bold=True, color=color)

    def text(self, x, y, s, size=1.5, bold=False, color=None):
        col = ' (color %d %d %d 1)' % color if color else ''
        self.items.append('(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s%s) '
                          '(justify left)) (uuid %s))' % (q(s), r2(x * G), r2(y * G), size, size,
                                                          ' (bold yes)' if bold else '', col,
                                                          q(uid(self.project, 'text', x, y, s))))

    def path(self, *pts):
        """Wire through pin endpoints ('R1', '2') and grid points (gx, gy)."""
        self.paths.append(pts)
        for p in pts:
            if isinstance(p[0], str):
                self.wired.add(p)

    def junction(self, gx, gy):
        self.items.append('(junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid %s))'
                          % (r2(gx * G), r2(gy * G), q(uid(self.project, 'j', gx, gy))))

    def _pin_xy(self, ref, num):
        c = next(c for c in self.comps if c.ref == ref)
        p = next(p for p in pins_of(c.lib_id) if p['num'] == num)
        ox, oy = xform(p['x'], p['y'], c.rot, c.mirror)
        return c.x + ox, c.y + oy

    def _draw_paths(self):
        segs = []
        labelled = set()
        for pts in self.paths:
            xy = [self._pin_xy(*p) if isinstance(p[0], str) else (p[0] * G, p[1] * G) for p in pts]
            first = []
            for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
                if abs(x1 - x2) > 0.01 and abs(y1 - y2) > 0.01:
                    first += [(x1, y1, x2, y1), (x2, y1, x2, y2)]
                else:
                    first.append((x1, y1, x2, y2))
            segs += first
            pin = next((p for p in pts if isinstance(p[0], str)), None)
            if pin is None:
                continue
            net = next(c for c in self.comps if c.ref == pin[0]).nets[pin[1]]
            if net in labelled or net in POWER:
                continue
            labelled.add(net)
            if all(pin in self.wired for pin in self._net_pins(net)):
                x1, y1, x2, y2 = max(first, key=lambda g: abs(g[0] - g[2]) + abs(g[1] - g[3]))
                if abs(y1 - y2) < 0.01:
                    self._label(net, min(x1, x2) + 1.27, y1, 0)
                else:
                    self._label(net, x1, max(y1, y2) - 1.27, 90)
        pts = {(r2(a), r2(b)) for g in segs for a, b in ((g[0], g[1]), (g[2], g[3]))}
        for x1, y1, x2, y2 in segs:
            cuts = [(x1, y1), (x2, y2)]
            for (px, py) in pts:
                if abs(x1 - x2) < 0.01 and abs(px - x1) < 0.01 and min(y1, y2) + 0.01 < py < max(y1, y2) - 0.01:
                    cuts.append((px, py))
                if abs(y1 - y2) < 0.01 and abs(py - y1) < 0.01 and min(x1, x2) + 0.01 < px < max(x1, x2) - 0.01:
                    cuts.append((px, py))
            cuts.sort(key=lambda c: (c[0] - x1) ** 2 + (c[1] - y1) ** 2)
            for a, b in zip(cuts, cuts[1:]):
                self._wire(a[0], a[1], b[0], b[1])

    def _net_pins(self, net):
        return [(c.ref, k) for c in self.comps for k, v in c.nets.items() if v == net]

    def _use(self, lib_id):
        if lib_id not in self.used_libs:
            node = list(lib_symbol(lib_id))
            node[1] = lib_id
            self.used_libs[lib_id] = node

    def _wire(self, x1, y1, x2, y2):
        self.items.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
                          % (r2(x1), r2(y1), r2(x2), r2(y2), q(uid(self.project, 'w', x1, y1, x2, y2))))

    def _label(self, net, x, y, d):
        just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[d]
        self.items.append('(label %s (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
                          % (q(net), r2(x), r2(y), d, just, q(uid(self.project, 'lbl', net, x, y))))

    def power(self, net, x, y, rot=None, flag=False):
        lib_id = 'power:PWR_FLAG' if flag else POWER[net]
        self._use(lib_id)
        if rot is None:
            rot = 0
        self.pwr_n += 1
        ref = ('#FLG%02d' if flag else '#PWR%02d') % self.pwr_n
        value = 'PWR_FLAG' if flag else net
        u = uid(self.project, 'pwr', ref)
        ty = y + (-3.2 if (net != 'GND' or flag) == (rot == 0) else 3.2)
        self.items.append('\n'.join([
            '(symbol (lib_id %s) (at %s %s %d) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid %s)'
            % (q(lib_id), r2(x), r2(y), rot, q(u)),
            '(property "Reference" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (q(ref), r2(x), r2(y)),
            '(property "Value" %s (at %s %s 0) (effects (font (size 1.27 1.27))))' % (q(value), r2(x), r2(ty)),
            '(property "Footprint" "" (at %s %s 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (r2(x), r2(y)),
            '(property "Datasheet" "" (at %s %s 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (r2(x), r2(y)),
            '(pin "1" (uuid %s))' % q(uid(u, 'p1')),
            '(instances (project %s (path %s (reference %s) (unit 1))))' % (q(self.project), q('/' + self.root), q(ref)),
            ')']))

    def flag(self, net, x, y):
        """PWR_FLAG plus matching power symbol at grid point (x, y)."""
        X, Y = x * G, y * G
        if net == 'GND':
            self.power('GND', X, Y)
            self.power(net, X, Y, 0, flag=True)
        else:
            self.power(net, X, Y)
            self.power(net, X, Y, 180, flag=True)

    def pwr(self, net, gx, gy, rot=0):
        self.power(net, gx * G, gy * G, rot)

    def label(self, net, gx, gy, ang=0):
        self._label(net, gx * G, gy * G, ang)

    def _attach(self, net, px, py, d, side=False):
        dx, dy = DIRV[d]
        if net in POWER:
            natural = 270 if net == 'GND' else 90
            if side and d in (0, 180):
                ex = px + dx * G
                self._wire(px, py, ex, py)
                self.power(net, ex, py, (d - natural) % 360)
                return
            if d == natural:
                self.power(net, px, py)
                return
            if d in (0, 180):
                ex, ey = px + dx * G, py
                self._wire(px, py, ex, ey)
                self.power(net, ex, ey)
                return
            ex, ey = px, py + dy * G
            self._wire(px, py, ex, ey)
            self.power(net, ex, ey, 180)
            return
        ex, ey = px + dx * G, py + dy * G
        self._wire(px, py, ex, ey)
        self._label(net, ex, ey, d)

    def _symbol_inst(self, c):
        self._use(c.lib_id)
        u = uid(self.project, 'sym', c.ref)
        c.uuid = u
        pins = pins_of(c.lib_id)
        xs, ys = [], []
        for p in pins:
            ox, oy = xform(p['x'], p['y'], c.rot, c.mirror)
            px, py = c.x + ox, c.y + oy
            xs.append(px)
            ys.append(py)
            if (c.ref, p['num']) in self.wired:
                pass
            elif p['num'] in c.nets:
                net = c.nets[p['num']]
                d = out_dir(p['ang'], c.rot, c.mirror)
                if net is None:
                    self.items.append('(no_connect (at %s %s) (uuid %s))' % (r2(px), r2(py), q(uid(u, 'nc', p['num']))))
                else:
                    self._attach(net, px, py, d, c.power_side)
            elif p['type'] != 'no_connect':
                raise ValueError('%s pin %s (%s) has no net' % (c.ref, p['num'], p['name']))
        for k in c.nets:
            if k not in [p['num'] for p in pins]:
                raise ValueError('%s has no pin %s' % (c.ref, k))
        if not xs:
            xs, ys = [c.x], [c.y]
        two_pin = len(pins) == 2 and c.lib_id.startswith('Device:')
        vertical = two_pin and abs(xs[0] - xs[1]) < 0.1
        if c.ref_pos:
            rx, ry, vx, vy, jr = c.ref_pos[0] * G, c.ref_pos[1] * G, c.ref_pos[2] * G, c.ref_pos[3] * G, 'left'
        elif vertical:
            rx, ry, vx, vy, jr = c.x + 1.6, c.y - 1.0, c.x + 1.6, c.y + 1.6, 'left'
        elif two_pin:
            rx, ry, vx, vy, jr = c.x, c.y - 2.4, c.x, c.y + 3.0, None
        else:
            top, bot = min(ys), max(ys)
            if not pins:
                top, bot = c.y - 3, c.y + 3
            rx, ry, vx, vy, jr = c.x, top - 1.8, c.x, bot + 2.4, None
        if c.mirror and jr:
            jr = {'left': 'right', 'right': 'left'}[jr]
        just = ' (justify %s)' % jr if jr else ''
        props = [('Reference', c.ref, rx, ry, False), ('Value', c.value, vx, vy, False),
                 ('Footprint', c.footprint, c.x, c.y, True), ('Datasheet', c.fields.get('Datasheet', ''), c.x, c.y, True)]
        for k, v in c.fields.items():
            if k != 'Datasheet':
                props.append((k, v, c.x, c.y, True))
        lines = ['(symbol (lib_id %s) (at %s %s %d)%s (unit 1) (exclude_from_sim no) (in_bom %s) (on_board yes) (dnp no) (uuid %s)'
                 % (q(c.lib_id), r2(c.x), r2(c.y), c.rot, ' (mirror y)' if c.mirror else '',
                    'yes' if c.in_bom else 'no', q(u))]
        for k, v, x, y, hide in props:
            lines.append('(property %s %s (at %s %s %d) (effects (font (size 1.27 1.27))%s%s))'
                         % (q(k), q(v), r2(x), r2(y), c.rot if c.rot in (90, 270) else 0, '' if hide else just, ' (hide yes)' if hide else ''))
        for p in pins:
            lines.append('(pin %s (uuid %s))' % (q(p['num']), q(uid(u, 'pin', p['num']))))
        lines.append('(instances (project %s (path %s (reference %s) (unit 1))))'
                     % (q(self.project), q('/' + self.root), q(c.ref)))
        lines.append(')')
        self.items.append('\n'.join(lines))

    def netlist(self):
        """{net: [(ref, pin)]} from the component data."""
        nets = {}
        for c in self.comps:
            for pin, net in c.nets.items():
                if net is not None:
                    nets.setdefault(net, []).append((c.ref, pin))
        return nets

    def write(self, path):
        for c in self.comps:
            self._symbol_inst(c)
        self._draw_paths()
        libs = '\n'.join(dump(n, 1) for n in self.used_libs.values())
        tb = ['(title %s)' % q(self.title), '(date "2026-10-13")', '(rev %s)' % q(self.rev),
              '(company "AIsonic 超声波探鱼器")']
        for i, cm in enumerate(self.comments):
            tb.append('(comment %d %s)' % (i + 1, q(cm)))
        txt = '\n'.join([
            '(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")',
            '(uuid %s)' % q(self.root),
            '(paper %s)' % q(self.paper),
            '(title_block %s)' % ' '.join(tb),
            '(lib_symbols\n%s\n)' % libs,
        ] + self.items + [
            '(sheet_instances (path "/" (page "1")))',
            '(embedded_fonts no)',
            ')'])
        parse(txt)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt + '\n')

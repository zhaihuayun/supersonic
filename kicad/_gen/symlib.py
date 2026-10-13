"""Project symbol library (AIsonic.kicad_sym) and custom footprints (AIsonic.pretty)."""
import os

from sexp import parse

FONT = '(effects (font (size 1.27 1.27)))'
HIDE = '(effects (font (size 1.27 1.27)) (hide yes))'


def _prop(key, val, x, y, hide=False, justify=None):
    eff = '(effects (font (size 1.27 1.27))%s%s)' % (
        ' (justify %s)' % justify if justify else '', ' (hide yes)' if hide else '')
    return '(property "%s" "%s" (at %.2f %.2f 0) %s)' % (key, val, x, y, eff)


def _pin(etype, x, y, ang, length, name, num, hide=False):
    return ('(pin %s line (at %.2f %.2f %d) (length %.2f)%s (name "%s" %s) (number "%s" %s))'
            % (etype, x, y, ang, length, ' (hide yes)' if hide else '', name, FONT, num, FONT))


def _symbol(name, ref, value, fp, desc, graphics, pins, ref_at, val_at, kw='', hide_names=False):
    return '\n'.join([
        '(symbol "%s" (pin_names (offset 1.016)%s) (exclude_from_sim no) (in_bom yes) (on_board yes)'
        % (name, ' (hide yes)' if hide_names else ''),
        _prop('Reference', ref, *ref_at, justify='left'),
        _prop('Value', value, *val_at, justify='left'),
        _prop('Footprint', fp, 0, 0, hide=True),
        _prop('Datasheet', '', 0, 0, hide=True),
        _prop('Description', desc, 0, 0, hide=True),
        _prop('ki_keywords', kw, 0, 0, hide=True),
        '(symbol "%s_0_1" %s)' % (name, ' '.join(graphics)),
        '(symbol "%s_1_1" %s)' % (name, ' '.join(pins)),
        ')'])


def _rect(x1, y1, x2, y2):
    return ('(rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) '
            '(fill (type background)))' % (x1, y1, x2, y2))


def _poly(pts, fill='background', width=0.254):
    p = ' '.join('(xy %.2f %.2f)' % xy for xy in pts)
    return '(polyline (pts %s) (stroke (width %.3f) (type default)) (fill (type %s)))' % (p, width, fill)


def _circle(x, y, r, fill='outline'):
    return ('(circle (center %.2f %.2f) (radius %.3f) (stroke (width 0.254) (type default)) '
            '(fill (type %s)))' % (x, y, r, fill))


def _arc(sx, sy, mx, my, ex, ey):
    return ('(arc (start %.2f %.2f) (mid %.2f %.2f) (end %.2f %.2f) '
            '(stroke (width 0.254) (type default)) (fill (type none)))' % (sx, sy, mx, my, ex, ey))


def _text(t, x, y, size=1.27):
    return '(text "%s" (at %.2f %.2f 0) (effects (font (size %.2f %.2f))))' % (t, x, y, size, size)


def opa320(inv_top=False):
    sp, sn = (-2.54, 2.54) if inv_top else (2.54, -2.54)
    g = [_poly([(-5.08, 5.08), (5.08, 0), (-5.08, -5.08), (-5.08, 5.08)]),
         _text('+', -3.81, sp), _text('-', -3.81, sn)]
    p = [_pin('input', -7.62, sp, 0, 2.54, '~', '3'),
         _pin('input', -7.62, sn, 0, 2.54, '~', '4'),
         _pin('output', 7.62, 0, 180, 2.54, '~', '1'),
         _pin('power_in', -2.54, 7.62, 270, 3.81, 'V+', '5'),
         _pin('power_in', -2.54, -7.62, 90, 3.81, 'V-', '2')]
    return _symbol('OPA320xDBV_N' if inv_top else 'OPA320xDBV', 'U', 'OPA320AIDBVT', 'Package_TO_SOT_SMD:SOT-23-5',
                   'Precision 20MHz rail-to-rail CMOS op-amp, SOT-23-5 (TI OPA320 DBV pinout)',
                   g, p, (1.27, 6.35), (1.27, -6.35), 'opamp low noise')


def ad8338():
    left = [('1', 'INPR', 'input', 5.08), ('2', 'INPD', 'input', 2.54), ('3', 'INMD', 'input', 0),
            ('4', 'INMR', 'input', -2.54), ('7', 'GAIN', 'input', -7.62)]
    right = [('11', 'OUTP', 'output', 5.08), ('10', 'OUTM', 'output', 2.54), ('12', 'FBKP', 'passive', 0),
             ('9', 'FBKM', 'passive', -2.54), ('13', 'VAGC', 'input', -5.08), ('16', 'VREF', 'output', -7.62),
             ('14', 'OFSN', 'passive', -10.16)]
    pins = [_pin(t, -15.24, y, 0, 2.54, nm, n) for n, nm, t, y in left]
    pins += [_pin(t, 15.24, y, 180, 2.54, nm, n) for n, nm, t, y in right]
    pins += [_pin('power_in', -5.08, 12.7, 270, 5.08, 'VBAT', '15'),
             _pin('input', 5.08, 12.7, 270, 5.08, 'MODE', '6'),
             _pin('power_in', -5.08, -17.78, 90, 5.08, 'COMM', '5'),
             _pin('passive', 0, -17.78, 90, 5.08, 'EP', '17'),
             _pin('passive', 5.08, -17.78, 90, 5.08, 'DETO', '8')]
    g = [_rect(-12.7, 7.62, 12.7, -12.7)]
    return _symbol('AD8338', 'U', 'AD8338ACPZ', 'Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm',
                   'Low power 18MHz VGA, 0-80dB linear-in-dB gain, LFCSP-16 3x3 (CP-16-22)',
                   g, pins, (7.62, 10.16), (-12.7, -20.32), 'VGA AGC ultrasound')


def ee19():
    g = [_rect(-7.62, 7.62, 7.62, -7.62),
         _poly([(-0.64, 6.35), (-0.64, -6.35)], fill='none'),
         _poly([(0.64, 6.35), (0.64, -6.35)], fill='none')]
    for i in range(4):
        y = 5.08 - i * 2.54
        g.append(_arc(-3.81, y, -2.54, y - 1.27, -3.81, y - 2.54))
    for i in range(4):
        y = 5.08 - i * 2.54
        g.append(_arc(3.81, y, 2.54, y - 1.27, 3.81, y - 2.54))
    g += [_poly([(-3.81, 5.08), (-6.35, 5.08), (-6.35, 5.08)], fill='none'),
          _poly([(-3.81, -5.08), (-6.35, -5.08)], fill='none'),
          _poly([(3.81, 5.08), (6.35, 5.08)], fill='none'),
          _poly([(3.81, -5.08), (6.35, -5.08)], fill='none'),
          _circle(-5.08, 6.35, 0.4, 'outline'), _circle(5.08, 6.35, 0.4, 'outline'),
          _text('10T', -4.6, 0, 1.0), _text('80T', 4.6, 0, 1.0)]
    p = [_pin('passive', -10.16, 5.08, 0, 2.54, 'P1', '1'),
         _pin('passive', -10.16, -5.08, 0, 2.54, 'P2', '3'),
         _pin('passive', 10.16, 5.08, 180, 2.54, 'S1', '6'),
         _pin('passive', 10.16, -5.08, 180, 2.54, 'S2', '10')]
    for i, n in enumerate(['2', '4', '5', '7', '8', '9']):
        p.append(_pin('no_connect', -6.35 + i * 2.54, -7.62, 90, 0, 'NC', n, hide=True))
    return _symbol('EE19_1to8', 'T', 'EE19 1:8 (10T:80T)', 'AIsonic:EE19_5+5_Vertical',
                   'EE19 bobbin pulse transformer, primary 10T pins 1-3, secondary 80T pins 6-10',
                   g, p, (-7.62, 10.16), (-7.62, -10.16), 'transformer EE19', hide_names=True)


CUSTOM = {'OPA320xDBV': opa320, 'OPA320xDBV_N': lambda: opa320(True), 'AD8338': ad8338, 'EE19_1to8': ee19}


def write_symbol_lib(path):
    body = '\n'.join(f() for f in CUSTOM.values())
    txt = ('(kicad_symbol_lib (version 20241209) (generator "aisonic_gen") (generator_version "9.0")\n'
           + body + '\n)\n')
    parse(txt)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)


def custom_symbol_nodes():
    return {name: parse(f()) for name, f in CUSTOM.items()}


def write_ee19_footprint(pretty_dir):
    """EE19 vertical bobbin, 5+5 pins, pitch 3.81 mm, row spacing 15.24 mm (verify against bobbin)."""
    os.makedirs(pretty_dir, exist_ok=True)
    pitch, row = 3.81, 15.24
    pads = []
    for i in range(5):
        x = (i - 2) * pitch
        shape = 'rect' if i == 0 else 'circle'
        pads.append('(pad "%d" thru_hole %s (at %.3f %.3f) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask"))'
                    % (i + 1, shape, x, -row / 2))
    for i in range(5):
        x = (2 - i) * pitch
        pads.append('(pad "%d" thru_hole circle (at %.3f %.3f) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask"))'
                    % (i + 6, x, row / 2))
    bw, bh = 21.0, 20.0
    txt = '\n'.join([
        '(footprint "EE19_5+5_Vertical" (version 20241229) (generator "aisonic_gen") (layer "F.Cu")',
        '(descr "EE19 vertical bobbin 5+5 pins, pitch 3.81mm, rows 15.24mm. Primary 1-3, secondary 6-10")',
        '(tags "EE19 transformer")',
        '(property "Reference" "REF**" (at 0 -12 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        '(property "Value" "EE19" (at 0 12 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        '(attr through_hole)',
        '(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))'
        % (-bw / 2, -bh / 2, bw / 2, bh / 2),
        '(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))'
        % (-bw / 2, -bh / 2, bw / 2, bh / 2),
        '(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))'
        % (-bw / 2 - 0.5, -bh / 2 - 0.5, bw / 2 + 0.5, bh / 2 + 0.5),
        '(fp_circle (center %.2f %.2f) (end %.2f %.2f) (stroke (width 0.3) (type solid)) (fill yes) (layer "F.SilkS"))'
        % (-2 * pitch - 2.2, -row / 2 + 2.2, -2 * pitch - 1.8, -row / 2 + 2.2),
        '(fp_text user "PRI" (at 0 -4 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        '(fp_text user "SEC HV" (at 0 4 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
    ] + pads + [')'])
    with open(os.path.join(pretty_dir, 'EE19_5+5_Vertical.kicad_mod'), 'w') as f:
        f.write(txt + '\n')

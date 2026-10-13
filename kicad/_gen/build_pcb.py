"""Build, autoroute (Freerouting) and verify the PCB for a design module.

Usage: python3 build_pcb.py design_tx [--no-route]
"""
import importlib
import json
import os
import subprocess
import sys

import pcbnew

import build_sch
import schgen
import sexp

STD_FP = '/usr/share/kicad/footprints/'
FREEROUTING = os.environ.get('FREEROUTING_JAR', '/tmp/freerouting.jar')
ORIGIN = (100.0, 100.0)


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(ORIGIN[0] + x), pcbnew.FromMM(ORIGIN[1] + y))


def load_fp(proj_dir, fpid):
    lib, name = fpid.split(':')
    path = os.path.join(proj_dir, 'AIsonic.pretty') if lib == 'AIsonic' else STD_FP + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise KeyError(fpid)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def add_outline(board, w, h, r=2.0):
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(mm(*a))
        s.SetEnd(mm(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)

    def arc(c, start, mid):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(mm(*start), mm(*mid), mm(*c))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)

    k = r * (1 - 0.70710678)
    seg((r, 0), (w - r, 0))
    seg((w, r), (w, h - r))
    seg((w - r, h), (r, h))
    seg((0, h - r), (0, r))
    arc((w, r), (w - r, 0), (w - k, k))
    arc((w - r, h), (w, h - r), (w - k, h - k))
    arc((0, h - r), (r, h), (k, h - k))
    arc((r, 0), (0, r), (k, k))


def add_zone(board, net, layer, w, h, inset=0.0, priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.3))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
    z.SetIsFilled(False)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(inset, inset), (w - inset, inset), (w - inset, h - inset), (inset, h - inset)]:
        ol.Append(mm(x, y))
    board.Add(z)
    return z


def add_text(board, x, y, txt, size, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(mm(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(size * 0.15))
    board.Add(t)


def build_board(mod, sch, d):
    pcb_path = os.path.join(d, mod.PROJECT + '.kicad_pcb')
    if os.path.exists(pcb_path):
        os.remove(pcb_path)
    board = pcbnew.NewBoard(pcb_path)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)

    nets = {}
    for name in sorted({n for c in sch.comps for n in c.nets.values() if n}):
        ni = pcbnew.NETINFO_ITEM(board, build_sch.pcb_net(name))
        board.Add(ni)
        nets[name] = ni
    nc = {}
    for c in sch.comps:
        for p in schgen.pins_of(c.lib_id):
            if p['type'] == 'no_connect' or (p['num'] in c.nets and c.nets[p['num']] is None):
                name = 'unconnected-(%s-%s-Pad%s)' % (c.ref, p['name'], p['num'])
                ni = pcbnew.NETINFO_ITEM(board, name)
                board.Add(ni)
                nc[(c.ref, p['num'])] = ni

    for c in sch.comps:
        if c.ref not in mod.PLACE:
            raise KeyError('no PCB placement for ' + c.ref)
        fp = load_fp(d, c.footprint)
        fp.SetReference(c.ref)
        fp.SetValue(c.value)
        fp.SetPath(pcbnew.KIID_PATH('/' + c.uuid))
        fp.SetSheetname('Root')
        fp.SetSheetfile(mod.PROJECT + '.kicad_sch')
        for k in ('LCSC', 'MPN'):
            if k in c.fields:
                f = pcbnew.PCB_FIELD(fp, fp.GetNextFieldId() if hasattr(fp, 'GetNextFieldId') else 0, k)
                f.SetText(c.fields[k])
                f.SetVisible(False)
                f.SetLayer(pcbnew.F_Fab)
                fp.AddField(f)
        x, y, rot = mod.PLACE[c.ref]
        board.Add(fp)
        fp.SetPosition(mm(x, y))
        fp.SetOrientationDegrees(rot)
        ref = fp.Reference()
        ref.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.9), pcbnew.FromMM(0.9)))
        ref.SetTextThickness(pcbnew.FromMM(0.15))
        if c.ref.startswith('H'):
            ref.SetVisible(False)
        if c.ref in getattr(mod, 'REF_AT', {}):
            rx, ry, ra = mod.REF_AT[c.ref]
            ref.SetPosition(mm(rx, ry))
            ref.SetTextAngleDegrees(ra)
        for pad in fp.Pads():
            num = pad.GetNumber()
            net = c.nets.get(num)
            if net:
                pad.SetNet(nets[net])
            elif (c.ref, num) in nc:
                pad.SetNet(nc[(c.ref, num)])
        missing = set(k for k, v in c.nets.items() if v) - set(p.GetNumber() for p in fp.Pads())
        if missing:
            raise ValueError('%s footprint lacks pads %s' % (c.ref, missing))

    for x, y, dia, drill in getattr(mod, 'EXTRA_VIAS', []):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(mm(x, y))
        v.SetWidth(pcbnew.FromMM(dia))
        v.SetDrill(pcbnew.FromMM(drill))
        v.SetNet(nets['GND'])
        board.Add(v)
    for net, width, pts in getattr(mod, 'EXTRA_TRACKS', []):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(mm(x0, y0))
            t.SetEnd(mm(x1, y1))
            t.SetWidth(pcbnew.FromMM(width))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(nets[net])
            board.Add(t)
    w, h = mod.BOARD
    add_outline(board, w, h)
    for x, y, txt, size in mod.SILK:
        add_text(board, x, y, txt, size)
    add_zone(board, nets['GND'], pcbnew.B_Cu, w, h, 0.0)
    add_zone(board, nets['GND'], pcbnew.F_Cu, w, h, 0.0)
    for keepout in getattr(mod, 'KEEPOUT', []):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetLayerSet(pcbnew.LSET.AllCuMask())
        ol = z.Outline()
        ol.NewOutline()
        x1, y1, x2, y2 = keepout
        for x, y in [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]:
            ol.Append(mm(x, y))
        board.Add(z)
    board.Save(pcb_path)
    return pcb_path


def route(pcb_path, d, passes=40):
    board = pcbnew.LoadBoard(pcb_path)
    dsn = os.path.join(d, 'output', 'route.dsn')
    ses = os.path.join(d, 'output', 'route.ses')
    if os.path.exists(ses):
        os.remove(ses)
    assert pcbnew.ExportSpecctraDSN(board, dsn)
    cmd = ['java', '-jar', FREEROUTING, '-de', dsn, '-do', ses, '-mp', str(passes), '-mt', '1',
           '--gui.enabled=false']
    print('routing:', ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if not os.path.exists(ses):
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise RuntimeError('freerouting failed')
    board = pcbnew.LoadBoard(pcb_path)
    assert pcbnew.ImportSpecctraSES(board, ses)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(pcb_path)
    for f in (dsn, ses):
        os.remove(f)
    for f in os.listdir(d):
        if f.endswith('.log') or f == 'freerouting.json':
            os.remove(os.path.join(d, f))


def stitch(pcb_path, d, w, h, clearances, pitch=5.0):
    """GND stitching vias on a grid, keeping clear of copper, courtyards and board edge."""
    board = pcbnew.LoadBoard(pcb_path)
    gnd = board.FindNet('GND')
    items = list(board.GetPads()) + [t for t in board.GetTracks()]
    boxes = []
    for fp in board.GetFootprints():
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False)
        bb.Inflate(pcbnew.FromMM(0.3))
        boxes.append(bb)
    n = 0
    y = pitch / 2
    while y < h:
        x = pitch / 2
        while x < w:
            if 1.5 < x < w - 1.5 and 1.5 < y < h - 1.5:
                pos = mm(x, y)
                ok = not any(bb.Contains(pos) for bb in boxes)
                if ok:
                    for it in items:
                        cl = max(clearances.get(it.GetNetname(), 0.3), 0.3)
                        margin = pcbnew.FromMM(0.35 + cl + 0.1)
                        if it.HitTest(pos, margin):
                            ok = False
                            break
                if ok:
                    v = pcbnew.PCB_VIA(board)
                    v.SetPosition(pos)
                    v.SetWidth(pcbnew.FromMM(0.7))
                    v.SetDrill(pcbnew.FromMM(0.35))
                    v.SetNet(gnd)
                    board.Add(v)
                    n += 1
            x += pitch
        y += pitch
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    for _ in range(4):
        added = _island_vias(board, gnd, items, clearances)
        n += added
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        if not added:
            break
    board.Save(pcb_path)
    return n


def _island_vias(board, gnd, items, clearances):
    anchors = [v.GetPosition() for v in board.GetTracks() if v.Type() == pcbnew.PCB_VIA_T and v.GetNetCode() == gnd.GetNetCode()]
    anchors += [p.GetPosition() for p in board.GetPads()
                if p.GetNetCode() == gnd.GetNetCode() and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    items = list(board.GetPads()) + list(board.GetTracks())
    added = 0
    for z in board.Zones():
        if z.GetNetCode() != gnd.GetNetCode() or z.GetLayer() != pcbnew.F_Cu:
            continue
        polys = z.GetFilledPolysList(pcbnew.F_Cu)
        for i in range(polys.OutlineCount()):
            outline = polys.Outline(i)
            if any(outline.PointInside(a) for a in anchors):
                continue
            bb = outline.BBox()
            step = pcbnew.FromMM(0.25)
            r = pcbnew.FromMM(0.45)
            found = None
            y = bb.GetTop()
            while y <= bb.GetBottom() and not found:
                x = bb.GetLeft()
                while x <= bb.GetRight():
                    pt = pcbnew.VECTOR2I(x, y)
                    ring = [pcbnew.VECTOR2I(x + dx, y + dy) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))]
                    if outline.PointInside(pt) and all(outline.PointInside(q) for q in ring):
                        clear = True
                        for it in items:
                            if it.GetNetCode() == gnd.GetNetCode():
                                continue
                            cl = max(clearances.get(it.GetNetname(), 0.2), 0.2)
                            if it.HitTest(pt, pcbnew.FromMM(0.35 + cl + 0.05)):
                                clear = False
                                break
                        if clear:
                            found = pt
                            break
                    x += step
                y += step
            if found:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(found)
                v.SetWidth(pcbnew.FromMM(0.7))
                v.SetDrill(pcbnew.FromMM(0.35))
                v.SetNet(gnd)
                board.Add(v)
                anchors.append(found)
                added += 1
    return added


def drop_floating_vias(board):
    """Remove GND vias whose copper islands are not tied to the main GND plane."""
    gnd = next(p.GetNetCode() for p in board.GetPads() if p.GetNetname() == 'GND')
    isl = []
    for z in board.Zones():
        if z.GetNetCode() != gnd:
            continue
        layer = z.GetLayer()
        polys = z.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            isl.append((layer, polys.Outline(i)))
    parent = list(range(len(isl)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def where(pos, layer):
        return [k for k, (l, o) in enumerate(isl) if l == layer and o.PointInside(pos)]

    vias = [v for v in board.GetTracks() if v.Type() == pcbnew.PCB_VIA_T and v.GetNetCode() == gnd]
    pads = [p for p in board.GetPads() if p.GetNetCode() == gnd]
    links = [(v, where(v.GetPosition(), pcbnew.F_Cu) + where(v.GetPosition(), pcbnew.B_Cu)) for v in vias]
    for p in pads:
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            links.append((p, where(p.GetPosition(), pcbnew.F_Cu) + where(p.GetPosition(), pcbnew.B_Cu)))
    for _, ks in links:
        for k in ks[1:]:
            parent[find(k)] = find(ks[0])
    score = {}
    for p in pads:
        for k in where(p.GetPosition(), pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu):
            score[find(k)] = score.get(find(k), 0) + 1
    if not score:
        return 0
    main = max(score, key=score.get)
    return {v.m_Uuid.AsString() for v, ks in links
            if v.Type() == pcbnew.PCB_VIA_T and (not ks or all(find(k) != main for k in ks))}


def _delete_items(pcb_path, uuids):
    """Delete top-level tracks/vias by uuid in the file (BOARD.Remove corrupts SWIG state here)."""
    if not uuids:
        return 0
    tree = sexp.parse(open(pcb_path, encoding='utf-8').read())
    keep, n = [], 0
    for node in tree:
        u = sexp.find1(node, 'uuid') if isinstance(node, list) and node[0] in ('segment', 'arc', 'via') else None
        if u is not None and u[1] in uuids:
            n += 1
            continue
        keep.append(node)
    open(pcb_path, 'w', encoding='utf-8').write(sexp.dump(keep) + '\n')
    return n


def prune_vias(pcb_path, d):
    """Remove stitching vias that DRC flags (dangling or clearance)."""
    rpt = os.path.join(d, 'output', 'drc_tmp.json')
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--format', 'json', '-o', rpt, pcb_path],
                   capture_output=True)
    data = json.load(open(rpt))
    os.remove(rpt)
    bad = set()
    for v in data.get('violations', []):
        for it in v.get('items', []):
            desc = it['description']
            if desc.startswith('Via') and '[GND]' in desc:
                bad.add(it['uuid'])
            if v['type'] == 'track_dangling' and desc.startswith('Track') and 'length 0.0' in desc:
                bad.add(it['uuid'])
    n = _delete_items(pcb_path, bad)
    for _ in range(3):
        board = pcbnew.LoadBoard(pcb_path)
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        k = _delete_items(pcb_path, drop_floating_vias(board))
        n += k
        if not k:
            break
    fill_only(pcb_path)
    return n


def unrouted(pcb_path, d):
    rpt = os.path.join(d, 'output', 'drc_tmp.json')
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', rpt, pcb_path], capture_output=True)
    data = json.load(open(rpt))
    os.remove(rpt)
    return [v for v in data.get('unconnected_items', [])
            if not all(i['description'].startswith('Zone') for i in v['items'])]


def fill_only(pcb_path):
    board = pcbnew.LoadBoard(pcb_path)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(pcb_path)


def drc(pcb_path, d):
    rpt = os.path.join(d, 'output', 'drc.json')
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--schematic-parity', '--severity-all', '--format', 'json',
                    '-o', rpt, pcb_path], capture_output=True)
    data = json.load(open(rpt))
    summary = {}
    for key in ('violations', 'unconnected_items', 'schematic_parity'):
        for v in data.get(key, []):
            summary.setdefault((key, v['severity'], v['type']), []).append(v['description'] + ' | ' + ' / '.join(
                i['description'] for i in v.get('items', [])))
    for k, v in sorted(summary.items()):
        print(k, len(v))
        for line in v[:6]:
            print('    ', line)
    return data


def main(modname, do_route=True):
    mod = importlib.import_module(modname)
    d = build_sch.project_dir(mod)
    sch, bad = build_sch.main(modname)
    if bad:
        raise SystemExit('schematic netlist mismatch')
    pcb_path = build_board(mod, sch, d)
    if do_route:
        for attempt in range(4):
            route(pcb_path, d)
            if not unrouted(pcb_path, d):
                break
            print('unrouted signals left, retrying (%d)' % (attempt + 1))
            pcb_path = build_board(mod, sch, d)
        print('stitching vias:', stitch(pcb_path, d, *mod.BOARD, {build_sch.pcb_net(n): v['clearance'] for v in mod.NETCLASSES.values() for n in v['nets']},
                                       getattr(mod, 'STITCH_PITCH', 5.0)), 'pruned:', prune_vias(pcb_path, d))
    else:
        fill_only(pcb_path)
    drc(pcb_path, d)


if __name__ == '__main__':
    main(sys.argv[1], '--no-route' not in sys.argv)

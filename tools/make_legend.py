"""Build the Mill_Legend layer (User.1): component outlines, polarity marks, references and terminal labels,
kept clear of all top copper so a shallow V-bit engrave never cuts a track or pad.

Usage (KiCad's own Python, which has pcbnew; shapely comes from KiCad's 3rd-party site-packages):
    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/make_legend.py texecom-power-reset.kicad_pcb

Close the board in KiCad first. The script renames User.1 to Mill_Legend, deletes whatever is on it and
rebuilds the legend, so rerun it after any layout change. Outlines are clipped wherever they come near top copper;
texts are placed whole at the first clear candidate spot (PREFERRED lists hand-picked spots for crowded areas).
Then export the layer:  kicad-cli pcb export gerbers --layers User.1 ...
"""
import math
import sys
sys.path.append('C:/Users/Johan/Documents/KiCad/10.0/3rdparty/Python311/site-packages')
import pcbnew
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

PCB = sys.argv[1]
S = 1e6
LAYER = pcbnew.User_1
LINE_W = 0.15          # engraved line width (V-bit at shallow depth)
MARGIN = 0.35          # clearance from any top copper / hole to the engrave centreline edge
EDGE_INSET = 1.0       # keep legend this far inside the board edge
MIN_PIECE = 0.8        # drop clipped fragments shorter than this
TXT_H = 1.2            # reference text height
LBL_H = 1.5            # terminal label height
TXT_T = 0.15

# hand-picked first-choice spots for crowded areas (x, y, angle); tried before the automatic search
PREFERRED = {  # (x, y, angle, text height)
    'C4': [(135.0, 125.5, 0, 1.0), (135.0, 125.3, 0, 1.0), (135.0, 125.7, 0, 1.0), (135.0, 125.5, 0, 0.9)],
    'R13': [(135.0, 129.0, 0, 1.0), (135.0, 129.0, 0, 0.9)],
}
TERMINAL_LABELS = {'J1': 'BAT IN', 'J2': 'BAT OUT', 'J3': 'AC IN', 'J4': 'AC OUT'}
PIN_MARKS = {('J1', '1'): '+', ('J1', '2'): '-', ('J2', '1'): '+', ('J2', '2'): '-'}

b = pcbnew.LoadBoard(PCB)
b.SetLayerName(LAYER, 'Mill_Legend')
ls = b.GetEnabledLayers()
ls.AddLayer(LAYER)
b.SetEnabledLayers(ls)

# remove previous legend
for d in [d for d in b.GetDrawings() if d.GetLayer() == LAYER]:
    b.Remove(d)


def xy(v):
    return (v.x / S, v.y / S)


def sps_polys(sps):
    out = []
    for i in range(sps.OutlineCount()):
        o = sps.Outline(i)
        outer = [xy(o.CPoint(k)) for k in range(o.PointCount())]
        holes = []
        for j in range(sps.HoleCount(i)):
            h = sps.Hole(i, j)
            holes.append([xy(h.CPoint(k)) for k in range(h.PointCount())])
        if len(outer) >= 3:
            out.append(Polygon(outer, holes).buffer(0))
    return out


# ---- obstacles: everything on the top copper plus every hole ----
obst = []
for p in b.GetPads():
    if p.IsOnLayer(pcbnew.F_Cu):
        sps = pcbnew.SHAPE_POLY_SET()
        p.TransformShapeToPolygon(sps, pcbnew.F_Cu, 0, 5000, pcbnew.ERROR_OUTSIDE)
        obst += sps_polys(sps)
    if p.GetDrillSize().x > 0:
        obst.append(Point(xy(p.GetPosition())).buffer(max(p.GetDrillSize().x, p.GetDrillSize().y) / 2 / S))
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        obst.append(Point(xy(t.GetPosition())).buffer(t.GetWidth(pcbnew.F_Cu) / 2 / S))
    elif t.GetLayer() == pcbnew.F_Cu:
        obst.append(LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(t.GetWidth() / 2 / S))
for z in b.Zones():
    if not z.GetIsRuleArea() and z.IsOnLayer(pcbnew.F_Cu):
        obst += sps_polys(z.GetFilledPolysList(pcbnew.F_Cu))
blocked = unary_union(obst).buffer(MARGIN + LINE_W / 2)

bb = b.GetBoardEdgesBoundingBox()
inside = box(bb.GetX() / S + EDGE_INSET, bb.GetY() / S + EDGE_INSET,
             bb.GetRight() / S - EDGE_INSET, bb.GetBottom() / S - EDGE_INSET)
allowed = inside.difference(blocked)


# ---- outlines ----
def arc_pts(c, r, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0) * r / 0.3))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def shape_lines(g):
    st = g.GetShape()
    if st == pcbnew.SHAPE_T_SEGMENT:
        return [[xy(g.GetStart()), xy(g.GetEnd())]]
    if st == pcbnew.SHAPE_T_RECTANGLE:
        c = [xy(v) for v in g.GetRectCorners()]
        return [c + [c[0]]]
    if st == pcbnew.SHAPE_T_CIRCLE:
        c = xy(g.GetCenter())
        return [arc_pts(c, g.GetRadius() / S, 0, 2 * math.pi, 64)]
    if st == pcbnew.SHAPE_T_ARC:
        c = xy(g.GetCenter())
        s, e = xy(g.GetStart()), xy(g.GetEnd())
        r = math.hypot(s[0] - c[0], s[1] - c[1])
        a0 = math.atan2(s[1] - c[1], s[0] - c[0])
        a1 = math.atan2(e[1] - c[1], e[0] - c[0])
        m = xy(g.GetArcMid())
        am = math.atan2(m[1] - c[1], m[0] - c[0])

        def between(a, lo, hi):  # is a on the ccw sweep lo->hi
            return (a - lo) % (2 * math.pi) <= (hi - lo) % (2 * math.pi)
        if between(am, a0, a1):
            a1 = a0 + (a1 - a0) % (2 * math.pi)
        else:
            a1 = a0 - (a0 - a1) % (2 * math.pi)
        return [arc_pts(c, r, a0, a1)]
    if st == pcbnew.SHAPE_T_POLY:
        out = []
        ps = g.GetPolyShape()
        for i in range(ps.OutlineCount()):
            o = ps.Outline(i)
            pts = [xy(o.CPoint(k)) for k in range(o.PointCount())]
            out.append(pts + [pts[0]])
        return out
    return []


lines = []
fronts = [fp for fp in b.GetFootprints() if not fp.IsFlipped()]
for fp in fronts:
    name = fp.GetFPID().GetLibItemName().wx_str()
    if name.startswith('MountingHole'):
        continue
    src = pcbnew.F_Fab if name.startswith('CP_Radial') else pcbnew.F_SilkS
    for g in fp.GraphicalItems():
        if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() == src:
            lines += shape_lines(g)

kept = []
for pl in lines:
    geom = LineString(pl).intersection(allowed)
    parts = [geom] if geom.geom_type == 'LineString' else list(getattr(geom, 'geoms', []))
    for part in parts:
        if part.geom_type == 'LineString' and part.length >= MIN_PIECE:
            kept.append(list(part.coords))

n_seg = 0
for pl in kept:
    for a, c in zip(pl, pl[1:]):
        if math.hypot(c[0] - a[0], c[1] - a[1]) < 0.01:
            continue
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(c[0]), pcbnew.FromMM(c[1])))
        s.SetWidth(pcbnew.FromMM(LINE_W))
        s.SetLayer(LAYER)
        b.Add(s)
        n_seg += 1

# ---- texts: placed whole at the first clear candidate position ----
placed = []  # shapely footprints of placed texts
outline_geom = unary_union([LineString(pl) for pl in kept]).buffer(0.3) if kept else Polygon()


def make_text(txt, x, y, h, angle):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(txt)
    t.SetLayer(LAYER)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(h), pcbnew.FromMM(h)))
    t.SetTextThickness(pcbnew.FromMM(TXT_T))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetTextAngleDegrees(angle)
    t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    return t


def text_geom(t):
    sps = pcbnew.SHAPE_POLY_SET()
    t.TransformShapeToPolygon(sps, LAYER, 0, 5000, pcbnew.ERROR_OUTSIDE)
    return unary_union(sps_polys(sps))


def try_place(txt, cands, h, avoid_outlines=True, owner=None):
    for (x, y, ang) in cands:
        if owner is not None and any(o is not owner and bx.Contains(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
                                     for o, bx in crt):
            continue
        t = make_text(txt, x, y, h, ang)
        g = text_geom(t)
        if g.is_empty:
            continue
        if not allowed.contains(g):
            continue
        if any(g.buffer(0.3).intersects(p) for p in placed):
            continue
        if avoid_outlines and g.intersects(outline_geom):
            continue
        b.Add(t)
        placed.append(g)
        return (x, y, ang)
    return None


def ring_cands(cx, cy, r, step=0.5, ang=(0, 90)):
    out = []
    for k in range(0, int(r / step) + 1):
        d = k * step
        for dx, dy in ((0, 0), (0, -d), (0, d), (-d, 0), (d, 0), (-d, -d), (d, -d), (-d, d), (d, d)):
            for a in ang:
                out.append((cx + dx, cy + dy, a))
    return out


report = []
crt = [(f, f.GetCourtyard(pcbnew.F_CrtYd).BBox()) for f in fronts if not f.GetReference().startswith('MH')]
# terminal labels first (largest, most important), just above the terminal body
for ref, label in TERMINAL_LABELS.items():
    fp = b.FindFootprintByReference(ref)
    cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    cx = (cy.GetX() + cy.GetRight()) / 2 / S
    top = cy.GetY() / S
    cands = [(cx + dx, top - 1.4 - dy, 0) for dy in (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0) for dx in (0, -1, 1, -2, 2)]
    report.append((label, try_place(label, cands, LBL_H)))
for (ref, pad), mark in PIN_MARKS.items():
    fp = b.FindFootprintByReference(ref)
    p = fp.FindPadByNumber(pad)
    x, y = xy(p.GetPosition())
    report.append(('%s.%s %s' % (ref, pad, mark), try_place(mark, ring_cands(x, y - 3.3, 1.5), LBL_H, avoid_outlines=False)))

# references: body centre first, then just outside the courtyard, then around
for fp in sorted(fronts, key=lambda f: f.GetReference()):
    ref = fp.GetReference()
    if ref.startswith('MH'):
        continue
    cyb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    cx, cy = (cyb.GetX() + cyb.GetRight()) / 2 / S, (cyb.GetY() + cyb.GetBottom()) / 2 / S
    w, h = cyb.GetWidth() / S, cyb.GetHeight() / S
    vert = h > w * 1.4
    a0 = (90, 0) if vert else (0, 90)
    pos = None
    for (px, py, pa, ph) in PREFERRED.get(ref, []):
        pos = try_place(ref, [(px, py, pa)], ph, owner=fp)
        if pos:
            break
    if pos is not None:
        report.append((ref, pos))
        continue
    cands = ring_cands(cx, cy, 1.5, ang=a0)
    for gap in (0.9, 1.4, 2.0):
        cands += [(cx, cyb.GetY() / S - gap, 0), (cx, cyb.GetBottom() / S + gap, 0),
                  (cyb.GetX() / S - gap, cy, 90), (cyb.GetRight() / S + gap, cy, 90)]
    cands += ring_cands(cx, cy, max(w, h) / 2 + 3, step=0.7, ang=a0)
    pos = try_place(ref, cands, TXT_H, owner=fp)
    if pos is None:  # last resort: allow crossing its own outline
        pos = try_place(ref, cands, TXT_H, avoid_outlines=False, owner=fp)
    report.append((ref, pos))

b.Save(PCB)
print('outline pieces', len(kept), 'segments', n_seg)
for r, p in report:
    print('  %-10s %s' % (r, 'NOT PLACED' if p is None else '(%.1f, %.1f) %d deg' % p))

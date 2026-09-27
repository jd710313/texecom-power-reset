"""Assembly drawings for the milled board, at 2:1 on A4 landscape (SVG + PDF):

  top    - the board as seen from the TOP: every top-side part with reference and value, the pads that need a top
           solder joint (ring, as on the engraved legend) and the vias.
  bottom - the board as seen from the BOTTOM (mirrored left-right): the 1206 SMD parts and the vias; through-hole
           parts in grey for orientation.

Vias are numbered the same way on both drawings (reading order as seen from the bottom).

Usage (KiCad's Python):
    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/make_assembly.py texecom-power-reset.kicad_pcb top    docs/pcb-assembly-top.svg
    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/make_assembly.py texecom-power-reset.kicad_pcb bottom docs/pcb-assembly-bottom.svg
The PDF is printed through headless Edge/Chrome (real fonts); MuPDF is the fallback.
"""
import math
import os
import subprocess
import sys
import tempfile
import pcbnew

PCB, SIDE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
assert SIDE in ('top', 'bottom')
TOP = SIDE == 'top'
S = 1e6
SC = 2.0                                  # drawing scale (page mm per board mm)
PAGE_W, PAGE_H = 297.0, 210.0             # A4 landscape
OX, OY = 12.0, 30.0                       # board drawing origin on the page

DESC_BOTTOM = {  # what each bottom part does (short, for the parts table)
    'F1': 'PTC fuse 0.5A, battery feed', 'C5': '10µF X5R, timer ch1 (CEXT)', 'C6': '10µF X5R, timer ch2 (CEXT)',
    'R7': '1k, Q1 base (ch1)', 'R8': '1k, Q2 base (ch2)', 'R9': '1k, GPIO4 series (ch1)', 'R10': '1k, GPIO3 series (ch2)',
    'R11': '100Ω, C5 series', 'R12': '100Ω, C6 series', 'R15': '1k, K1 LED', 'R16': '1k, K2 LED',
}
SHORT_VALUE = {'Pololu S9V11E2F5': 'Pololu 5V', 'ESP32-C3 SuperMini': 'ESP32-C3', 'SRD-05VDC': 'SRD-05VDC'}
BLUE, BLUE_T, PINK, ORANGE = '#2f6db5', '#1f4f8a', '#c2185b', '#d9480f'

b = pcbnew.LoadBoard(PCB)
bb = b.GetBoardEdgesBoundingBox()
X0, Y0, X1, Y1 = bb.GetX() / S, bb.GetY() / S, bb.GetRight() / S, bb.GetBottom() / S
CU = pcbnew.F_Cu if TOP else pcbnew.B_Cu


def P(x, y):
    """board mm -> page mm (mirrored left-right for the bottom view)"""
    return (OX + SC * (x - X0) if TOP else OX + SC * (X1 - x)), OY + SC * (y - Y0)


def xy(v):
    return v.x / S, v.y / S


def fmt(v):
    return ('%.3f' % v).rstrip('0').rstrip('.')


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def nice_value(v):
    v = v.replace('uF', 'µF').replace('nF', 'nF')
    if v in ('100', '1k', '10k', '100k', '1M') or v.endswith('k') and v[:-1].isdigit():
        v = v if v.endswith(('k', 'M')) else v + 'Ω'
    return SHORT_VALUE.get(v, v)


def poly_path(pts):
    return 'M' + ' L'.join('%s %s' % (fmt(a), fmt(c)) for a, c in (P(*p) for p in pts)) + ' Z'


def sps_path(sps):
    d = []
    for i in range(sps.OutlineCount()):
        o = sps.Outline(i)
        d.append(poly_path([xy(o.CPoint(k)) for k in range(o.PointCount())]))
        for j in range(sps.HoleCount(i)):
            h = sps.Hole(i, j)
            d.append(poly_path([xy(h.CPoint(k)) for k in range(h.PointCount())]))
    return ' '.join(d)


def shape_path(g):
    """F.SilkS / F.Fab graphic -> SVG path (page coords)"""
    st = g.GetShape()
    if st == pcbnew.SHAPE_T_SEGMENT:
        return poly_path([xy(g.GetStart()), xy(g.GetEnd())])[:-2]
    if st == pcbnew.SHAPE_T_RECTANGLE:
        return poly_path([xy(v) for v in g.GetRectCorners()])
    if st == pcbnew.SHAPE_T_CIRCLE:
        cx, cy = P(*xy(g.GetCenter()))
        rr = SC * g.GetRadius() / S
        return 'M%s %s a%s %s 0 1 0 %s 0 a%s %s 0 1 0 %s 0' % (fmt(cx - rr), fmt(cy), fmt(rr), fmt(rr), fmt(2 * rr), fmt(rr), fmt(rr), fmt(-2 * rr))
    if st == pcbnew.SHAPE_T_ARC:
        c = xy(g.GetCenter())
        s_, m_, e_ = xy(g.GetStart()), xy(g.GetArcMid()), xy(g.GetEnd())
        r_ = math.hypot(s_[0] - c[0], s_[1] - c[1])
        a0 = math.atan2(s_[1] - c[1], s_[0] - c[0])
        a1 = math.atan2(e_[1] - c[1], e_[0] - c[0])
        am = math.atan2(m_[1] - c[1], m_[0] - c[0])
        sweep = (a1 - a0) % (2 * math.pi)
        if (am - a0) % (2 * math.pi) > sweep:
            sweep -= 2 * math.pi
        pts = [(c[0] + r_ * math.cos(a0 + sweep * k / 24), c[1] + r_ * math.sin(a0 + sweep * k / 24)) for k in range(25)]
        return poly_path(pts)[:-2]
    if st == pcbnew.SHAPE_T_POLY:
        ps = g.GetPolyShape()
        return ' '.join(poly_path([xy(ps.Outline(i).CPoint(k)) for k in range(ps.Outline(i).PointCount())])
                        for i in range(ps.OutlineCount()))
    return ''


out = []
add = out.append
add('<svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm" viewBox="0 0 %s %s" '
    'font-family="Arial, Helvetica, sans-serif">' % (PAGE_W, PAGE_H, PAGE_W, PAGE_H))
add('<rect x="0" y="0" width="%s" height="%s" fill="#ffffff"/>' % (PAGE_W, PAGE_H))

# ---- title ----
if TOP:
    title = 'Texecom power reset · rev A · top side (component side)'
    sub = ('Viewed from the TOP, as the engraved legend reads. Scale 2:1 (print at 100%, A4 landscape). '
           'Parts sit on this side; most joints are soldered underneath.')
else:
    title = 'Texecom power reset · rev A · bottom side (solder side)'
    sub = ('Viewed from the BOTTOM: the board is flipped left-right, as you see it when soldering. '
           'Scale 2:1 (print at 100%, A4 landscape).')
add('<text x="%s" y="14" font-size="6.2" font-weight="700" fill="#1d2b2f">%s</text>' % (OX, esc(title)))
add('<text x="%s" y="21" font-size="3.4" fill="#4a5a5e">%s</text>' % (OX, esc(sub)))

# ---- board outline (rounded rectangle from Edge.Cuts) ----
r = 0
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_ARC:
        r = d.GetRadius() / S
        break
bx = min(P(X0, Y0)[0], P(X1, Y0)[0])
add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#f6f4ee" stroke="#1d2b2f" stroke-width="0.5"/>'
    % (fmt(bx), fmt(OY), fmt(SC * (X1 - X0)), fmt(SC * (Y1 - Y0)), fmt(SC * r)))
board_page = (bx, OY, bx + SC * (X1 - X0), OY + SC * (Y1 - Y0))

# ---- copper of this side, light, for context ----
for z in b.Zones():
    if not z.GetIsRuleArea() and z.IsOnLayer(CU):
        add('<path d="%s" fill="#f1dfcb" fill-rule="evenodd" stroke="none"/>' % sps_path(z.GetFilledPolysList(CU)))
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == CU:
        (ax, ay), (cx, cy) = P(*xy(t.GetStart())), P(*xy(t.GetEnd()))
        add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#dcb48c" stroke-width="%s" stroke-linecap="round"/>'
            % (fmt(ax), fmt(ay), fmt(cx), fmt(cy), fmt(SC * t.GetWidth() / S)))
for p in b.GetPads():
    if not p.IsOnLayer(CU):
        continue
    sps = pcbnew.SHAPE_POLY_SET()
    p.TransformShapeToPolygon(sps, CU, 0, 5000, pcbnew.ERROR_INSIDE)
    smd = p.GetParentFootprint().IsFlipped()
    add('<path d="%s" fill="%s" stroke="none"/>' % (sps_path(sps), '#b8733c' if smd else '#cf9a6c'))
    if p.GetDrillSize().x:
        hx, hy = P(*xy(p.GetPosition()))
        add('<circle cx="%s" cy="%s" r="%s" fill="#ffffff"/>' % (fmt(hx), fmt(hy), fmt(SC * p.GetDrillSize().x / 2 / S)))

occupied = []  # page-space rectangles taken by labels / highlighted parts


def rect_hit(a, c):
    return not (a[2] < c[0] or c[2] < a[0] or a[3] < c[1] or c[3] < a[1])


def place(cx, cy, w, h, dist_list, inside=None):
    for dist in dist_list:
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            x, y = cx + dist * math.cos(a) - w / 2, cy + dist * math.sin(a) - h / 2
            box = (x, y, x + w, y + h)
            if box[0] < board_page[0] + 1 or box[2] > board_page[2] - 1 or box[1] < board_page[1] + 1 or box[3] > board_page[3] - 1:
                continue
            if any(rect_hit(box, o) for o in occupied):
                continue
            occupied.append(box)
            return box
    return None


fronts = [f for f in b.GetFootprints() if not f.IsFlipped() and not f.GetReference().startswith('MH')]
bottoms = [f for f in b.GetFootprints() if f.IsFlipped()]


def fp_box(f, layer):
    c = f.GetCourtyard(layer).BBox()
    (ax, ay), (cx, cy) = P(c.GetX() / S, c.GetY() / S), P(c.GetRight() / S, c.GetBottom() / S)
    return (min(ax, cx), min(ay, cy), max(ax, cx), max(ay, cy))


# ---- parts ----
if TOP:
    # every top-side part: light body, its silkscreen outline (polarity / pin-1 marks included), label
    for f in fronts:
        box = fp_box(f, pcbnew.F_CrtYd)
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="1" fill="%s" fill-opacity="0.10" stroke="none"/>'
            % (fmt(box[0]), fmt(box[1]), fmt(box[2] - box[0]), fmt(box[3] - box[1]), BLUE))
        src = pcbnew.F_Fab if f.GetFPID().GetLibItemName().wx_str().startswith('CP_Radial') else pcbnew.F_SilkS
        for g in f.GraphicalItems():
            if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() == src:
                d = shape_path(g)
                if d:
                    filled = g.GetShape() == pcbnew.SHAPE_T_POLY and getattr(g, 'IsSolidFill', lambda: False)()
                    add('<path d="%s" fill="%s" stroke="%s" stroke-width="0.45" stroke-linecap="round" stroke-linejoin="round"/>'
                        % (d, BLUE if filled else 'none', BLUE))
    for f in bottoms:  # bottom parts only as faint dashed boxes
        box = fp_box(f, pcbnew.B_CrtYd)
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="0.6" fill="none" stroke="#a9b2ae" stroke-width="0.3" '
            'stroke-dasharray="1 0.8"/>' % (fmt(box[0]), fmt(box[1]), fmt(box[2] - box[0]), fmt(box[3] - box[1])))
else:
    for f in fronts:  # through-hole parts: grey dashed outline + ref
        box = fp_box(f, pcbnew.F_CrtYd)
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="0.8" fill="none" stroke="#a9b2ae" stroke-width="0.35" '
            'stroke-dasharray="1.2 0.9"/>' % (fmt(box[0]), fmt(box[1]), fmt(box[2] - box[0]), fmt(box[3] - box[1])))
        add('<text x="%s" y="%s" font-size="2.9" text-anchor="middle" fill="#8b9692">%s</text>'
            % (fmt((box[0] + box[2]) / 2), fmt((box[1] + box[3]) / 2 + 1.2), f.GetReference()))
    smd_boxes = {}
    for f in bottoms:
        pts = []
        for g in f.GraphicalItems():
            if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() == pcbnew.B_Fab:
                sb = g.GetBoundingBox()
                pts += [(sb.GetX() / S, sb.GetY() / S), (sb.GetRight() / S, sb.GetBottom() / S)]
        for p in f.Pads():
            pb = p.GetBoundingBox()
            pts += [(pb.GetX() / S, pb.GetY() / S), (pb.GetRight() / S, pb.GetBottom() / S)]
        xs = [P(*q)[0] for q in pts]
        ys = [P(*q)[1] for q in pts]
        box = (min(xs) - 0.6, min(ys) - 0.6, max(xs) + 0.6, max(ys) + 0.6)
        smd_boxes[f.GetReference()] = box
        occupied.append(box)
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="1" fill="%s" fill-opacity="0.16" stroke="%s" '
            'stroke-width="0.6"/>' % (fmt(box[0]), fmt(box[1]), fmt(box[2] - box[0]), fmt(box[3] - box[1]), BLUE, BLUE))

# mounting holes
for f in b.GetFootprints():
    if f.GetReference().startswith('MH'):
        hx, hy = P(*xy(f.GetPosition()))
        add('<circle cx="%s" cy="%s" r="%s" fill="#ffffff" stroke="#1d2b2f" stroke-width="0.4"/>' % (fmt(hx), fmt(hy), fmt(SC * 1.6)))

# ---- top-joint pads (top view only): pads a top track runs into ----
top_joints = []
if TOP:
    ends = [(t.GetStart(), t.GetEnd()) for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == pcbnew.F_Cu]
    for f in fronts:
        for p in f.Pads():
            if p.GetDrillSize().x and any(p.HitTest(e) for se in ends for e in se):
                top_joints.append(p)
    for p in top_joints:
        hx, hy = P(*xy(p.GetPosition()))
        rr = SC * max(p.GetSize().x, p.GetSize().y) / 2 / S + 0.9
        add('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="0.7"/>' % (fmt(hx), fmt(hy), fmt(rr), ORANGE))
        occupied.append((hx - rr, hy - rr, hx + rr, hy + rr))

# ---- vias: numbered in reading order as seen from the BOTTOM (same numbers on both drawings) ----
def via_key(v):
    x, y = xy(v.GetPosition())
    return (round(SC * (y - Y0) / 6), X1 - x)


vias = sorted((t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T), key=via_key)
via_pts = []
for v in vias:
    vx, vy = P(*xy(v.GetPosition()))
    rr = SC * v.GetWidth(CU) / 2 / S
    via_pts.append((vx, vy, rr))
    occupied.append((vx - rr, vy - rr, vx + rr, vy + rr))
    add('<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="0.7"/>'
        % (fmt(vx), fmt(vy), fmt(rr + 0.5), PINK, PINK))
    add('<circle cx="%s" cy="%s" r="%s" fill="#ffffff" stroke="%s" stroke-width="0.3"/>'
        % (fmt(vx), fmt(vy), fmt(SC * v.GetDrill() / 2 / S), PINK))

# ---- labels ----
if TOP:
    big = []
    for f in sorted(fronts, key=lambda f: -(fp_box(f, pcbnew.F_CrtYd)[2] - fp_box(f, pcbnew.F_CrtYd)[0]) * (fp_box(f, pcbnew.F_CrtYd)[3] - fp_box(f, pcbnew.F_CrtYd)[1])):
        box = fp_box(f, pcbnew.F_CrtYd)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        ref, val = f.GetReference(), nice_value(f.GetValue())
        if f.GetReference().startswith('J'):
            val = ''   # the terminal names are engraved on the board already; value = BAT IN etc.
        w = max(len(ref) * 2.5, len(val) * 1.7) + 1.4
        h = 6.8 if val else 4.4
        # inside the body when there's room, otherwise outside with a leader
        lb = None
        if box[2] - box[0] > w + 1 and box[3] - box[1] > h + 1:
            lb = place(cx, cy, w, h, [0, 2, 3.5])
        leader = lb is None
        if lb is None:
            lb = place(cx, cy, w, h, [6, 7.5, 9, 11, 13, 15])
        if lb is None:
            continue
        lx, ly = (lb[0] + lb[2]) / 2, lb[1]
        if leader:
            add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.3"/>' % (fmt(cx), fmt(cy), fmt(lx), fmt(ly + h / 2), BLUE))
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="1" fill="#ffffff" fill-opacity="0.92" stroke="%s" stroke-width="0.3"/>'
            % (fmt(lb[0]), fmt(lb[1]), fmt(lb[2] - lb[0]), fmt(lb[3] - lb[1]), BLUE))
        add('<text x="%s" y="%s" font-size="3.4" font-weight="700" text-anchor="middle" fill="%s">%s</text>' % (fmt(lx), fmt(ly + 3.4), BLUE_T, ref))
        if val:
            add('<text x="%s" y="%s" font-size="2.5" text-anchor="middle" fill="%s">%s</text>' % (fmt(lx), fmt(ly + 6.0), BLUE_T, esc(val)))
else:
    for f in sorted(bottoms, key=lambda f: f.GetReference()):
        box = smd_boxes[f.GetReference()]
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        ref, val = f.GetReference(), nice_value(f.GetValue())
        w = max(len(ref) * 2.6, len(val) * 1.75) + 1.6
        lb = place(cx, cy, w, 7.2, [7, 8.5, 10, 12, 14])
        if lb is None:
            continue
        lx, ly = (lb[0] + lb[2]) / 2, lb[1]
        add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.3"/>' % (fmt(cx), fmt(cy), fmt(lx), fmt(ly + 3.6), BLUE))
        add('<rect x="%s" y="%s" width="%s" height="%s" rx="1" fill="#ffffff" stroke="%s" stroke-width="0.35"/>'
            % (fmt(lb[0]), fmt(lb[1]), fmt(lb[2] - lb[0]), fmt(lb[3] - lb[1]), BLUE))
        add('<text x="%s" y="%s" font-size="3.6" font-weight="700" text-anchor="middle" fill="%s">%s</text>' % (fmt(lx), fmt(ly + 3.5), BLUE_T, ref))
        add('<text x="%s" y="%s" font-size="2.7" text-anchor="middle" fill="%s">%s</text>' % (fmt(lx), fmt(ly + 6.4), BLUE_T, esc(val)))

# via badges
for i, (vx, vy, rr) in enumerate(via_pts, 1):
    lb = place(vx, vy, 4.6, 4.6, [rr + 3.2, rr + 4.2, rr + 5.4, rr + 7, rr + 9])
    if lb is None:
        continue
    bx_, by_ = (lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2
    add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.3"/>' % (fmt(vx), fmt(vy), fmt(bx_), fmt(by_), PINK))
    add('<circle cx="%s" cy="%s" r="2.3" fill="%s"/>' % (fmt(bx_), fmt(by_), PINK))
    add('<text x="%s" y="%s" font-size="2.9" font-weight="700" text-anchor="middle" fill="#ffffff">%d</text>'
        % (fmt(bx_), fmt(by_ + 1.0), i))

# edge orientation notes
tx = (board_page[0] + board_page[2]) / 2
add('<text x="%s" y="%s" font-size="3" text-anchor="middle" fill="#4a5a5e">terminal edge (J1–J4)</text>' % (fmt(tx), fmt(board_page[3] + 5)))
if TOP:
    add('<text x="%s" y="%s" font-size="3" text-anchor="end" fill="#4a5a5e">SuperMini (U3): USB-C at this edge →</text>'
        % (fmt(board_page[2] - 2), fmt(board_page[1] - 2.2)))
else:
    add('<text x="%s" y="%s" font-size="3" fill="#4a5a5e">← SuperMini (U3): USB-C at this edge</text>'
        % (fmt(board_page[0] + 2), fmt(board_page[1] - 2.2)))

# ---- side panel ----
SX = board_page[2] + 10
y = OY + 2


def heading(t):
    global y
    add('<text x="%s" y="%s" font-size="4.2" font-weight="700" fill="#1d2b2f">%s</text>' % (fmt(SX), fmt(y), esc(t)))


def para(lines, color='#1d2b2f', x=None, step=4.4):
    global y
    for ln in lines:
        add('<text x="%s" y="%s" font-size="3.1" fill="%s">%s</text>' % (fmt(SX if x is None else x), fmt(y), color, esc(ln)))
        y += step


def refkey(f):
    rf = f.GetReference()
    return (rf.rstrip('0123456789'), int(''.join(ch for ch in rf if ch.isdigit()) or 0))


if TOP:
    heading('Top-side parts')
    y += 5
    parts = sorted(fronts, key=refkey)
    half = (len(parts) + 1) // 2
    y0 = y
    for k, f in enumerate(parts):
        col = 0 if k < half else 1
        yy = y0 + (k % half) * 3.9
        xx = SX + col * 40
        val = nice_value(f.GetValue())
        add('<text x="%s" y="%s" font-size="2.8" font-weight="700" fill="%s">%s</text>' % (fmt(xx), fmt(yy), BLUE_T, f.GetReference()))
        add('<text x="%s" y="%s" font-size="2.8" fill="#1d2b2f">%s</text>' % (fmt(xx + 8), fmt(yy), esc(val)))
    y = y0 + half * 3.9 + 5
    heading('Key')
    y += 5.2
    add('<circle cx="%s" cy="%s" r="1.7" fill="none" stroke="%s" stroke-width="0.7"/>' % (fmt(SX + 2.4), fmt(y - 1.1), ORANGE))
    para(['pad with a top track: solder on top too (%d)' % len(top_joints)], x=SX + 7)
    y += 1
    add('<circle cx="%s" cy="%s" r="2.1" fill="%s"/>' % (fmt(SX + 2.4), fmt(y - 1.1), PINK))
    para(['via (wire link, both sides; same numbers', 'as the bottom drawing)'], x=SX + 7)
    y += 1
    add('<rect x="%s" y="%s" width="5" height="3.4" rx="0.6" fill="none" stroke="#a9b2ae" stroke-width="0.4" stroke-dasharray="1 0.8"/>' % (fmt(SX), fmt(y - 3)))
    para(['1206 part on the bottom side'], x=SX + 7)
    y += 3
    para(['Mount axial and disc parts 1–2mm raised so', 'the ringed top pads can be reached. The rest',
          'is soldered on the bottom only (see README §6c).'], color='#4a5a5e')
else:
    heading('Bottom-side SMD parts (1206)')
    y += 3
    for f in sorted(bottoms, key=refkey):
        y += 5.2
        add('<rect x="%s" y="%s" width="3.4" height="3.4" rx="0.6" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="0.4"/>' % (fmt(SX), fmt(y - 3), BLUE, BLUE))
        add('<text x="%s" y="%s" font-size="3.3" font-weight="700" fill="%s">%s</text>' % (fmt(SX + 5), fmt(y), BLUE_T, f.GetReference()))
        add('<text x="%s" y="%s" font-size="3.1" fill="#1d2b2f">%s</text>' % (fmt(SX + 15), fmt(y), esc(DESC_BOTTOM.get(f.GetReference(), f.GetValue()))))
    y += 10
    heading('Vias (%d): wire links' % len(vias))
    y += 6
    add('<circle cx="%s" cy="%s" r="2.3" fill="%s"/>' % (fmt(SX + 2.3), fmt(y - 1.1), PINK))
    add('<text x="%s" y="%s" font-size="2.9" font-weight="700" text-anchor="middle" fill="#ffffff">n</text>' % (fmt(SX + 2.3), fmt(y - 0.1)))
    under = []
    for i, v in enumerate(vias, 1):
        for f in fronts:
            if f.GetCourtyard(pcbnew.F_CrtYd).Contains(v.GetPosition()):
                under.append('%d is under %s' % (i, f.GetReference()))
    note = ('first. Via ' + ', '.join(under) + ': keep it low.') if under else 'first.'
    para(['Push a short wire through each via,', 'solder both sides, trim flush. Fit them', note], x=SX + 6)
    y += 5
    heading('Key')
    for col, label, dash in (('#b8733c', 'SMD pad (bottom part)', None), ('#cf9a6c', 'through-hole pad', None),
                             ('#a9b2ae', 'through-hole part (body on top)', '1.2 0.9'), ('#f1dfcb', 'GND pour (bottom)', None)):
        y += 5.4
        if dash:
            add('<rect x="%s" y="%s" width="5" height="3.4" rx="0.6" fill="none" stroke="%s" stroke-width="0.4" stroke-dasharray="%s"/>'
                % (fmt(SX), fmt(y - 3), col, dash))
        else:
            add('<rect x="%s" y="%s" width="5" height="3.4" rx="0.6" fill="%s"/>' % (fmt(SX), fmt(y - 3), col))
        add('<text x="%s" y="%s" font-size="3.1" fill="#1d2b2f">%s</text>' % (fmt(SX + 7), fmt(y), label))
    y += 9
    para(['Solder the SMD parts first, then the', 'through-hole parts. Everything is',
          'soldered on this side; pads marked with', 'a ring on the top legend also need a',
          'top joint (see README §6c).'], color='#4a5a5e')

add('</svg>')
svg = '\n'.join(out)
open(OUT, 'w', encoding='utf-8').write(svg)
print('wrote', OUT, '| vias', len(vias), '| top joints', len(top_joints))

# ---- PDF: headless Edge/Chrome (real fonts, exact A4); MuPDF fallback ----
pdf_out = OUT[:-4] + '.pdf'
browsers = [r'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
            r'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
            r'C:/Program Files/Google/Chrome/Application/chrome.exe']
done = False
try:
    if os.path.exists(pdf_out):
        os.remove(pdf_out)
except PermissionError:
    print('PDF not written: %s is open in another program; close it and run again' % pdf_out)
    browsers = []
    done = True
for exe in browsers:
    if not os.path.exists(exe):
        continue
    html = os.path.join(tempfile.gettempdir(), 'assembly_print_%s.html' % SIDE)
    open(html, 'w', encoding='utf-8').write(
        '<!doctype html><html><head><meta charset="utf-8"><style>@page{size:297mm 210mm;margin:0}'
        'html,body{margin:0;padding:0}svg{display:block;width:297mm;height:210mm}</style></head><body>'
        + svg + '</body></html>')
    subprocess.run([exe, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--print-to-pdf=' + os.path.abspath(pdf_out), 'file:///' + html.replace(os.sep, '/')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    done = os.path.exists(pdf_out)
    if done:
        print('wrote', pdf_out, 'via', os.path.basename(exe))
        break
if not done:
    try:
        import pymupdf
        pymupdf.open('pdf', pymupdf.open(OUT).convert_to_pdf()).save(pdf_out)
        print('wrote', pdf_out, 'via MuPDF')
    except Exception as e:  # PDF is optional
        print('no pdf:', e)

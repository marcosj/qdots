import stim

def coord(d, qi):
    c = stim.Circuit()
    D = 2 * d

    dq, xa, za = [], [], []
    coords = {}

    # Data qubits are simple: odd/odd pairs
    for y in range(1, D, 2):
        for x in range(1, D, 2):
            i = qi(x, y, D)
            dq.append(i)
            c.append('QUBIT_COORDS', i, [x, y])
            coords[i] = [x, y]

    # Z-Ancillas: Both x and y are EVEN, and (x + y) % 4 == 0
    for y in range(0, D + 1, 2):
        for x in range(0, D + 1, 2):
            if (x + y) % 4 == 0:
                # Excludes the horizontal boundary lines (y=0 and y=D)
                if 0 < y < D:
                    i = qi(x, y, D)
                    za.append(i)
                    c.append('QUBIT_COORDS', i, [x, y])
                    coords[i] = [x, y]

    # X-Ancillas: Both x and y are EVEN, and (x + y) % 4 == 2
    for y in range(0, D + 1, 2):
        for x in range(0, D + 1, 2):
            if (x + y) % 4 == 2:
                # Excludes the vertical boundary lines (x=0 and x=D)
                if 0 < x < D:
                    i = qi(x, y, D)
                    xa.append(i)
                    c.append('QUBIT_COORDS', i, [x, y])
                    coords[i] = [x, y]

    return c, dq, xa, za, coords

def prep(dq, xa, za):
    c = stim.Circuit()
    # prepares data qubits in |+>_L
    c.append('RX', dq)
    c.append('TICK')
    c.append('R', xa + za)
    c.append('TICK')
    c.append('H', dq[::2])
    c.append('TICK')
    return c

def round(d, dq, xa, za, coords, off, qi):
    c = stim.Circuit()
    c.append("H", xa + za)
    c.append("TICK")

    D = 2 * d
    for (xdx, xdy), (zdx, zdy) in off:
        cz_targets = []

        # X-ancillas: Control = X-ancilla, Target = Data qubit at offset
        for a in xa:
            ax, ay = coords[a]
            trgt = qi(ax + xdx, ay + xdy, D)
            if trgt in dq:
                cz_targets.extend([a, trgt])

        # Z-ancillas: Control = Data qubit at offset, Target = Z-ancilla
        for a in za:
            ax, ay = coords[a]
            ctrl = qi(ax + zdx, ay + zdy, D)
            if ctrl in dq:
                cz_targets.extend([ctrl, a])

        c.append("CX", cz_targets)
        c.append("TICK")

        if xdx > 0:
            c.append("H", dq)
            c.append("TICK")

    c.append("H", xa + za)
    c.append("TICK")

    c.append("MR", xa + za)
    return c

def detect(r, xa, za, coords):
    c = stim.Circuit()
    aq = xa + za
    na = len(aq)

    if r == 0:
        for i, a in enumerate(xa):
            c.append("DETECTOR", [stim.target_rec(-na+i)], coords[a]+[0])
    else:
        c.append("SHIFT_COORDS", [], [0, 0, 1])
        for i, a in enumerate(aq):
            rec = -na + i
            prev = rec - na
            c.append("DETECTOR", [stim.target_rec(rec), stim.target_rec(prev)], coords[a]+[0])
    c.append("TICK")
    return c

def meas(d, r, dq, xa, za, coords, off, qi):
    c = stim.Circuit()
    c.append('H', dq[::2])
    c.append('TICK')
    c.append('MX', dq)
    D = 2 * d
    na, nd = len(xa) + len(za), len(dq)
    # Compare Z-measurements against the Z-ancillas
    for i, q in enumerate(xa):
        x, y = coords[q]
        rec = []
        for (dx, dy), _ in off:
            tx, ty = x + dx, y + dy
            if 0 <= tx < D and 0 <= ty < D:
                rec.append(stim.target_rec(-nd + dq.index(qi(tx, ty, D))))
        j = xa.index(q)
        rec.append(stim.target_rec(-nd - na + j))
        c.append('DETECTOR', rec, [x, y, r])

    # Logical X runs vertically
    xL = [qi(1, y, D) for y in range(1, D, 2)]
    rec = [stim.target_rec(-nd + dq.index(q)) for q in xL]
    c.append('OBSERVABLE_INCLUDE', rec, 0)
    return c

def gen_xzzx_rot_mx(d, r):
    qi = lambda x, y, D: x + (D + 1) * (y // 2)
    off = [
        ((+1, +1), (+1, +1)), # NE
        ((-1, +1), (+1, -1)), # NW
        ((+1, -1), (-1, +1)), # SE
        ((-1, -1), (-1, -1))  # SW
    ]
    C, dq, xa, za, coords = coord(d, qi)
    P = prep(dq, xa, za)
    R = round(d, dq, xa, za, coords, off, qi)
    D0 = detect(0, xa, za, coords)
    Di = detect(r, xa, za, coords)
    Ri = R + Di
    M = meas(d, r, dq, xa, za, coords, off, qi)
    return C + P + R + D0 + Ri * (r-1) + M

if __name__ == '__main__':
    sc = gen_xzzx_rot_mx(3, 1)
    sc.to_file("xzrxcx.stim")
    svg = sc.diagram('timeslice-svg')
    with open("xzrxcx.svg", "w") as f:
        f.write(str(svg))
    dem = sc.detector_error_model(decompose_errors=True)
    #print('dem\n', dem)

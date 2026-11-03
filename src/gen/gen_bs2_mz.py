import stim

def coord(d, qi):
    c = stim.Circuit()
    D = 2 * d

    dq, xa, za = [], [], []
    coords = {}

    # Data Qubits
    dq = list(range(d*d))
    for q in dq:
        row, col = divmod(q, d)
        c.append('QUBIT_COORDS', [q], [2*col, 2*row])
        coords[q] = [2*col, 2*row]

    # ZZ Ancillas
    za = list(range(d*d, d*d + d*(d-1)))
    for i in range(len(za)):
        row, col = divmod(i, d)
        c.append('QUBIT_COORDS', [za[i]], [2*col, 2*row+1])
        coords[za[i]] = [2*col, 2*row+1]

    # XX Ancillas
    xa = list(range(d*d + d*(d-1), d*d + 2*d*(d-1)))
    for i in range(len(xa)):
        row, col = divmod(i, d-1)
        c.append('QUBIT_COORDS', [xa[i]], [2*col+1, 2*row])
        coords[xa[i]] = [2*col+1, 2*row]

    return c, dq, xa, za, coords

def prep(dq, xa, za):
    c = stim.Circuit()
    # prepares data qubits in |0>_L
    c.append('R', dq)
    c.append('TICK')
    c.append('R', za + xa)
    c.append('TICK')
    return c

def round(d, dq, xa, za, coords, off, qi):
    lines = []
    for col in range(d-1):
        stabX = 'MPP '
        for row in range(d):
            stabX += f'X{row * d + col}*X{row * d + col+1} '
        lines.append(stabX)
        lines.append('TICK')
    for row in range(d-1):
        stabZ = 'MPP '
        for col in range(d):
            stabZ += f'Z{row * d + col}*Z{(row+1) * d + col} '
        lines.append(stabZ)
        lines.append('TICK')
    return stim.Circuit('\n'.join(lines))
    '''c = stim.Circuit()
    for col in range(d-1):
        gauges = []
        for row in range(d):
            gauges.append(f'X{row * d + col}*X{row * d + col+1}')
        c.append('MPP', [g for g in gauges])
        c.append('TICK')
    for row in range(d-1):
        gauges = []
        for col in range(d):
            gauges.append(f'Z{row * d + col}*Z{(row+1) * d + col}')
        c.append('MPP', [], [g for g in gauges])
        c.append('TICK')
    return c'''

def detect(d, r, xa, za, coords):
    c = stim.Circuit()
    if r > 0:
        c.append("SHIFT_COORDS", [], [0, 0, 1])

    # X stabilizers
    for col in range(d-1):
        gauge = [col*d + row for row in range(d)]
        meas = [stim.target_rec(-len(xa) - len(za) + i) for i in gauge]
        if r > 0:
            prev = [stim.target_rec(-(2*len(xa)+2*len(za)) + i) for i in gauge]
            c.append('DETECTOR', meas + prev, [2*col+1, 0, 0])

    # Z stabilizers
    for row in range(d-1):
        gauge = [row*d + col for col in range(d)]
        meas = [stim.target_rec(-len(za) + i) for i in gauge]
        if r > 0:
            prev = [stim.target_rec(-(2*len(za)+len(xa)) + i) for i in gauge]
            c.append('DETECTOR', meas + prev, [0, 2*row+1, 0])
        else:
            c.append('DETECTOR', meas, [0, 2*row+1, 0])

    c.append("TICK")
    return c

def meas(d, r, dq, xa, za, coords, off, qi):
    c = stim.Circuit()
    c.append('M', dq)
    for i in range(len(za)):
        row, col = divmod(i, d)
        meas = [stim.target_rec(-(len(dq)+len(za)) + i)]
        prev = [stim.target_rec(-len(dq) + i), stim.target_rec(-len(dq) + i+d)]
        c.append('DETECTOR', meas + prev, [2*col, 2*row+1, r])
    Z_L = [stim.target_rec(-d*d + i) for i in range(d)]
    c.append('OBSERVABLE_INCLUDE', Z_L, 0)
    return c

def gen_bs2_mz(d, r):
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
    D0 = detect(d, 0, xa, za, coords)
    Di = detect(d, r, xa, za, coords)
    Ri = R + Di
    M = meas(d, r, dq, xa, za, coords, off, qi)
    return C + P + R + D0 + Ri * (r-1) + M

if __name__ == '__main__':
    from ..conf import TMP_DIR
    c = gen_bs2_mz(3, 3)
    c.to_file(TMP_DIR / "bs2.stim")
    with open(TMP_DIR / "bs2.url", "w") as f:
        f.write(c.to_crumble_url())
    dem = c.detector_error_model(decompose_errors=True)
    #print('dem\n', dem)
    svg = c.diagram('timeslice-svg') # detslice-with-ops
    with open(TMP_DIR / "bs2.svg", "w") as f:
        f.write(str(svg))

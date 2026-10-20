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
    # prepares data qubits in |+>_L
    c.append('RX', dq)
    c.append('TICK')
    c.append('R', za + xa)
    c.append('TICK')
    return c

def round(d, dq, xa, za, coords, off, qi):
    c = stim.Circuit()

    # X gauges
    c.append('H', xa)
    c.append('TICK')
    for i in range(len(xa)):
        c.append('CNOT', [xa[i], i + i // (d-1)])
    c.append('TICK')
    for i in range(len(xa)):
        c.append('CNOT', [xa[i], i+1 + i // (d-1)])
    c.append('TICK')
    c.append('H', xa)
    c.append('TICK')
    c.append('MR', xa)
    c.append('TICK')

    # Z gauges
    for i in range(len(za)):
        c.append('CNOT', [i, za[i]])
    c.append('TICK')
    for i in range(len(za)):
        c.append('CNOT', [i+d, za[i]])
    c.append('TICK')
    c.append('MR', za)
    c.append('TICK')

    #c.append("MR", xa + za)
    return c

def detect(d, r, xa, za, coords):
    c = stim.Circuit()
    if r > 0:
        c.append("SHIFT_COORDS", [], [0, 0, 1])

    # X stabilizers
    for col in range(d-1):
        gauge = [col + row*(d-1) for row in range(d)]
        meas = [stim.target_rec(-len(xa) - len(za) + i) for i in gauge]
        if r > 0:
            prev = [stim.target_rec(-(2*len(xa)+2*len(za)) + i) for i in gauge]
            c.append('DETECTOR', meas + prev, [2*col+1, 0, 0])
        else:
            c.append('DETECTOR', meas, [2*col+1, 0, 0])

    # Z stabilizers
    for row in range(d-1):
        gauge = [row*d + col for col in range(d)]
        meas = [stim.target_rec(-len(za) + i) for i in gauge]
        if r > 0:
            prev = [stim.target_rec(-(2*len(za)+len(xa)) + i) for i in gauge]
            c.append('DETECTOR', meas + prev, [0, 2*row+1, 0])

    c.append("TICK")
    return c

def meas(d, r, dq, xa, za, coords, off, qi):
    c = stim.Circuit()
    c.append('MX', dq)
    for i in range(len(xa)):
        row, col = divmod(i, d)
        meas = [stim.target_rec(-(len(dq)+len(xa)+len(za)) + i)]
        prev = [stim.target_rec(-len(dq) + i), stim.target_rec(-len(dq) + i+d)]
        c.append('DETECTOR', meas + prev, [2*col+1, 2*row, r])
    X_L = [stim.target_rec(-d*d + i*d) for i in range(d)]
    c.append('OBSERVABLE_INCLUDE', X_L, 0)
    return c

def gen_bs_mx(d, r):
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
    c = gen_bs_mx(3, 1)
    c.to_file(TMP_DIR / "bsx3.stim")
    dem = c.detector_error_model(decompose_errors=True)
    #print('dem\n', dem)
    svg = c.diagram('timeslice-svg') # detslice-with-ops
    with open(TMP_DIR / "bs3.svg", "w") as f:
        f.write(str(svg))

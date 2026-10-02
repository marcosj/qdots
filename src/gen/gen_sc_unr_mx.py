import stim

qi = lambda x, y, D: x + (D + 1) * (y // 2)
coords = {}
off = [
    ((+1, +1), (+1, +1)), # NE
    ((-1, +1), (+1, -1)), # NW
    ((+1, -1), (-1, +1)), # SE
    ((-1, -1), (-1, -1))  # SW
]

def coord(d):
    c = stim.Circuit()
    D = 2 * d

    dq, xa, za = [], [], []

    # Data qubits are simple: odd/odd pairs
    for y in range(1, D, 2):
        for x in range(1, D, 2):
            i = qi(x, y, D)
            dq.append(i)
            c.append('QUBIT_COORDS', i, [x, y])
            coords[i] = [x, y]

    # 2. Z-Ancillas: Both x and y are EVEN, and (x + y) % 4 == 0
    for y in range(0, D + 1, 2):
        for x in range(0, D + 1, 2):
            if (x + y) % 4 == 0:
                # Keep internal checks and the open left/right boundaries
                # Excludes the horizontal boundary lines (y=0 and y=D)
                if 0 < y < D:
                    i = qi(x, y, D)
                    za.append(i)
                    c.append('QUBIT_COORDS', i, [x, y])
                    coords[i] = [x, y]

    # 3. X-Ancillas: Both x and y are EVEN, and (x + y) % 4 == 2
    for y in range(0, D + 1, 2):
        for x in range(0, D + 1, 2):
            if (x + y) % 4 == 2:
                # Keep internal checks and the open top/bottom boundaries
                # Excludes the vertical boundary lines (x=0 and x=D)
                if 0 < x < D:
                    i = qi(x, y, D)
                    xa.append(i)
                    c.append('QUBIT_COORDS', i, [x, y])
                    coords[i] = [x, y]

    return c, dq, xa, za

def prep(dq, xa, za):
    c = stim.Circuit()
    # prepares data qubits in |0>_L
    c.append('R', dq)
    c.append('TICK')
    c.append('R', xa + za)
    c.append('TICK')
    return c

def round(d, dq, xa, za):
    c = stim.Circuit()
    c.append("H", xa)
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

    c.append("H", xa)
    c.append("TICK")

    c.append("MR", xa + za)
    return c

def detect(r, xa, za):
    c = stim.Circuit()
    aq = xa + za
    na = len(aq)

    if r == 0:
        for i, a in enumerate(za):
            c.append("DETECTOR", [stim.target_rec(-len(za)+i)], coords[a]+[0])
    else:
        c.append("SHIFT_COORDS", [], [0, 0, 1])
        for i, a in enumerate(aq):
            rec = -na + i
            prev = rec - na
            c.append("DETECTOR", [stim.target_rec(rec), stim.target_rec(prev)], coords[a]+[0])
    c.append("TICK")
    return c

def meas(d, r, dq, xa, za):
    c = stim.Circuit()
    c.append('M', dq)
    D = 2 * d
    na, nd = len(xa) + len(za), len(dq)
    # Compare Z-measurements against the Z-ancillas
    for i, q in enumerate(za):
        x, y = coords[q]
        rec = []
        for (dx, dy), _ in off:
            tx, ty = x + dx, y + dy
            if 0 <= tx < D and 0 <= ty < D:
                rec.append(stim.target_rec(-nd + dq.index(qi(tx, ty, D))))
        j = (xa + za).index(q)
        rec.append(stim.target_rec(-nd - na + j))
        c.append('DETECTOR', rec, [x, y, r])

    # Logical Z runs horinzontally
    zL = [qi(x, 1, D) for x in range(1, D, 2)]
    rec = [stim.target_rec(-nd + dq.index(q)) for q in zL]
    c.append('OBSERVABLE_INCLUDE', rec, 0)
    return c

def gen_sc_rot_mz(d, r):
    C, dq, xa, za = coord(d)
    P = prep(dq, xa, za)
    R = round(d, dq, xa, za)
    D0 = detect(0, xa, za)
    Di = detect(r, xa, za)
    Ri = R + Di
    M = meas(d, r, dq, xa, za)
    return C + P + R + D0 + Ri * (r-1) + M

def gen_usc(d, r, mode='X'):
	c = stim.Circuit()
	D = 2 * d - 1
	def qi(x, y): return x + y * D

	dq, xa, za = [], [], []
	for y in range(D):
		for x in range(D):
			i = qi(x, y)
			c.append('QUBIT_COORDS', i, [x, y])
			if (x + y) % 2 == 0:
				dq.append(i)
			elif x % 2 == 1:
				xa.append(i)
			else:
				za.append(i)
	na, nd = len(xa) + len(za), len(dq)

	if mode == 'X':
		# prepares data qubits in |+>_L
		c.append('RX', dq)
	else:
		# prepares data qubits in |0>_L
		c.append('R', dq)
	c.append('TICK')

	# prepares ancilla qubits in |0>_L
	c.append('R', xa + za)
	c.append('TICK')

	for ri in range(r):
		# Round S
		# applies R_Y(-π/2) to data qubits
		c.append('SQRT_Y_DAG', dq)
		c.append('TICK')
		# applies R_Y(+π/2) to ancilla qubits
		c.append('SQRT_Y', xa + za)
		c.append('TICK')

		# CNOT neighbors
		off = [
			{'dx': 1, 'dy': 0},
			{'dx': 0, 'dy': 1},
			{'dx': 0, 'dy': -1},
			{'dx': -1, 'dy': 0}
		]
		for nq in off:
			# S_X: X stabilizers
			cx = []
			for q in xa:
				y, x = divmod(q, D)
				tx, ty = x + nq['dx'], y + nq['dy']
				if 0 <= tx < D and 0 <= ty < D:
					cx.extend([q, qi(tx, ty)])
			c.append('CZ', cx)
			c.append('TICK')
		# applies R_Y(+π/2) to data qubits
		c.append('SQRT_Y', dq)
		c.append('TICK')
		for nq in off:
			# S_Z: Z stabilizers
			cx = []
			for q in za:
				y, x = divmod(q, D)
				tx, ty = x + nq['dx'], y + nq['dy']
				if 0 <= tx < D and 0 <= ty < D:
					cx.extend([qi(tx, ty), q])
			c.append('CZ', cx)
			c.append('TICK')

		# applies R_Y(-π/2) to ancilla qubits
		c.append('SQRT_Y_DAG', xa + za)
		c.append('TICK')
		# measures ancilla qubits
		c.append('MR', xa + za)
		for i, q in enumerate(xa + za):
			y, x = divmod(q, D)
			if ri == 0:
				if q in xa:
					c.append('DETECTOR', [stim.target_rec(-na + i)], [x, y, ri])
			else:
				c.append('DETECTOR', [stim.target_rec(-na + i),
									  stim.target_rec(-2 * na + i)], [x, y, ri])
		c.append('TICK')

	# Final Measurement and detection
	if mode == 'X':
		c.append('MX', dq)
		# Compare X-measurements against the X-ancillas
		for i, q in enumerate(xa):
			y, x = divmod(q, D)
			rec = []
			for nq in off:
				tx, ty = x + nq['dx'], y + nq['dy']
				if 0 <= tx < D and 0 <= ty < D:
					rec.append(stim.target_rec(-nd + dq.index(qi(tx, ty))))
			# Find the position of this specific ancilla inside the final (xa+za) MR block
			j = (xa + za).index(q)
			rec.append(stim.target_rec(-nd - na + j))
			c.append('DETECTOR', rec, [x, y, r])

		# Logical X runs horizontally
		xL = [qi(0, y) for y in range(0, D, 2)]
		rec = [stim.target_rec(-nd + dq.index(q)) for q in xL]
		c.append('OBSERVABLE_INCLUDE', rec, 0)
	else:
		c.append('M', dq)
		# Compare Z-measurements against the Z-ancillas
		for i, q in enumerate(za):
			y, x = divmod(q, D)
			rec = []
			for nq in off:
				tx, ty = x + nq['dx'], y + nq['dy']
				if 0 <= tx < D and 0 <= ty < D:
					rec.append(stim.target_rec(-nd + dq.index(qi(tx, ty))))
			j = (xa + za).index(q)
			rec.append(stim.target_rec(-nd - na + j))
			c.append('DETECTOR', rec, [x, y, r])

		# Logical Z runs vertically
		zL = [qi(x, 0) for x in range(0, D, 2)]
		rec = [stim.target_rec(-nd + dq.index(q)) for q in zL]
		c.append('OBSERVABLE_INCLUDE', rec, 0)

	return c

if __name__ == '__main__':
	sc = gen_usc(3, 2, 'X')
	dem = sc.detector_error_model(decompose_errors=True)
	print('usc_mx\n', sc)
	print('dem\n', dem)
	#sc.diagram('timeslice-svg')
	svg = dem.diagram('matchgraph-svg')
	with open("a.svg", "w") as f:
		f.write(str(svg))

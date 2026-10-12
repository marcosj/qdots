import stim
from math import exp

def add_noise(circ, round=0, reset=0, gate=0, meas=0, eta=None, mem='x'):
    noisy = stim.Circuit()
    flat = circ.flattened()

    # Extract data qubits
    if round > 0:
        for op in reversed(flat):
            if op.name in ['M', 'MX']:
                dq = [t.value for t in op.targets_copy()]
                break
    #coords = circ.get_final_qubit_coordinates()

    for op in flat:
        trgts = op.targets_copy()

        # pre-op noise
        if meas > 0:
            match op.name:
                case 'MR' | 'M':
                    noisy.append('X_ERROR', trgts, meas)
                case 'MX':
                    noisy.append('Z_ERROR', trgts, meas)

        noisy.append(op)

        # post-op noise
        match op.name:
            # Resets
            case 'RX':
                if reset > 0:
                    noisy.append('Z_ERROR', trgts, reset)

            case 'R':
                if reset > 0:
                    noisy.append('X_ERROR', trgts, reset)
                if round > 0 and set([t.value for t in trgts]) != set(dq):
                    noisy.append('TICK')
                    if eta is not None:
                        # Biased noise: PAULI_CHANNEL_1(px, py, pz)
                        if mem == 'x':
                            px = py = round / (2 * (1 + eta))
                            pz = 2 * eta * px  # pz = eta * round / (1 + eta)
                        else:
                            py = pz = round / (2 * (1 + eta))
                            px = 2 * eta * pz  # px = eta * round / (1 + eta)
                        noisy.append('PAULI_CHANNEL_1', dq, [px, py, pz])
                    else:
                        # Symmetric depolarizing noise
                        noisy.append('DEPOLARIZE1', dq, round)

            case 'MR':
                if meas > 0:
                    noisy.append('X_ERROR', trgts, meas)

            # Gates
            case 'H' | 'SQRT_Y' | 'SQRT_Y_DAG':
                if gate > 0:
                    noisy.append('DEPOLARIZE1', trgts, gate)

            case 'CX' | 'CZ':
                if gate > 0:
                    noisy.append('DEPOLARIZE2', trgts, gate)

    return noisy

# Noise in quantum dots
def qdot(circ, ld, st, eta=None):
    noisy = stim.Circuit()
    flat = circ.flattened()

    # Get all qubit indices
    allq = set(circ.get_final_qubit_coordinates().keys())

    # Extract data qubits (dq) from the final readout
    #dq = set()
    for op in reversed(flat):
        if op.name in ['M', 'MX']:
            dq = {t.value for t in op.targets_copy() if t.is_qubit_target}
            break

    # Ancilla qubits (aq)
    aq = allq - dq

    # Idle noise probabilities based on Gaussian decay model: p = 0.5 * (1 - exp(-(t/t2)^2))
    p = lambda t, t2: 0.5 * (1.0 - exp(- (t / t2) ** 2))

    # Idle probabilities during 2-qubit gate duration max(t2q)
    max_t2q = max(ld['t2q'], st['t2q'])
    pidq = p(max_t2q, ld['t2'])
    piaq = p(max_t2q, st['t2'])

    # Idle probabilities during measurement duration tr
    pird = p(st['tr'], ld['t2'])  # dq idling while ancillae measure
    pira = p(ld['tr'], st['t2'])  # aq idling while data measures

    for op in flat:
        trgts = op.targets_copy()
        trgtn = {t.value for t in trgts if t.is_qubit_target}

        # Pre-op noise (Readout errors)
        match op.name:
            case 'MR':
                noisy.append('X_ERROR', trgts, st['pr'])
                noisy.append('Z_ERROR', allq - trgtn, pird)
            case 'M':
                noisy.append('X_ERROR', trgts, ld['pr'])
                noisy.append('Z_ERROR', allq - trgtn, pira)
            case 'MX':
                noisy.append('Z_ERROR', trgts, ld['pr'])
                noisy.append('Z_ERROR', allq - trgtn, pira)

        noisy.append(op)

        # Post-op noise (Resets, Gates, idles)
        match op.name:
            case 'RX':
                noisy.append('Z_ERROR', trgts, ld['pp'])
            case 'R':
                noisy.append('X_ERROR', [q for q in trgtn if q in dq], ld['pp'])
                noisy.append('X_ERROR', [q for q in trgtn if q in aq], st['pp'])
            case 'MR':
                noisy.append('X_ERROR', trgts, st['pp'])

            case 'SQRT_Y' | 'SQRT_Y_DAG' | 'H':
                noisy.append('Y_ERROR', [q for q in trgtn if q in dq], ld['p1q'])
                noisy.append('Y_ERROR', [q for q in trgtn if q in aq], st['p1q'])

            case 'CZ' | 'CX':
                for i in range(0, len(trgts), 2):
                    noisy.append('PAULI_CHANNEL_2', [trgts[i], trgts[i+1]],
                                 [0,0,0, 0,0,0, 0,0,0, 0,0,0, 0,0, ld['p2q']])
                idle = allq - trgtn
                noisy.append('Z_ERROR', [q for q in idle if q in dq], pidq)
                noisy.append('Z_ERROR', [q for q in idle if q in aq], piaq)

    return noisy

if __name__ == '__main__':
    from ..conf import TMP_DIR, ld, st
    c = stim.Circuit.generated('surface_code:rotated_memory_x', distance=3, rounds=3)
    n = qdot(c, ld, st)
    n.to_file(TMP_DIR / 'noisy.stim')

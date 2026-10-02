import stim

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

if __name__ == '__main__':
    import sys
    sys.path.append('..')  # Add parent directory to Python path
    from gen.gen_sc_rot_mz import gen_sc_rot_mz  # Adjust module path relative to parent
    c = gen_sc_rot_mz(3, 1)
    n = add_noise(c,.1, eta=30)
    n.to_file("d3ours.stim")
    dem = n.detector_error_model(decompose_errors=True)
    # Print DEM errors caused by Z noise
    for i in dem:
        if "pz" in str(i) or "error" in str(i):
            print(i)

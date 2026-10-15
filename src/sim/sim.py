from noi.add_noise import add_noise, qdot
from conf import TMP_DIR
#from mwpf import SinterMWPFDecoder
import time
import os
import numpy as np
import stim
import sinter

def gen_tasks(circgen, dists, probs, rounds, dq, aq, rnd=False, rst=False, gate=False, meas=False, eta=None, mem='x', debug=False):
    # Noiseless circuits
    less = {}
    for d in dists:
        if rounds == '1':
          rlist = [1]
        elif rounds == 'd':
          rlist = [d]
        elif rounds == '2d':
          rlist = list(range(1, 2 * dists[-1] + 1))
        for r in rlist:
            less[(d, r)] = circgen(d, r)    #.flattened()

    # Noisy circuits
    for (d, r), circ in less.items():
        for p in probs:
            if dq:
                noisy = qdot(circ, dq, aq, eta)
            else:
                ro = p if rnd else 0
                re = p if rst else 0
                ga = p if gate else 0
                me = p if meas else 0
                noisy = add_noise(circ, ro, re, ga, me, eta, mem)
            if debug:
                path = TMP_DIR / f'noisy_d{d}_r{r}_p{p:.5f}.stim'
                noisy.to_file(path)
            yield sinter.Task(
                circuit=noisy,
                json_metadata={
                    'd': d, 'r': r, 'p': float(p)
                },
            )

def sim(tasks, fname, shots=100_000, max_errors=500, cores=4, clear_history=False):
    if clear_history and os.path.exists(fname):
        os.remove(fname)

    t = time.time()
    '''tasks = gen_tasks(
        circgen=circgen,
        dists=dists,
        probs=probs,
        rounds=rounds,
        rnd=rnd,
        rst=rst,
        gate=gate,
        meas=meas,
        eta=eta
    )'''

    stats = sinter.collect(
        num_workers=cores,
        tasks=tasks,
        decoders=['pymatching'],   # mwpf, fusion_blossom, pymatching
        max_shots=shots,
        max_errors=max_errors,
        save_resume_filepath=fname,
        #custom_decoders = {'mwpf': SinterMWPFDecoder(cluster_node_limit=50)}
    )
    t = time.time() - t
    print(f'Elapsed: {int(t // 60)}m{t % 60:.1f}s')
    return stats

def load(fname):
    return sinter.read_stats_from_csv_files(fname)

if __name__ == '__main__':
    geoms = ['rotated']
    bases = ['Z', 'X']
    dists = [3, 5, 7, 9]
    num_samples = 20
    p_e = np.geomspace(1e-4, 5e-2, num_samples)
    rounds = [3, 5, 7]  # None == [d]
    fname = 'surface_code_sweep.csv'
    def gen_bs_cx(geo, basis, d, r):
        # basic dummy circuit
        c = stim.Circuit()
        c.append("QUBIT_COORDS", [0], [2, 2])
        c.append("R", [0])
        c.append("M", [0])
        return c
    print("Starting simulation sweep...")
    stats = sim(gen_bs_cx, fname, geoms, bases, dists, p_e, rounds)
    print(f"Sweep complete! Processed {len(stats)} tracking rows.")

from conf import CSV_DIR, PNG_DIR, DEFAULT_SHOTS
from gen import gen_bs_cx, gen_usc_cz
from gen import gen_xzzx_rot_mz, gen_xzzx_rot_mx, gen_sc_rot_mz, gen_sc_rot_mx
from noi import add_noise
from sim import sim, load, gen_tasks
from viz import plot, bias
import numpy as np
#import matplotlib.pyplot as plt
import stim

def gen_sc_rot_mz_craig(d, r):
    return stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=r,
            distance=d
        )

'''
p_{h.b.} is the root of
1 - H(p_I,p_x,p_y,p_z) = 0
Shannon entropy: H(p) = -sum p_i lg p_i
1 + p_I lg p_I + 2 p_x lg p_x + p_z lg p_z = 0
1 + (1 - p) lg(1 - p) + p / (η + 1) lg p / 2(η + 1) + ηp / (η + 1) lg ηp / (η + 1) = 0
'''

def run(gen, di=3, df=9, ds=2, pi=10e-2, pf=None, ps=20, rounds=None,
        rnd=False, rst=False, gate=False, meas=False, eta=None, mem='x',
        fname=None, title=None, sweep='p', shots=10**4, errors=500, reset=True):
    d = [*range(di, df+1, ds)]
    p = np.geomspace(pi, pf, ps) if pf else [pi]
    r = [rounds] if rounds else [*range(1, 2*dmax+1)]
    tasks = gen_tasks(gen, d, p, r, rnd, rst, gate, meas, eta, mem)
    csv = CSV_DIR / f'{fname}.csv'
    stats = sim(tasks, csv, shots=shots, max_errors=errors, clear_history=reset)
    png = PNG_DIR / f'{fname}.png'
    p_th = plot(stats, title=title, path=png)
    print(f'{p_th}')

def phenoi(gen, filt, titt, filf, titf):
    simt = CSV_DIR / f'{filt}.csv'
    path = PNG_DIR / f'{filt}.png'
    d = [3,5,7,9]
    pi, pf, ps = 7e-3, 5e-2, 25
    p = np.geomspace(pi, pf, ps)
    r = [9]
    sh = 10**6
    stats = sim(gen, simt, d, p, r, rnd=True, meas=True, shots=sh, max_errors=1000, clear_history=True)
    plot(stats, title=f'{titt} (r={r[0]})', path=path)

    simf = CSV_DIR / f'{filf}.csv'
    pafi = PNG_DIR / f'{filf}.png'
    p = [0.008]
    r = [*range(1,2*d[-1])]
    stats = sim(gen, simf, d, p, r, rnd=True, meas=True, shots=sh, max_errors=1000, clear_history=True)
    plot(stats, sweep='r', title=f'{titf} (p={p[0]})', path=pafi)

def cirlev2():
    simt = CSV_DIR / 'bs_cz_cl_th.csv'
    path = PNG_DIR / 'bs_cz_cl_th.png'
    d = [3,5,7,9]
    pi, pf, ps = 5e-4, 1e-2, 20
    p = np.geomspace(pi, pf, ps)
    r = [9]
    sh = 2**17
    stats = sim(gen_bs_cx, simt, 'cz', 'z', d, p, r, rst=True, gate=True, meas=True, shots=sh, max_errors=100)
    plot(stats, title='Bacon-Shor circuit level threshold', path=path)

    simf = CSV_DIR / 'bs_cz_cl_fi.csv'
    pafi = PNG_DIR / 'bs_cz_cl_fi.png'
    p = [0.001]
    r = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    stats = sim(gen_bs_cx, simf, 'cz', 'z', d, p, r, rst=True, gate=True, meas=True, shots=sh, max_errors=100)
    plot(stats, sweep='r', title='Bacon-Shor circuit level fidelity', path=pafi)

def cirlev(gen, filt, titt, filf, titf, pi, pf, ps, po, shots=10**6, errors=1000, reset=True):
    simt = CSV_DIR / f'{filt}.csv'
    path = PNG_DIR / f'{filt}.png'
    d = [3,5,7,9]
    p = np.geomspace(pi, pf, ps)
    r = [9]
    stats = sim(gen, simt, d, p, r, rst=True, gate=True, meas=True, shots=shots, max_errors=errors, clear_history=reset)
    plot(stats, title=f'{titt} (r={r[0]})', path=path)

    simf = CSV_DIR / f'{filf}.csv'
    pafi = PNG_DIR / f'{filf}.png'
    r = [*range(1,2*d[-1])]
    stats = sim(gen, simf, d, [po], r, rst=True, gate=True, meas=True, shots=shots, max_errors=errors, clear_history=reset)
    plot(stats, sweep='r', title=f'{titf} (p={po})', path=pafi)

r'''
Model / Bias                        Hashing / Capacity      Optimal ML Decoder          MWPM (PyMatching)
Depolarizing ($\eta = 0.5$)         $\approx 18.9\%$        $\approx 18.7\%$            $\approx 15.5\%$
CSS High-Bias ($\eta \to \infty$)   $\approx 10.9\%$        $\approx 10.8\%$            $\approx 9.9\%$
'''

def main():
    codcap = [True, False, False, False]
    cirlev = [False, True, True, True]
    d = [25, 37, 12]
    p_c = []
    xp = {
        'xz_mx_e0': [gen_xzzx_rot_mz, *d, 12e-2, 19e-2, 5, 1, *codcap, .5, 'x', 'xz_mx_e0', 'XZZX code capacity (eta=1/2)','p'],
        'xz_mx_e1': [gen_xzzx_rot_mz, *d, 16e-2, 24e-2, 5, 1, *codcap, 1, 'x', 'xz_mx_e1', 'XZZX code capacity (eta=1)', 'p'],
        'xz_mx_e3': [gen_xzzx_rot_mz, *d, 35e-2, 45e-2, 5, 1, *codcap, 3, 'x', 'xz_mx_e3', 'XZZX code capacity (eta=3)', 'p'],
        'xz_mx_e10': [gen_xzzx_rot_mz, *d, 47e-2, 50e-2, 5, 1, *codcap, 10, 'x', 'xz_mx_e10', 'XZZX code capacity (eta=10)', 'p'],
        'xz_mx_e30': [gen_xzzx_rot_mz, *d, 35e-2, 48e-2, 5, 1, *codcap, 30, 'x', 'xz_mx_e30', 'XZZX code capacity (eta=30)', 'p'],
        'xz_mx_e100': [gen_xzzx_rot_mz, *d, 35e-2, 48e-2, 5, 1, *codcap, 100, 'x', 'xz_mx_e100', 'XZZX code capacity (eta=100)', 'p'],
        'xz_e0': [gen_xzzx_rot_mz, 9, 7e-2, 2e-2, 20, 1, *codcap, .5, 'z', 'xz_e0', 'XZZX code capacity (eta=1/2)','p'],
        'xz_e1': [gen_xzzx_rot_mz, 9, 8e-2, 3.2e-2, 20, 1, *codcap, 1, 'z', 'xz_e1', 'XZZX code capacity (eta=1)', 'p'],
        'xz_e3': [gen_xzzx_rot_mz, 9, 8e-2, 3.2e-2, 20, 1, *codcap, 3, 'z', 'xz_e3', 'XZZX code capacity (eta=3)', 'p'],
        'xz_e10': [gen_xzzx_rot_mz, 9, 1.5e-2, 4e-2, 20, 1, *codcap, 10, 'z', 'xz_e10', 'XZZX code capacity (eta=10)', 'p'],
        'xz_e30': [gen_xzzx_rot_mz, 9, 2.5e-2, 5.5e-2, 20, 1, *codcap, 30, 'z', 'xz_e30', 'XZZX code capacity (eta=30)', 'p'],
        'sc_e0': [gen_sc_rot_mz, 9, 9e-2, 30e-2, 20, 1, *codcap, .5, 'z', 'sc_e0', 'Surface code code capacity (eta=1/2)','p'],
        'sc_e1': [gen_sc_rot_mz, 9, 9e-2, 30e-2, 20, 1, *codcap, 1, 'z', 'sc_e1', 'Surface code code capacity (eta=1)', 'p'],
        'sc_e3': [gen_sc_rot_mz, 9, 8e-2, 60e-2, 20, 1, *codcap, 3, 'z', 'sc_e3', 'Surface code code capacity (eta=3)', 'p'],
        'sc_e10': [gen_sc_rot_mz, 9, 8e-2, 20e-2, 20, 1, *codcap, 10, 'z', 'sc_e10', 'Surface code code capacity (eta=10)', 'p'],
        'sc_e30': [gen_sc_rot_mz, 9, 7e-2, 15e-2, 30, 1, *codcap, 30, 'z', 'sc_e30', 'Surface code code capacity (eta=30)', 'p'],
        'sc_e100': [gen_sc_rot_mz, 9, 7e-2, 15e-2, 30, 1, *codcap, 100, 'z', 'sc_e100', 'Surface code code capacity (eta=100)', 'p'],
        'sc_mx_e0': [gen_sc_rot_mx, 9, 9e-2, 30e-2, 20, 1, *codcap, .5, 'x', 'sc_mx_e0', 'Surface code memX code capacity (eta=1/2)','p'],
        'sc_mx_e1': [gen_sc_rot_mx, 9, 9e-2, 30e-2, 20, 1, *codcap, 1, 'x', 'sc_mx_e1', 'Surface code memX code capacity (eta=1)', 'p'],
        'sc_mx_e3': [gen_sc_rot_mx, 9, 8e-2, 60e-2, 20, 1, *codcap, 3, 'x', 'sc_mx_e3', 'Surface code memX code capacity (eta=3)', 'p'],
        'sc_mx_e10': [gen_sc_rot_mx, 9, 8e-2, 20e-2, 20, 1, *codcap, 10, 'x', 'sc_mx_e10', 'Surface code memX code capacity (eta=10)', 'p'],
        'sc_mx_e30': [gen_sc_rot_mx, 9, 7e-2, 15e-2, 30, 1, *codcap, 30, 'x', 'sc_mx_e30', 'Surface code memX code capacity (eta=30)', 'p'],
        'sc_mx_e100': [gen_sc_rot_mx, 9, 7e-2, 15e-2, 30, 1, *codcap, 100, 'x', 'sc_mx_e100', 'Surface code memX code capacity (eta=100)', 'p'],
        'sc_cc': [gen_sc_rot_mz, 9, 2e-2, 3e-1, 20, 1, *codcap, 'sc_cc', 'Surface code capacity threshold', 'p'],
        'sccl': [gen_sc_rot_mz, 'sc_cl_th', 'Surface circuit level threshold', 'sc_cl_fi', 'Surface circuit level fidelity', 5e-3, 3e-2, 20, 0.009, 10**5, 500],
        'xzcc': [gen_xzzx_rot_mz, 'xz_cc', 'XZZX code capacity threshold', 2e-2, 3e-1, 20],
        'xzcl': [gen_xzzx_rot_mz, 'xz_cl_th', 'XZZX circuit level threshold', 'xz_cl_fi', 'XZZX circuit level fidelity', 5e-4, 1e-2, 20, 0.0009, 10**6, 1000],
        'bscc': [gen_bs_cx, 'bs_cc', 'Bacon-Shor capacity threshold', 9e-3, 3e-1, 20],
        'bscl': [gen_bs_cx, 'bs_cl_th', 'Bacon-Shor circuit level threshold', 'bs_cl_fi', 'Bacon-Shor circuit level fidelity', 1e-3, 7e-3, 20, 0.0015, 10**5, 1000],
    }
    #codcap(*xp['bscc'])
    #run(*xp['xz_mx_e10'])
    eta = [.5, 1, 3, 10, 30, 100]
    p_c_sc_z = [0.13985321363686604, 0.1259493011211646, 0.11079478398646855, 0.09645308386339203, 0.09542599989093375, 0.0972472327536627]
    p_sc_mx = [0.1413598942781524, 0.12709453946432944, 0.1068022013543007, 0.10098255200981622, 0.09579212340424623, 0.09104029006940331]
    p_xz_mx = [0.14232311627333294, 0.1837878368826132, 0.3650184972586271, None, None, None]     # [3, 9, 12]
    p_xz_mx2 = [0.1495255516848949, 0.2007257409614447, 0.4024511367410391, None, None, None]     # [13, 25, 12]
    p_xz_mx3 = [0.15524649388399522, 0.1943616476209687, 0.392083761910609, None, None, None]     # [25, 37, 12]
    p_xz_mx4 = []
    bias(eta, p_sc_mx, p_xz_mx3, PNG_DIR / 'bias_sc_mx.png')
    #codcap(gen_bs_cx, 'bs_sim.csv', 'bs_cz_cc_th.png', 'Bacon-Shor code capacity threshold')
    #phenoi(gen_xzzx_rot_mz, 'xz_pn_th', 'XZZX phenomenological threshold', 'xz_pn_fi', 'XZZX phenomenological fidelity')
    #phenoi(gen_bs_cx, 'bs_cz_pn_th.csv', 'bs_cz_pn_th.png', 'Bacon-Shor phenomenological threshold',
    #    'bs_cz_pn_fi.csv', 'bs_cz_pn_fi.png', 'Bacon-Shor phenomenological fidelity')
    #cirlev(gen_usc_cz, 'sc_cz_cl_th', 'Surface code circuit level threshold', 'sc_cz_cl_fi', 'Surface code circuit level fidelity')
    #imprimir diagrama rot sc - ya
    #con mem Z - ya
    #agregar p a fidelity - ya
    #todos qubits LD
    #con readout time / 10
    # per round plot
    #px = p/2(1+eta)
    #pz = eta p / (1+eta)
    #p = sum pi

if __name__ == "__main__":
    main()

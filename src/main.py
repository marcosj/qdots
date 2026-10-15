from conf import CSV_DIR, PNG_DIR, DEFAULT_SHOTS, ld, st
from gen import gen_bs_mz
from gen import gen_xzzx_rot_mz, gen_xzzx_rot_mx, gen_sc_rot_mz, gen_sc_rot_mx
from noi import add_noise, qdot
from sim import sim, load, gen_tasks
from viz import plot, bias
import sys
import numpy as np
from dataclasses import dataclass
from typing import Callable

@dataclass
class Args:
    gen: Callable
    di: int = 3
    df: int = 9
    ds: int = 2
    pi: float = 10
    pf: float | None = None
    ps: int = 20
    rounds: str = 'd'
    dq: dict | None = None
    aq: dict | None = None
    rnd: bool = False
    rst: bool = False
    gate: bool = False
    meas: bool = False
    eta: float | None = None
    mem: str = 'x'
    fname: str = 'dummy'
    title: str = ''
    sweep: str = 'p'
    shots: int = 10**5
    errors: int = 1000
    reset: bool = True
    debug: bool = False

def run(a: Args):
    d = list(range(a.di, a.df + 1, a.ds))
    p = np.geomspace(a.pi, a.pf, a.ps) / 100 if a.pf else [a.pi / 100]
    #r = [a.rounds] if a.rounds else [*range(1, 2 * a.df + 1)]
    tasks = gen_tasks(a.gen, d, p, a.rounds, a.dq, a.aq, a.rnd, a.rst, a.gate, a.meas, a.eta, a.mem, a.debug)
    csv = CSV_DIR / f'{a.fname}.csv'
    stats = sim(tasks, csv, shots=a.shots, max_errors=a.errors, clear_history=a.reset)
    png = PNG_DIR / f'{a.fname}.png'
    p_th = plot(stats, sweep=a.sweep, title=a.title, path=png)
    print(f'{p_th}')
    return p_th

r'''
Model / Bias                        Hashing / Capacity      Optimal ML Decoder          MWPM (PyMatching)
Depolarizing ($\eta = 0.5$)         $\approx 18.9\%$        $\approx 18.7\%$            $\approx 15.5\%$
CSS High-Bias ($\eta \to \infty$)   $\approx 10.9\%$        $\approx 10.8\%$            $\approx 9.9\%$
'''
def main():
    codcap = { 'rounds': '1', 'rnd': True }
    cirlev = { 'rst': True, 'gate': True, 'meas': True, 'debug': False }
    d9 = { 'di': 3, 'df': 9, 'ds': 2 }
    d25 = { 'di': 13, 'df': 25, 'ds': 4 }
    d37 = { 'di': 25, 'df': 37, 'ds': 4 }
    sczcl = { 'gen': gen_sc_rot_mz, **d9, **cirlev }
    sczcc = { 'gen': gen_sc_rot_mz, **d9, **codcap }
    scxcl = { 'gen': gen_sc_rot_mx, **d9, **cirlev }
    scxcc = { 'gen': gen_sc_rot_mx, **d9, **codcap }
    bszcl = { 'gen': gen_bs_mz, **d9, **cirlev, 'shots': 10**6, 'errors': 2000 }
    bszcc = { 'gen': gen_bs_mz, **d9, **codcap }
    xzzcl = { 'gen': gen_xzzx_rot_mz, **d9, **cirlev }
    xzzcc = { 'gen': gen_xzzx_rot_mz, **d9, **codcap }
    xzxcl = { 'gen': gen_xzzx_rot_mx, **d9, **cirlev, 'shots': 10**4, 'errors': 500 }
    xzxcc = { 'gen': gen_xzzx_rot_mx, **d9, **codcap }
    xp = {
        'sczth': { **sczcl, 'pi': .5, 'pf': 2, 'fname': 'scz_th', 'title': 'Surface code memZ circuit level threshold' },
        'sczfi': { **sczcl, 'pi': .6, 'rounds': '2d', 'sweep': 'r', 'fname': 'scz_fi', 'title': 'Surface code memZ circuit level fidelity' },
        'scxth': { **scxcl, 'pi': .5, 'pf': 2, 'fname': 'scx_th', 'title': 'Surface code memX circuit level threshold' },
        'scxfi': { **scxcl, 'pi': .6, 'rounds': '2d', 'sweep': 'r', 'fname': 'scx_fi', 'title': 'Surface code circuit memX level fidelity' },
        'bszth': { **bszcl, 'pi': .1, 'pf': .5, 'fname': 'bsz_th', 'title': 'Bacon-Shor circuit level threshold' },
        'bszfi': { **bszcl, 'pi': .1, 'rounds': '2d', 'sweep': 'r', 'fname': 'bsz_fi', 'title': 'Bacon-Shor circuit level fidelity' },
        'scz0': { **sczcc, 'pi': 9, 'pf': 30, 'eta': .5, 'fname': 'scz_e0', 'title': 'Surface code code capacity (η=½)' },
        'scz1': { **sczcc, 'pi': 9, 'pf': 30, 'eta': 1, 'fname': 'scz_e1', 'title': 'Surface code code capacity (η=1)' },
        'scz2': { **sczcc, 'pi': 10, 'pf': 40, 'eta': 2, 'fname': 'scz_e2', 'title': 'Surface code code capacity (η=2)' },
        'scz3': { **sczcc, 'pi': 8, 'pf': 60, 'eta': 3, 'fname': 'scz_e3', 'title': 'Surface code code capacity (η=3)' },
        'scz5': { **sczcc, 'pi': 30, 'pf': 70, 'eta': 5, 'fname': 'scz_e5', 'title': 'Surface code code capacity (η=5)' },
        'scz100': { **sczcc, 'pi': 7, 'pf': 15, 'eta': 100, 'fname': 'scz_e100', 'title': 'Surface code code capacity (η=100)' },
        'xzz0': { **xzzcc, 'pi': 7, 'pf': 20, 'eta': .5, 'fname': 'xzz_e0', 'title': 'XZZX code capacity (η=½)' },
        'xzz1': { **xzzcc, 'pi': 8, 'pf': 32, 'eta': 1, 'fname': 'xzz_e1', 'title': 'XZZX code capacity (η=1)' },
        'xzz2': { **xzzcc, 'pi': 15, 'pf': 40, 'eta': 2, 'fname': 'xzz_e2', 'title': 'XZZX code capacity (η=2)' },
        'xzz3': { **xzzcc, 'pi': 20, 'pf': 50, 'eta': 3, 'fname': 'xzz_e3', 'title': 'XZZX code capacity (η=3)' },
        'xzz5': { **xzzcc, 'pi': 30, 'pf': 70, 'eta': 5, 'fname': 'xzz_e5', 'title': 'XZZX code capacity (η=5)' },
        'scx0': { **scxcc, 'pi': 9, 'pf': 30, 'eta': .5, 'fname': 'scx_e0', 'title': 'Surface code memX code capacity (η=½)' },
        'scx1': { **scxcc, 'pi': 9, 'pf': 30, 'eta': 1, 'fname': 'scx_e1', 'title': 'Surface code memX code capacity (η=1)' },
        'scx3': { **scxcc, 'pi': 8, 'pf': 60, 'eta': 3, 'fname': 'scx_e3', 'title': 'Surface code memX code capacity (η=3)' },
        'scx10': { **scxcc, 'pi': 8, 'pf': 20, 'eta': 10, 'fname': 'scx_e10', 'title': 'Surface code memX code capacity (η=10)' },
        'scx30': { **scxcc, 'pi': 7, 'pf': 15, 'eta': 30, 'fname': 'scx_e30', 'title': 'Surface code memX code capacity (η=30)' },
        'scx100': { **scxcc, 'pi': 7, 'pf': 15, 'eta': 100, 'fname': 'scx_e100', 'title': 'Surface code memX code capacity (η=100)' },
        'xzx0': { **xzxcc, 'pi': 12, 'pf': 19, 'eta': .5, 'fname': 'xzx_e0', 'title': 'XZZX code capacity (η=½)' },
        'xzx1': { **xzxcc, 'pi': 16, 'pf': 24, 'eta': 1, 'fname': 'xzx_e1', 'title': 'XZZX code capacity (η=1)' },
        'xzx3': { **xzxcc, 'pi': 35, 'pf': 45, 'eta': 3, 'fname': 'xzx_e3', 'title': 'XZZX code capacity (η=3)' },
        'xzx10': { **xzxcc, 'pi': 47, 'pf': 50, 'eta': 10, 'fname': 'xzx_e10', 'title': 'XZZX code capacity (η=10)' },
        'xzx30': { **xzxcc, 'pi': 35, 'pf': 48, 'eta': 30, 'fname': 'xzx_e30', 'title': 'XZZX code capacity (η=30)' },
        'xzx100': { **xzxcc, 'pi': 35, 'pf': 48, 'eta': 100, 'fname': 'xzx_e100', 'title': 'XZZX code capacity (η=100)' },
        'bsz0': { **bszcc, 'pi': 1.5, 'pf': 7, 'eta': .5, 'fname': 'bsz_e0', 'title': 'Bacon-Shor code capacity (η=½)' },
        'bsz1': { **bszcc, 'pi': 2, 'pf': 7, 'eta': 1, 'mem': 'z', 'fname': 'bsz_e1', 'title': 'Bacon-Shor code capacity (η=1)' },
        'bsz3': { **bszcc, 'pi': 1, 'pf': 6, 'eta': 3, 'mem': 'z', 'fname': 'bsz_e3', 'title': 'Bacon-Shor code capacity (η=3)' },
        'bsz10': { **bszcc, 'pi': .9, 'pf': 5, 'eta': 10, 'mem': 'z', 'fname': 'bsz_e10', 'title': 'Bacon-Shor code capacity (η=10)' },
        'bsz30': { **bszcc, 'pi': .9, 'pf': 4, 'eta': 30, 'mem': 'z', 'fname': 'bsz_e30', 'title': 'Bacon-Shor code capacity (η=30)' },
        'bsz100': { **bszcc, 'pi': .9, 'pf': 4, 'eta': 100, 'mem': 'z', 'fname': 'bsz_e100', 'title': 'Bacon-Shor code capacity (η=100)' },
        'xzzth': { **xzzcl, 'pi': .05, 'pf': .2, 'fname': 'xzz_th', 'title': 'XZZX threshold circuit level noise' },
        'xzqth': { **xzzcl, 'pi': .05, 'pf': .2, 'fname': 'xzq_th', 'title': 'XZZX threshold real noise' },
        'xzzfi': { **xzzcl, 'pi': .9, 'rounds': '2d', 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'xzz_fi', 'title': 'XZZX fidelity real noise' },
        'zxzth': { **bszcl, 'pi': .1, 'pf': .5, 'dq': ld, 'aq': st, 'fname': 'zxz_th', 'title': 'XZZX Bacon-Shor threshold real noise' },
        'zxzfi': { **bszcl, 'pi': .15, 'rounds': '2d', 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'zxz_fi', 'title': 'XZZX Bacon-Shor fidelity real noise' },
    }
    #run(Args(**xp[sys.argv[1]]))
    #quit()
    if len(sys.argv) == 1:
        eta = [.5, 1, 3, 10, 30, 100]
        p_c_sc_z = [0.13985321363686604, 0.1259493011211646, 0.11079478398646855, 0.09645308386339203, 0.09542599989093375, 0.0972472327536627]
        p_sc_mx = [0.1413598942781524, 0.12709453946432944, 0.1068022013543007, 0.10098255200981622, 0.09579212340424623, 0.09104029006940331]
        p_xz_mx = [0.14232311627333294, 0.1837878368826132, 0.3650184972586271, None, None, None]     # [3, 9, 12]
        p_xz_mx2 = [0.1495255516848949, 0.2007257409614447, 0.4024511367410391, None, None, None]     # [13, 25, 12]
        p_xz_mx3 = [0.15524649388399522, 0.1943616476209687, 0.392083761910609, None, None, None]     # [25, 37, 12]
        p_xz_mx4 = []
        eta = [.5, 1, 2, 3, 5]
        scz = [0.1417611209358204, 0.18774341010618173, 0.2916077319153026, 0.38567013450092313, 0.56454132213293]
        xzz = [0.13566037652629326, 0.17736467374028722, 0.2860873230133435, 0.3929751351502915, 0.5977063006599191]
        eta = [.5, 1, 3, 10, 30, 100]
        zxz = [None]*6
        bsz = [0.038018165997960596, 0.03464704070955221, 0.028689948056820343, 0.026738051498766187, 0.02637361894038132, 0.025570694549471508]
        bias(eta, bsz, zxz, PNG_DIR / 'zxz_eta.png')
    elif len(sys.argv) == 2:
        variant = sys.argv[1]
        config = xp.get(variant)
        if config is None:
            print(f"❌ Error: Variant '{variant}' not found in xp dict.")
            sys.exit(1)
        run(Args(**config))

if __name__ == "__main__":
    main()
    #todos qubits LD
    #con readout time / 10

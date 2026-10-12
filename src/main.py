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
    rounds: int | None = None
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
    shots: int = 10**6
    errors: int = 2000
    reset: bool = True

def run(a: Args):
    d = list(range(a.di, a.df + 1, a.ds))
    p = np.geomspace(a.pi, a.pf, a.ps) / 100 if a.pf else [a.pi / 100]
    r = [a.rounds] if a.rounds else [*range(1, 2 * a.df + 1)]
    tasks = gen_tasks(a.gen, d, p, r, a.dq, a.aq, a.rnd, a.rst, a.gate, a.meas, a.eta, a.mem)
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
    codcap = { 'rounds': 1, 'rnd': True }
    cirlev = { 'rst': True, 'gate': True, 'meas': True }
    d9 = { 'di': 3, 'df': 9, 'ds': 2 }
    d25 = { 'di': 13, 'df': 25, 'ds': 4 }
    d37 = { 'di': 25, 'df': 37, 'ds': 4 }
    sczcl = { 'gen': gen_sc_rot_mz, **d9, **cirlev }
    sczcc = { 'gen': gen_sc_rot_mz, **d9, **codcap }
    scxcl = { 'gen': gen_sc_rot_mx, **d9, **cirlev }
    scxcc = { 'gen': gen_sc_rot_mx, **d9, **codcap }
    bszcl = { 'gen': gen_bs_mz, **d9, **cirlev }
    bszcc = { 'gen': gen_bs_mz, **d9, **codcap }
    xzzcl = { 'gen': gen_xzzx_rot_mz, **d9, **cirlev }
    xzzcc = { 'gen': gen_xzzx_rot_mz, **d9, **codcap }
    xzxcl = { 'gen': gen_xzzx_rot_mx, **d9, **cirlev }
    xzxcc = { 'gen': gen_xzzx_rot_mx, **d9, **codcap }
    xp = {
        'sczth': { **sczcl, 'pi': .8, 'pf': 5, 'rounds': 9, 'fname': 'scz_th', 'title': 'Surface code circuit level threshold' },
        'sczfi': { **sczcl, 'pi': .9, 'sweep': 'r', 'fname': 'scz_fi', 'title': 'Surface code circuit level fidelity' },
        'bszth': { **bszcl, 'pi': .1, 'pf': .5, 'rounds': 9, 'fname': 'bsz_th', 'title': 'Bacon-Shor circuit level threshold' },
        'bszfi': { **bszcl, 'pi': .15, 'sweep': 'r', 'fname': 'bsz_fi', 'title': 'Bacon-Shor circuit level fidelity' },
        'scz0': { **sczcc, 'pi': 9, 'pf': 30, 'eta': .5, 'fname': 'scz_e0', 'title': 'Surface code code capacity (η=½)' },
        'scz1': { **sczcc, 'pi': 9, 'pf': 30, 'eta': 1, 'fname': 'scz_e1', 'title': 'Surface code code capacity (η=1)' },
        'scz3': { **sczcc, 'pi': 8, 'pf': 60, 'eta': 3, 'fname': 'scz_e3', 'title': 'Surface code code capacity (η=3)' },
        'scz10': { **sczcc, 'pi': 8, 'pf': 20, 'eta': 10, 'fname': 'scz_e10', 'title': 'Surface code code capacity (η=10)' },
        'scz30': { **sczcc, 'pi': 7, 'pf': 15, 'eta': 30, 'fname': 'scz_e30', 'title': 'Surface code code capacity (η=30)' },
        'scz100': { **sczcc, 'pi': 7, 'pf': 15, 'eta': 100, 'fname': 'scz_e100', 'title': 'Surface code code capacity (η=100)' },
        'xzz0': { **xzzcc, 'pi': 7, 'pf': 2, 'eta': .5, 'fname': 'xzz_e0', 'title': 'XZZX code capacity (η=½)' },
        'xzz1': { **xzzcc, 'pi': 8, 'pf': 3.2, 'eta': 1, 'fname': 'xzz_e1', 'title': 'XZZX code capacity (η=1)' },
        'xzz3': { **xzzcc, 'pi': 8, 'pf': 3.2, 'eta': 3, 'fname': 'xzz_e3', 'title': 'XZZX code capacity (η=3)' },
        'xzz10': { **xzzcc, 'pi': 1.5, 'pf': 4, 'eta': 10, 'fname': 'xzz_e10', 'title': 'XZZX code capacity (η=10)' },
        'xzz30': { **xzzcc, 'pi': 2.5, 'pf': 5.5, 'eta': 30, 'fname': 'xzz_e30', 'title': 'XZZX code capacity (η=30)' },
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
        'bsz1': { **bszcc, 'pi': 2, 'pf': 7, 'eta': 1, 'fname': 'bsz_e1', 'title': 'Bacon-Shor code capacity (η=1)' },
        'bsz3': { **bszcc, 'pi': 8, 'pf': 50, 'eta': 3, 'fname': 'bsz_e3', 'title': 'Bacon-Shor code capacity (η=3)' },
        'bsz10': { **bszcc, 'pi': 8, 'pf': 50, 'eta': 10, 'fname': 'bsz_e10', 'title': 'Bacon-Shor code capacity (η=10)' },
        'bsz30': { **bszcc, 'pi': 7, 'pf': 50, 'eta': 30, 'fname': 'bsz_e30', 'title': 'Bacon-Shor code capacity (η=30)' },
        'bsz100': { **bszcc, 'pi': 7, 'pf': 50, 'eta': 100, 'fname': 'bsz_e100', 'title': 'Bacon-Shor code capacity (η=100)' },
        'xzzth': { **xzzcl, 'pi': .8, 'pf': 5, 'rounds': 9, 'dq': ld, 'aq': st, 'fname': 'xzz_th', 'title': 'XZZX threshold real noise' },
        'xzzfi': { **xzzcl, 'pi': .9, 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'xzz_fi', 'title': 'XZZX fidelity real noise' },
        'zxzth': { **bszcl, 'pi': .1, 'pf': .5, 'rounds': 9, 'dq': ld, 'aq': st, 'fname': 'zxz_th', 'title': 'XZZX Bacon-Shor threshold real noise' },
        'zxzfi': { **bszcl, 'pi': .15, 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'zxz_fi', 'title': 'XZZX Bacon-Shor fidelity real noise' },
    }
    run(Args(**xp[sys.argv[1]]))
    if len(sys.argv) == 1:
        eta = [.5, 1, 3, 10, 30, 100]
        p_c_sc_z = [0.13985321363686604, 0.1259493011211646, 0.11079478398646855, 0.09645308386339203, 0.09542599989093375, 0.0972472327536627]
        p_sc_mx = [0.1413598942781524, 0.12709453946432944, 0.1068022013543007, 0.10098255200981622, 0.09579212340424623, 0.09104029006940331]
        p_xz_mx = [0.14232311627333294, 0.1837878368826132, 0.3650184972586271, None, None, None]     # [3, 9, 12]
        p_xz_mx2 = [0.1495255516848949, 0.2007257409614447, 0.4024511367410391, None, None, None]     # [13, 25, 12]
        p_xz_mx3 = [0.15524649388399522, 0.1943616476209687, 0.392083761910609, None, None, None]     # [25, 37, 12]
        p_xz_mx4 = []
        bias(eta, p_sc_mx, p_xz_mx3, PNG_DIR / 'bias_sc_mx.png')
    elif len(sys.argv) == 2:
        variant = sys.argv[1]
        config = xp.get(variant)
        if config is None:
            print(f"❌ Error: Variant '{variant}' not found in xp dict.")
            sys.exit(1)
        run(*config)

if __name__ == "__main__":
    main()
    #todos qubits LD
    #con readout time / 10

from conf import CSV_DIR, PNG_DIR, IMG_DIR, ld, st
from gen import gen_bs_mz, gen_bs2_mz, gen_bs2_zxxz
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
    skip: bool = False

def run(a: Args):
    csv = CSV_DIR / f'{a.fname}.csv'
    if a.skip:
        stats = load(csv)
    else:
        d = list(range(a.di, a.df + 1, a.ds))
        p = np.geomspace(a.pi, a.pf, a.ps) / 100 if a.pf else [a.pi / 100]
        #r = [a.rounds] if a.rounds else [*range(1, 2 * a.df + 1)]
        eta = a.eta if isinstance(a.eta, list) else [a.eta]
        tasks = gen_tasks(a.gen, d, p, a.rounds, a.dq, a.aq, a.rnd, a.rst, a.gate, a.meas, eta, a.mem, a.debug)
        stats = sim(tasks, csv, shots=a.shots, max_errors=a.errors, clear_history=a.reset)
    img = IMG_DIR / f'{a.fname}.svg'
    title = a.title if a.pf else f'{a.title} (p={a.pi})'
    p_th = plot(stats, sweep=a.sweep, title=title, path=img)
    if p_th: print(f'{p_th}')
    return p_th

r'''
Model / Bias                        Hashing / Capacity      Optimal ML Decoder          MWPM (PyMatching)
Depolarizing ($\eta = 0.5$)         $\approx 18.9\%$        $\approx 18.7\%$            $\approx 15.5\%$
CSS High-Bias ($\eta \to \infty$)   $\approx 10.9\%$        $\approx 10.8\%$            $\approx 9.9\%$
'''
def main():
    codcap = { 'rounds': '1', 'rnd': True, 'skip': False }
    cirlev = { 'rst': True, 'gate': True, 'meas': True, 'debug': False, 'skip': False }
    d9 = { 'di': 3, 'df': 9, 'ds': 2 }
    d25 = { 'di': 13, 'df': 25, 'ds': 4 }
    d37 = { 'di': 25, 'df': 37, 'ds': 4 }
    sczcl = { 'gen': gen_sc_rot_mz, **d9, **cirlev }
    sczcc = { 'gen': gen_sc_rot_mz, **d9, **codcap }
    scxcl = { 'gen': gen_sc_rot_mx, **d9, **cirlev }
    scxcc = { 'gen': gen_sc_rot_mx, **d9, **codcap }
    bszcl = { 'gen': gen_bs_mz, **d9, **cirlev, 'shots': 10**7, 'errors': 4000 }
    bszcc = { 'gen': gen_bs2_mz, **d9, **codcap }
    zxzcc = { 'gen': gen_bs2_zxxz, **d9, **codcap }
    xzzcl = { 'gen': gen_xzzx_rot_mz, **d9, **cirlev }
    xzzcc = { 'gen': gen_xzzx_rot_mz, **d9, **codcap }
    xzxcl = { 'gen': gen_xzzx_rot_mx, **d9, **cirlev, 'shots': 10**6, 'errors': 2000 }
    xzxcc = { 'gen': gen_xzzx_rot_mx, **d9, **codcap }
    xp = {
        'sczth': { **sczcl, 'pi': .5, 'pf': 2, 'fname': 'scz_th', 'title': 'Surface code memZ circuit level threshold' },
        'sczfi': { **sczcl, 'pi': .6, 'rounds': '2d', 'sweep': 'r', 'fname': 'scz_fi', 'title': 'Surface code memZ circuit level fidelity' },
        'scxth': { **scxcl, 'pi': .5, 'pf': 2, 'fname': 'scx_th', 'title': 'Surface code memX circuit level threshold' },
        'scxfi': { **scxcl, 'pi': .6, 'rounds': '2d', 'sweep': 'r', 'fname': 'scx_fi', 'title': 'Surface code circuit memX level fidelity' },
        'bszth': { **bszcl, 'pi': .1, 'pf': .5, 'fname': 'bsz_th', 'title': 'Bacon-Shor circuit level threshold' },
        'bszfi': { **bszcl, 'pi': .1, 'rounds': '2d', 'sweep': 'r', 'fname': 'bsz_fi', 'title': 'Bacon-Shor circuit level fidelity' },
        'scz0': { **sczcc, 'pi': 9, 'pf': 30, 'eta': .5, 'mem': 'z', 'fname': 'scz_e0', 'title': 'Surface code code capacity (η=½)' },
        'scz1': { **sczcc, 'pi': 9, 'pf': 30, 'eta': 1, 'mem': 'z', 'fname': 'scz_e1', 'title': 'Surface code code capacity (η=1)' },
        'scz3': { **sczcc, 'pi': 8, 'pf': 30, 'eta': 3, 'mem': 'z', 'fname': 'scz_e3', 'title': 'Surface code code capacity (η=3)' },
        'scz10': { **sczcc, 'pi': 8, 'pf': 20, 'eta': 10, 'mem': 'z', 'fname': 'scz_e10', 'title': 'Surface code code capacity (η=10)' },
        'scz30': { **sczcc, 'pi': 7, 'pf': 20, 'eta': 30, 'mem': 'z', 'fname': 'scz_e30', 'title': 'Surface code code capacity (η=30)' },
        'scz100': { **sczcc, 'pi': 7, 'pf': 20, 'eta': 100, 'mem': 'z', 'fname': 'scz_e100', 'title': 'Surface code code capacity (η=100)' },
        'scx0': { **scxcc, 'pi': 9, 'pf': 30, 'eta': .5, 'mem': 'z', 'fname': 'scx_e0', 'title': 'Surface code memX code capacity (η=½)' },
        'scx1': { **scxcc, 'pi': 9, 'pf': 30, 'eta': 1, 'fname': 'scx_e1', 'title': 'Surface code memX code capacity (η=1)' },
        'scx3': { **scxcc, 'pi': 8, 'pf': 20, 'eta': 3, 'fname': 'scx_e3', 'title': 'Surface code memX code capacity (η=3)' },
        'scx10': { **scxcc, 'pi': 8, 'pf': 20, 'eta': 10, 'fname': 'scx_e10', 'title': 'Surface code memX code capacity (η=10)' },
        'scx30': { **scxcc, 'pi': 7, 'pf': 15, 'eta': 30, 'fname': 'scx_e30', 'title': 'Surface code memX code capacity (η=30)' },
        'scx100': { **scxcc, 'pi': 7, 'pf': 15, 'eta': 100, 'fname': 'scx_e100', 'title': 'Surface code memX code capacity (η=100)' },
        'bsz0': { **bszcc, 'pi': 1.5, 'pf': 7, 'eta': .5, 'mem': 'z', 'fname': 'bsz_e0', 'title': 'Bacon-Shor code capacity (η=½)' },
        'bsz1': { **bszcc, 'pi': 2, 'pf': 7, 'eta': 1, 'mem': 'z', 'fname': 'bsz_e1', 'title': 'Bacon-Shor code capacity (η=1)' },
        'bsz3': { **bszcc, 'pi': 1, 'pf': 6, 'eta': 3, 'mem': 'z', 'fname': 'bsz_e3', 'title': 'Bacon-Shor code capacity (η=3)' },
        'bsz10': { **bszcc, 'pi': .9, 'pf': 5, 'eta': 10, 'mem': 'z', 'fname': 'bsz_e10', 'title': 'Bacon-Shor code capacity (η=10)' },
        'bsz30': { **bszcc, 'pi': .9, 'pf': 4, 'eta': 30, 'mem': 'z', 'fname': 'bsz_e30', 'title': 'Bacon-Shor code capacity (η=30)' },
        'bsz100': { **bszcc, 'pi': .9, 'pf': 4, 'eta': 100, 'mem': 'z', 'fname': 'bsz_e100', 'title': 'Bacon-Shor code capacity (η=100)' },
        'xzz0': { **xzzcc, 'pi': 7, 'pf': 20, 'eta': .5, 'fname': 'xzz_e0', 'title': 'XZZX code capacity (η=½)' },
        'xzz1': { **xzzcc, 'pi': 8, 'pf': 32, 'eta': 1, 'fname': 'xzz_e1', 'title': 'XZZX code capacity (η=1)' },
        'xzz2': { **xzzcc, 'pi': 15, 'pf': 40, 'eta': 2, 'fname': 'xzz_e2', 'title': 'XZZX code capacity (η=2)' },
        'xzz3': { **xzzcc, 'pi': 20, 'pf': 50, 'eta': 3, 'fname': 'xzz_e3', 'title': 'XZZX code capacity (η=3)' },
        'xzz5': { **xzzcc, 'pi': 30, 'pf': 70, 'eta': 5, 'fname': 'xzz_e5', 'title': 'XZZX code capacity (η=5)' },
        'xzx0': { **xzxcc, 'pi': 8, 'pf': 25, 'eta': .5, 'mem': 'z', 'fname': 'xzx_e0', 'title': 'XZZX code capacity (η=½)' },
        'xzx1': { **xzxcc, 'pi': 9, 'pf': 40, 'eta': 1, 'mem': 'z', 'fname': 'xzx_e1', 'title': 'XZZX code capacity (η=1)' },
        'xzx2': { **xzxcc, 'pi': 10, 'pf': 40, 'eta': 2, 'mem': 'z', 'fname': 'xzx_e2', 'title': 'XZZX code capacity (η=2)' },
        'xzx3': { **xzxcc, 'pi': 20, 'pf': 50, 'eta': 3, 'mem': 'z', 'fname': 'xzx_e3', 'title': 'XZZX code capacity (η=3)' },
        'xzx5': { **xzxcc, 'pi': 30, 'pf': 70, 'eta': 5, 'mem': 'z', 'fname': 'xzx_e5', 'title': 'XZZX code capacity (η=5)' },
        'xzx100': { **xzxcc, 'pi': 40, 'pf': 80, 'eta': 100, 'mem': 'z', 'fname': 'xzx_e100', 'title': 'XZZX code capacity (η=100)' },
        'zxz0': { **zxzcc, 'pi': 1.5, 'pf': 7, 'eta': .5, 'fname': 'zxz_e0', 'title': 'BS ZXXZ code capacity (η=½)' },
        'zxz1': { **zxzcc, 'pi': 2, 'pf': 15, 'eta': 1, 'fname': 'zxz_e1', 'title': 'BS ZXXZ code capacity (η=1)' },
        'zxz2': { **zxzcc, 'pi': 5, 'pf': 25, 'eta': 2, 'fname': 'zxz_e2', 'title': 'BS ZXXZ code capacity (η=2)' },
        'zxz3': { **zxzcc, 'pi': 5, 'pf': 25, 'eta': 3, 'fname': 'zxz_e3', 'title': 'BS ZXXZ code capacity (η=3)' },
        'zxz5': { **zxzcc, 'pi': 5, 'pf': 25, 'eta': 5, 'fname': 'zxz_e5', 'title': 'BS ZXXZ code capacity (η=5)' },
        'zxz10': { **zxzcc, 'pi': 10, 'pf': 40, 'eta': 10, 'fname': 'zxz_e10', 'title': 'BS ZXXZ code capacity (η=10)' },
        'zxz30': { **zxzcc, 'pi': 35, 'pf': 70, 'eta': 20, 'fname': 'zxz_e30', 'title': 'BS ZXXZ code capacity (η=20)' },
        'zxz100': { **zxzcc, 'pi': 30, 'pf': 60, 'eta': 100, 'fname': 'zxz_e100', 'title': 'BS ZXXZ code capacity (η=100)' },
        'xzzth': { **xzzcl, 'pi': .05, 'pf': .2, 'fname': 'xzz_th', 'title': 'XZZX threshold circuit level noise' },
        'xzqth': { **xzzcl, 'pi': .05, 'pf': .2, 'dq': ld, 'aq': st, 'fname': 'xzq_th', 'title': 'XZZX threshold real noise' },
        'scqth': { **scxcl, 'pi': .4, 'pf': 1, 'dq': ld, 'aq': st, 'fname': 'scq_th', 'title': 'SC memX threshold real noise' },
        'xzzfi': { **xzzcl, 'pi': .01, 'rounds': '2d', 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'xzz_fi', 'title': 'XZZX fidelity real noise' },
        'xzxfi': { **xzxcl, 'pi': .01, 'rounds': '2d', 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'xzx_fi', 'title': 'XZZX fidelity real noise' },
        'xzxbi': { **xzxcl, 'sweep': 'eta', 'eta': [.5, 1, 3, 10, 30], 'dq': ld, 'aq': st, 'fname': 'xzx_bi', 'title': 'XZZX memX real noise' },
        'xzzbi': { **xzzcl, 'sweep': 'eta', 'eta': [.5, 1, 3, 10, 30], 'dq': ld, 'aq': st, 'fname': 'xzz_bi', 'title': 'XZZX memZ real noise' },
        'zxzbi': { **bszcl, 'sweep': 'eta', 'eta': [.5, 1, 3, 10, 30], 'dq': ld, 'aq': st, 'fname': 'zxz_bi', 'title': 'B-S real noise' },
        'zxzth': { **bszcl, 'pi': 6, 'pf': 45, 'dq': ld, 'aq': st, 'fname': 'zxz_th', 'title': 'XZZX Bacon-Shor threshold real noise' },
        'zxzfi': { **bszcl, 'pi': .15, 'rounds': '2d', 'sweep': 'r', 'dq': ld, 'aq': st, 'fname': 'zxz_fi', 'title': 'XZZX Bacon-Shor fidelity real noise' },
    }
    if len(sys.argv) == 1:
        p_sc_mz = [0.13985321363686604, 0.1259493011211646, 0.11079478398646855, 0.09645308386339203, 0.09542599989093375, 0.0972472327536627]
        p_sc_mx = [0.1413598942781524, 0.12709453946432944, 0.1068022013543007, 0.10098255200981622, 0.09579212340424623, 0.09104029006940331]
        p_xz_mx = [0.14232311627333294, 0.1837878368826132, 0.3650184972586271, None, None, None]     # [3, 9, 12]
        p_xz_mx2 = [0.1495255516848949, 0.2007257409614447, 0.4024511367410391, None, None, None]     # [13, 25, 12]
        p_xz_mx3 = [0.15524649388399522, 0.1943616476209687, 0.392083761910609, None, None, None]     # [25, 37, 12]
        p_xz_mx4 = []
        eta0 = [.5, 1, 3, 10, 30, 100]
        eta1 = [.5, 1, 2, 3, 5]
        eta2 = [.5, 1, 3, 10, 20]
        scz = [0.1417611209358204, 0.18774341010618173, 0.2916077319153026, 0.38567013450092313, 0.56454132213293]
        scz = [0.14961519690496228, 0.12826596878000174, 0.10384830464251618, 0.0961654802524303, 0.09571803624183392, 0.09609040280942507]
        scx = [0.15078491460723228, 0.1273188432399462, 0.10900359453459263, 0.10221421283052234, 0.09744709600225226, 0.0918379236294599]
        bsz = [0.038018165997960596, 0.03464704070955221, 0.028689948056820343, 0.026738051498766187, 0.02637361894038132, 0.025570694549471508]
        xzz = [0.14247883976140674, 0.19651284354310997, 0.2894570438710485, 0.3930659771618724, 0.5574723978394587]
        xzx = [0.13566037652629326, 0.17736467374028722, 0.2860873230133435, 0.3929751351502915, 0.5977063006599191]
        zxz = [0.038354563758788325, 0.05085781854098201, 0.10179043393512349, 0.2816142801669332, 0.5154433380303763]
        xyz = [[(eta0, scz), (eta1, xzz)], 'xzz_eta.svg']
        xyx = [[(eta0, scx), (eta1, xzx)], 'xzx_eta.svg']
        xyb = [[(eta0, bsz), (eta2, zxz)], 'zxz_eta.svg']
        bias(xyz[0], IMG_DIR / xyz[1])
        bias(xyx[0], IMG_DIR / xyx[1])
        bias(xyb[0], IMG_DIR / xyb[1])
    elif len(sys.argv) == 2:
        variant = sys.argv[1]
        config = xp.get(variant)
        if config is None:
            print(f"Error: Variant '{variant}' not found in xp dict.")
            print(xp.keys())
            sys.exit(1)
        run(Args(**config))

if __name__ == "__main__":
    main()
    #todos qubits LD
    #con readout time / 10

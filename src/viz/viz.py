import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import sinter

def plot(stats, sweep='p', title='Surface Code Performance', legend_title='d', path=None):
    """
    Plots sinter error rates generic to sweeping physical error rates ('p') or rounds ('r').

    Parameters:
    -----------
    stats : list
        The stats collected or loaded from sinter.
    sweep_type : str
        'p' to plot Logical Error Rate vs Physical Error Rate (log-log style).
        'r' to plot Logical Error Rate vs Rounds (semilogy style).
    title : str
        Main title for the plot.
    legend_title : str
        Label title for the legend grouping (typically code distance 'd').
    save_path : str, optional
        File path to save the generated figure (e.g., 'plot.png').
    """
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    p_th = None

    if sweep == 'p':
        # --- Plot Style 1: Sweep Physical Error Rates ---
        sinter.plot_error_rate(
            ax=ax,
            stats=stats,
            x_func=lambda s: s.json_metadata['p'],
            group_func=lambda s: s.json_metadata['d'],
            failure_units_per_shot_func=lambda s: s.json_metadata['r']
        )
        ax.set_xscale('log')
        ax.set_xlabel('Physical Error Rate, p')

        # --- Automatic Threshold Crossing Calculation ---
        # 1. Aggregate logical error rates per shot from stats
        grid = {}
        p_vals = set()
        d_vals = set()

        for s in stats:
            p = s.json_metadata['p']
            d = s.json_metadata['d']
            r = s.json_metadata.get('r', 1)

            p_vals.add(p)
            d_vals.add(d)

            # Match Sinter's per-shot error rate scaling
            ler_per_shot = (s.errors / s.shots) / r if s.shots > 0 else 0
            grid[(p, d)] = ler_per_shot

        # 2. Linear interpolation across min(d) and max(d)
        sorted_p = sorted(p_vals)
        sorted_d = sorted(d_vals)
        d_min, d_max = sorted_d[0], sorted_d[-1]

        valid_p = [p for p in sorted_p if (p, d_min) in grid and (p, d_max) in grid]
        diffs = [grid[(p, d_max)] - grid[(p, d_min)] for p in valid_p]

        crossing_idx = np.where(np.diff(np.sign(diffs)))[0]
        if len(crossing_idx) > 0:
            idx = crossing_idx[0]
            p1, p2 = valid_p[idx], valid_p[idx + 1]
            y1, y2 = diffs[idx], diffs[idx + 1]
            p_th = p1 - y1 * (p2 - p1) / (y2 - y1)
        else:
            p_th = valid_p[np.argmin(np.abs(diffs))]

        # 3. Add vertical line for threshold
        ax.axvline(
            x=p_th,
            color='black',
            linestyle='--',
            linewidth=1.5,
            label=f'$p_{{th}} \\approx$ {p_th:.1%}'
        )

    elif sweep == 'r':
        # --- Plot Style 2: Sweep Round Count ---
        sinter.plot_error_rate(
            ax=ax,
            stats=stats,
            x_func=lambda s: s.json_metadata['r'],
            group_func=lambda s: s.json_metadata['d'],
            failure_units_per_shot_func=lambda s: s.json_metadata['r']
        )
        ax.set_xlabel('Rounds')
        # Dynamic ticks based on integer round data found in metadata
        r_vals = {s.json_metadata['r'] for s in stats if 'r' in s.json_metadata}
        if r_vals:
            ax.set_xticks(sorted(list(r_vals)))

    else:
        raise ValueError("sweep_type must be either 'p' (physical error rate) or 'r' (rounds).")

    # --- Plot Aesthetics ---
    ax.set_yscale('log')
    ax.set_title(title)
    ax.set_ylabel('Logical Error Rate per Shot')

    ax.grid(visible=True, which='major', linestyle='-', linewidth=0.7)
    ax.grid(visible=True, which='minor', linestyle=':', linewidth=0.5)

    ax.legend(title=legend_title, loc='best')
    fig.tight_layout()

    if path:
        fig.savefig(path, dpi=300)
        print(f"Plot saved to: {path}")
        plt.close(fig)

    return p_th     # fig, ax

def entropy_gap(p, eta):
    # Calculates 1 - H(p_I, p_x, p_y, p_z) for a given error rate p and bias eta.
    if p <= 0 or p >= 1:
        return 1

    # Error probabilities
    px = py = p / 2 / (eta + 1)
    pz = eta * p / (eta + 1)
    pI = 1 - p

    probs = np.array([pI, px, py, pz])

    # 1 - Shannon entropy
    return 1.0 + np.sum(probs * np.log2(probs))

def hashing_bound(etas):
    # Computes p_hb for each eta in etas
    p_hb = []
    for eta in etas:
        # Finds the root where entropy gap = 0 in the range (0, 0.5)
        sol = brentq(entropy_gap, 1e-6, 0.4999, args=(eta,))
        p_hb.append(sol)
    return np.array(p_hb)

def bias(eta, css, xzzx, path):
    etas = np.logspace(np.log10(0.5), np.log10(1000), 100)
    p_hb = hashing_bound(etas)
    plt.semilogx(etas, p_hb, 'k-', linewidth=1.25, label='$p_{h.b.}$')
    plt.semilogx(eta, css, 'ro:', label='CSS')
    plt.semilogx(eta, xzzx, 'bo:', label='XZZX')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.xlabel(r'Bias: $\eta$')
    plt.ylabel('Treshold error rate: $p_c$')
    plt.legend(loc='best')
    plt.savefig(path, dpi=300)
    #plt.show()
    plt.close()

if __name__ == '__main__':
    # Load CSV statistics
    stats = sinter.read_stats_from_csv_files('surface_code_sweep.csv')

    # Plot Logical vs Physical error rate (threshold intersection check)
    plot(
        stats=stats,
        sweep_type='p',
        title='XZZX Rotated Memory Threshold',
        save_path='threshold_sweep.png'
    )

    # Plot Logical error rate decay vs Code Rounds
    plot(
        stats=stats,
        sweep_type='r',
        title='Error Accumulation Across Rounds',
        save_path='rounds_sweep.png'
    )

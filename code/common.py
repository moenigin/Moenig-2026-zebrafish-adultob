"""Shared constants and plotting helpers for the figure scripts."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

# Paths are relative to the repository root, so scripts run from anywhere.
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"

# Principal neuron (PN) classes in plotting order, with x tick labels.
PN_CLASSES = ["MC_small", "MC_intermediate", "MC_large", "RC"]
PN_LABELS = ["small\nMC", "med.\nMC", "large\nMC", "RC"]
PN_PALETTE = dict(zip(PN_CLASSES, sns.color_palette("tab10", len(PN_CLASSES))))


def set_style():
    """Plot style (replaces the former local 'thesis' style sheet)."""
    plt.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,                # editable text in PDF export
    })


def class_panel(ax, df, column, ylabel, exponent=None, swarm_size=3):
    """Violin + notched box + swarm of one feature per PN class.

    exponent: fixed power of ten shown as offset above the y axis
    (e.g. 3 -> 'x10^3'); None keeps matplotlib's automatic choice.
    """
    common = dict(data=df, x="type_detail", y=column, order=PN_CLASSES,
                  hue="type_detail", hue_order=PN_CLASSES, palette=PN_PALETTE,
                  legend=False, ax=ax)
    sns.violinplot(linewidth=0, **common)
    for violin in ax.collections:
        violin.set_alpha(.6)
    sns.boxplot(fliersize=0, showcaps=False, notch=True, linewidth=.75,
                boxprops=dict(alpha=.75), **common)
    sns.swarmplot(size=swarm_size, edgecolor="0.5", **common)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(PN_LABELS)))
    ax.set_xticklabels(PN_LABELS)
    if exponent is not None:
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis="y", style="sci",
                            scilimits=(exponent, exponent))

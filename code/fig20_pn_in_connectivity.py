"""Fig. 20: synaptic connectivity between interneuron (IN) classes and principal neurons (PN).

Every IN was assessed against all mitral cells (MC) and ruffed cells (RC) that
have dendrites in the glomeruli the IN innervates (data/in_glomerulus_map.csv,
data/pn_glomeruli.csv). A pair counts as connected if at least one annotated
synapse with certainty >= 3 links the two neurons (data/synapse_annotations.csv;
reciprocity = 1 marks the two synapses of a reciprocal contact).
Connected pairs are typed as

    reciprocal   a synapse flagged as reciprocal, or synapses in both directions
    input to IN  synapses from the PN onto the IN only
    IN output    synapses from the IN onto the PN only

Per PN type (MC, RC) the script makes three figures: the number of synapses per
connected pair, the fraction of connected PNs per IN and glomerulus, and the
fractions of the connection types, all per IN class. The number of assessed and
connected pairs per class is printed.

Input:  data/in_glomerulus_map.csv, data/pn_glomeruli.csv,
        data/synapse_annotations.csv,
        data/plin1_rc_pairs.csv (additional IN-RC pairs assessed for PLIN1; only
                                INs listed in the IN map are used)
Usage:  python code/fig20_pn_in_connectivity.py            # show the figures
        python code/fig20_pn_in_connectivity.py --save DIR # also save them
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from common import DATA_DIR, set_style

MIN_CERTAINTY = 3
OVERLAY_FILE = DATA_DIR / "plin1_rc_pairs.csv"

CLASS_ORDER = ["GLIN1", "GLIN2", "GLIN3", "GLIN4", "PLIN1", "PLIN2", "PLIN3_v",
               "PLIN3_rl", "PLIN4", "DLIN1_r", "DLIN1_l", "DLIN1_s", "DLIN2_c",
               "DLIN2_f", "DLIN2_s", "DLIN3"]
CLASS_COLORS = ["#94F761", "#32CD32", "#228B22", "#01562C", "#87CEEB",
                "#00B1B5", "#4682B4", "#4682B4", "#2B3990", "#F15838",
                "#F15838", "#F15838", "#E81D2A", "#E81D2A", "#E81D2A",
                "#8B0000"]
CLASS_PALETTE = dict(zip(CLASS_ORDER, CLASS_COLORS))
TYPE_COLORS = {"reciprocal": "#6522B2", "input to IN": "#FCD203",
               "IN output": "#61686D"}
FIG_SIZE = (5, 7)


def plot_class(neuron_type):
    """IN class shown in the figure: PLIN4_a/b/c are summarised as PLIN4."""
    return "PLIN4" if neuron_type.startswith("PLIN4") else neuron_type


def count_synapses(synapses):
    """Number of synapses per (presynaptic neuron, postsynaptic neuron,
    reciprocity flag)."""
    return synapses.groupby(
        ["id_pre", "id_post", "reciprocity"]).size().to_dict()


def pair_record(counts, observation, in_id, in_class, glomerulus, pn_id,
                pn_class):
    """Synapse counts between one IN and one PN."""
    return {
        "observation": observation, "in_id": in_id, "in_class": in_class,
        "glomerulus": glomerulus, "pn_id": pn_id, "pn_class": pn_class,
        "n_reciprocal": counts.get((in_id, pn_id, 1), 0)
        + counts.get((pn_id, in_id, 1), 0),
        "n_input": counts.get((pn_id, in_id, 0), 0),    # PN presynaptic
        "n_output": counts.get((in_id, pn_id, 0), 0),   # IN presynaptic
    }


def connection_type(n_reciprocal, n_input, n_output):
    """Type of a connected pair, None if there is no synapse."""
    if n_reciprocal > 0 or (n_input > 0 and n_output > 0):
        return "reciprocal"
    if n_input > 0:
        return "input to IN"
    if n_output > 0:
        return "IN output"
    return None


def assess_glomeruli(in_map, pn, counts):
    """All IN-PN pairs within the glomeruli listed in the IN map.

    Each row of the map is one observation (IN, glomerulus). If a compartment
    is given, only PNs of that compartment (or of both, 'AB') are assessed.
    """
    records = []
    for observation, row in enumerate(in_map.itertuples(index=False)):
        pns = pn[pn["glomerulus"] == row.glomerulus]
        if isinstance(row.compartment, str) and row.compartment != "AB":
            pns = pns[pns["subcompartment"].isin([row.compartment, "AB"])]
        for pn_id, pn_type in zip(pns["neuron_id"], pns["neuron_type"]):
            records.append(pair_record(
                counts, observation, row.neuron_id, plot_class(row.neuron_type_specific),
                row.glomerulus, pn_id, pn_type[:2]))   # MC(_dendrite), RC(...)
    return pd.DataFrame(records)


def add_overlay_pairs(pairs, in_map, counts, overlay):
    """Add the IN-RC pairs that were assessed explicitly for PLIN1.

    PLIN1 contacts RCs outside the glomerular neuropil, so these pairs are
    assessed separately (data/plin1_rc_pairs.csv). Each IN of the overlay is
    one additional observation. .
    """
    class_of = in_map.drop_duplicates("neuron_id").set_index(
        "neuron_id")["neuron_type_specific"].map(plot_class)
    records, observation = [], pairs["observation"].max() + 1
    for in_id, rc_ids in overlay[overlay["in_neuron_id"].isin(class_of.index)
                                 ].groupby("in_neuron_id")["rc_neuron_id"]:
        for rc_id in rc_ids:
            records.append(pair_record(counts, observation, in_id,
                                       class_of[in_id], "overlay", rc_id,
                                       "RC"))
        observation += 1
    return pd.concat([pairs, pd.DataFrame(records)], ignore_index=True)


def analyse(data_dir=DATA_DIR):
    """Pair table with the synapse counts and the type of each pair."""
    in_map = pd.read_csv(data_dir / "in_glomerulus_map.csv")
    pn = pd.read_csv(data_dir / "pn_glomeruli.csv")
    synapses = pd.read_csv(data_dir / "synapse_annotations.csv")
    counts = count_synapses(synapses[synapses["certainty"] >= MIN_CERTAINTY])

    pairs = assess_glomeruli(in_map, pn, counts)
    # add Plin1 RC overlay
    pairs = add_overlay_pairs(pairs, in_map, counts,
                              pd.read_csv(OVERLAY_FILE))
    pairs["n_synapses"] = pairs[["n_reciprocal", "n_input", "n_output"]].sum(
        axis=1)
    pairs["type"] = [connection_type(*x) for x in zip(
        pairs["n_reciprocal"], pairs["n_input"], pairs["n_output"])]
    return pairs


def fraction_connected(pairs):
    """Fraction of connected PNs per observation (IN and glomerulus)."""
    grouped = pairs.assign(connected=pairs["n_synapses"] > 0).groupby(
        ["observation", "in_class"], as_index=False).agg(
        n_pairs=("connected", "size"), n_connected=("connected", "sum"))
    grouped["fraction"] = grouped["n_connected"] / grouped["n_pairs"]
    return grouped


def class_summary(pairs):
    """Assessed and connected pairs and fractions of the connection types per
    IN class."""
    summary = pd.DataFrame(index=CLASS_ORDER)
    summary["pairs"] = pairs.groupby("in_class").size()
    connected = pairs[pairs["type"].notna()]
    summary["connected"] = connected.groupby("in_class").size()
    types = connected.groupby(["in_class", "type"]).size().unstack(fill_value=0)
    for kind in TYPE_COLORS:
        summary[kind] = types[kind] if kind in types else 0
    summary = summary.fillna(0)
    summary[list(TYPE_COLORS)] = summary[list(TYPE_COLORS)].div(
        summary["connected"].replace(0, np.nan), axis=0)
    return summary


def plot_class_box(df, column, xlabel, title, xlim=None):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    sns.boxplot(data=df, y="in_class", x=column, order=CLASS_ORDER,
                hue="in_class", hue_order=CLASS_ORDER, palette=CLASS_PALETTE,
                legend=False, ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.set_title(title)
    if xlim is not None:
        ax.set_xlim(xlim)
    fig.tight_layout()
    return fig


def plot_connection_types(summary, title):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    y = np.arange(len(CLASS_ORDER))
    left = np.zeros(len(CLASS_ORDER))
    for kind, color in TYPE_COLORS.items():
        width = summary[kind].fillna(0).values
        ax.barh(y, width, left=left, color=color, label=kind, height=.8)
        left += width
    ax.set_yticks(y)
    ax.set_yticklabels(CLASS_ORDER)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("fraction of connection types")
    ax.set_title(title)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.12), ncol=3,
              frameon=False, fontsize="small", handlelength=1)
    fig.tight_layout()
    return fig


def main(save_dir=None):
    set_style()
    pairs = analyse()
    figures = {}
    for pn_class in ("MC", "RC"):
        sel = pairs[pairs["pn_class"] == pn_class]
        obs = fraction_connected(sel)
        summary = class_summary(sel)
        print(f"\nIN classes and {pn_class}s (fractions refer to connected "
              f"pairs):")
        print(summary.round(2).to_string())
        figures[f"fig20_n_synapses_{pn_class}"] = plot_class_box(
            sel[sel["n_synapses"] > 0], "n_synapses", "synapses / pair",
            f"synapses with {pn_class}s",
            xlim=(0, 25) if pn_class == "MC" else None)
        figures[f"fig20_fraction_connected_{pn_class}"] = plot_class_box(
            obs, "fraction", "fraction connected / glomerulus",
            f"{pn_class}s connected to an IN")
        figures[f"fig20_connection_types_{pn_class}"] = plot_connection_types(
            summary, f"{pn_class} connectivity")

    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        for name, fig in figures.items():
            for suffix in (".png", ".pdf"):
                fig.savefig(save_dir / f"{name}{suffix}", dpi=300,
                            bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--save", type=Path, metavar="DIR",
                        help="also save the figures as PNG and PDF to DIR")
    main(parser.parse_args().save)

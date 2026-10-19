"""Agreement between the expert classifications and the master classification.

Four experts (expert1-4) sorted neurons into groups, separately for
interneurons (IN) and principal neurons (PN). The master classification in
data/neuron_information.csv is the reference. For every pair of neurons we
count in how many of the five classifications (master + four experts) the
pair was placed in the same group. The counts are shown as a matrix with the
neurons ordered by master class.

Only neurons that were part of the expert classification task are analysed.
They are not listed separately but derived from the expert files: a neuron
counts as included if at least one expert placed it in any group.

Input:  data/neuron_information.csv
        data/expert_classification/{IN,PN}/*_neuron_classification_expert<N>.json
        (json: {group number: [segment ids]})
Usage:  python code/expert_classification_agreement.py            # show figures
        python code/expert_classification_agreement.py --save DIR # also save
"""
import argparse
import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

from common import DATA_DIR

EXPERT_DIR = DATA_DIR / "expert_classification"
EXPERTS = (1, 2, 3, 4)

# Group number each expert used for neurons they could not classify
# (None: the expert did not use such a group).
UNCLASSIFIABLE_GROUP = {
    "IN": {1: 0, 2: 15, 3: None, 4: 11},
    "PN": {1: None, 2: None, 3: None, 4: 5},
}

# Master classes shown in the figure (in plotting order) and the column of
# neuron_information.csv that holds them. Neurons the master classification
# could not assign ('unclassified') are part of the analysis but not shown.
MASTER_CLASSES = {
    "IN": ("neuron_type_broad",
           ["GLIN1", "GLIN2", "GLIN3", "GLIN4", "PLIN1", "PLIN2", "PLIN3",
            "PLIN4", "DLIN1", "DLIN2", "DLIN3"]),
    "PN": ("neuron_type_specific",
           ["MC_small", "MC_intermediate", "MC_large", "RC"]),
}
CELL_TYPE_NAMES = {"IN": "interneurons", "PN": "principal neurons"}


def load_expert_groups(cell_type, expert):
    """Read one expert's json file: {group number: [segment ids]}."""
    pattern = f"*_neuron_classification_expert{expert}.json"
    files = sorted((EXPERT_DIR / cell_type).glob(pattern))
    if len(files) != 1:
        raise FileNotFoundError(
            f"Expected exactly one file matching {pattern} in "
            f"{EXPERT_DIR / cell_type}, found {len(files)}.")
    with open(files[0], "r") as f:
        return {int(k): [int(s) for s in v] for k, v in json.load(f).items()}


def segments_to_neurons(groups, segment_to_neuron):
    """Translate segment ids to neuron ids.

    Returns the groups with neuron ids (duplicates within a group removed) and
    the set of segment ids that are not part of the neuron table.
    """
    neuron_groups, unknown = {}, set()
    for group, segments in groups.items():
        neurons = []
        for seg in segments:
            if seg not in segment_to_neuron:
                unknown.add(seg)
            elif segment_to_neuron[seg] not in neurons:
                neurons.append(segment_to_neuron[seg])
        neuron_groups[group] = neurons
    return neuron_groups, unknown


def assignment_graph(neurons):
    """Graph with one node per neuron and no edges."""
    graph = nx.Graph()
    graph.add_nodes_from(neurons)
    return graph


def add_edges(graph, groups, unclassifiable_group=None):
    """Connect all neurons that were placed in the same group.

    Neurons in the unclassifiable group stay unconnected.
    """
    for group, neurons in groups.items():
        if group == unclassifiable_group:
            continue
        graph.add_edges_from(combinations(neurons, 2), weight=1)
    return graph


def get_united_graph(graphs, neurons):
    """Union of several graphs; the edge weight is the number of graphs
    in which the edge occurs."""
    united = assignment_graph(neurons)
    for graph in graphs:
        for src, targ in graph.edges:
            if united.has_edge(src, targ):
                united.edges[src, targ]["weight"] += 1
            else:
                united.add_edge(src, targ, weight=1)
    return united


def plot_agreement_matrix(graph, master_groups, n_classifications, title):
    """Matrix of the edge weights, neurons ordered by master class."""
    order = [n for neurons in master_groups.values() for n in neurons]
    mat = nx.to_numpy_array(graph, nodelist=order)
    n = len(order)

    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    img = ax.imshow(mat, cmap="viridis", vmin=0, vmax=n_classifications,
                    interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.suptitle(title)
    cbar = fig.colorbar(img, ax=ax, ticks=range(n_classifications + 1),
                        fraction=0.046, pad=0.04)
    cbar.set_label("classifications with pair in same group")

    # colored bands marking the master classes on the left and top
    colors = plt.cm.Set3(np.linspace(0, 1, len(master_groups)))
    band, gap = 0.025 * n, 0.01 * n
    start = 0
    for color, neurons in zip(colors, master_groups.values()):
        size = len(neurons)
        ax.add_patch(Rectangle((-gap - band, start - .5), band, size,
                               facecolor=color, clip_on=False))
        ax.add_patch(Rectangle((start - .5, -gap - band - .5), size, band,
                               facecolor=color, clip_on=False))
        start += size
    handles = [Patch(facecolor=c, label=f"{name} (n={len(v)})")
               for c, (name, v) in zip(colors, master_groups.items())]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(1.0, .5),
               frameon=False, title="master class")
    return fig


def report_coverage(cell_type, included, expert_groups, segments_of):
    """Print how many neurons each expert classified and which neurons
    (segment ids) were included by other experts but are absent from an
    expert's classification."""
    print(f"\n{CELL_TYPE_NAMES[cell_type]}: {len(included)} neurons included "
          f"in the expert classification")
    for expert, groups in expert_groups.items():
        unclass = UNCLASSIFIABLE_GROUP[cell_type][expert]
        present = {n for ns in groups.values() for n in ns}
        n_unclass = len(groups.get(unclass, []))
        absent = sorted(included - present)
        print(f"  expert{expert}: {len(present)} neurons, "
              f"{n_unclass} unclassifiable, {len(absent)} absent")
        if absent:
            segments = [s for n in absent for s in segments_of[n]]
            print(f"    included by other experts only (segment ids): "
                  f"{segments}")


def load_classifications(info, cell_type):
    """Load the expert and master classifications of one cell type.

    Returns the sorted neuron ids included in the expert classification, the
    master groups {class: [neuron ids]} restricted to these neurons (classes
    without neurons dropped) and the expert groups {expert: {group: [ids]}}.
    """
    rows = info[info["neuron_type"] == cell_type]
    segment_to_neuron = dict(zip(rows["segment_id"], rows["neuron_id"]))
    segments_of = rows.groupby("neuron_id")["segment_id"].apply(list).to_dict()

    # expert classifications
    expert_groups = {}
    for expert in EXPERTS:
        groups = load_expert_groups(cell_type, expert)
        unclass = UNCLASSIFIABLE_GROUP[cell_type][expert]
        if unclass is not None and unclass not in groups:
            raise ValueError(
                f"expert{expert} ({cell_type}): unclassifiable group "
                f"{unclass} not found, groups are {sorted(groups)}")
        expert_groups[expert], unknown = segments_to_neurons(
            groups, segment_to_neuron)
        if unknown:
            print(f"Warning: expert{expert} ({cell_type}): {len(unknown)} "
                  f"segment ids not in neuron_information.csv were ignored: "
                  f"{sorted(unknown)}")

    # neurons that were part of the expert classification
    included = {n for groups in expert_groups.values()
                for ns in groups.values() for n in ns}
    report_coverage(cell_type, included, expert_groups, segments_of)

    # master classification (reference), restricted to the included neurons
    column, classes = MASTER_CLASSES[cell_type]
    master = rows.drop_duplicates("neuron_id")
    master = master[master["neuron_id"].isin(included)]
    master_groups = {c: master.loc[master[column] == c, "neuron_id"].tolist()
                     for c in classes}
    master_groups = {c: ns for c, ns in master_groups.items() if ns}
    n_shown = sum(len(ns) for ns in master_groups.values())
    print(f"  master classification: {n_shown} neurons in "
          f"{len(master_groups)} classes shown, "
          f"{len(included) - n_shown} included neurons without a master "
          f"class")
    return sorted(included), master_groups, expert_groups


def expert_graphs(cell_type, neurons, expert_groups):
    """One graph per expert; neurons placed in the same group are connected."""
    base = assignment_graph(neurons)
    return [add_edges(base.copy(), groups,
                      UNCLASSIFIABLE_GROUP[cell_type][expert])
            for expert, groups in expert_groups.items()]


def analyse(info, cell_type):
    """Build the agreement matrix for one cell type."""
    neurons, master_groups, expert_groups = load_classifications(
        info, cell_type)
    # one graph per classification (master first), united into one graph
    graphs = [add_edges(assignment_graph(neurons), master_groups)]
    graphs += expert_graphs(cell_type, neurons, expert_groups)
    united = get_united_graph(graphs, neurons)
    title = (f"{CELL_TYPE_NAMES[cell_type]}: agreement of master and "
             f"expert classifications")
    return plot_agreement_matrix(united, master_groups, len(graphs), title)


def main(save_dir=None):
    info = pd.read_csv(DATA_DIR / "neuron_information.csv")
    for cell_type in ("IN", "PN"):
        fig = analyse(info, cell_type)
        if save_dir is not None:
            save_dir.mkdir(parents=True, exist_ok=True)
            for suffix in (".png", ".pdf"):
                fig.savefig(save_dir / f"expert_agreement_{cell_type}{suffix}",
                            dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--save", type=Path, metavar="DIR",
                        help="also save the figures as PNG and PDF to DIR")
    main(parser.parse_args().save)

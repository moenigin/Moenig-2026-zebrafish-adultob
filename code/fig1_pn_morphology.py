"""Fig. 1: morphology of principal neuron (PN) classes.

Total dendritic length, soma volume and tip ratio per class (small,
intermediate and large mitral cells (MC), and RC).

Input:  data/fig1_pn_morphology.csv
Usage:  python code/fig1_pn_morphology.py            # show the figures
        python code/fig1_pn_morphology.py --save DIR  # also save PNG and PDF
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from common import DATA_DIR, PN_CLASSES, class_panel, set_style

# (column in the csv, y axis label, fixed power of ten or None, file name)
PANELS = [
    ("total_length", r"length [$\mu$m]", 3, "fig1_pn_length"),
    ("soma_vol", r"soma vol. [$\mu$m$^3$]", 2, "fig1_pn_soma_volume"),
    ("tip_ratio", "tip ratio", None, "fig1_pn_tip_ratio"),
]


def main(save_dir=None):
    set_style()
    pn = pd.read_csv(DATA_DIR / "fig1_pn_morphology.csv")
    print("Neurons per class:")
    print(pn["type_detail"].value_counts().reindex(PN_CLASSES).to_string())

    for column, ylabel, exponent, name in PANELS:
        fig, ax = plt.subplots(figsize=(3.4, 3.6))
        class_panel(ax, pn, column, ylabel, exponent)
        fig.tight_layout()
        if save_dir is not None:
            save_dir.mkdir(parents=True, exist_ok=True)
            for suffix in (".png", ".pdf"):
                fig.savefig(save_dir / f"{name}{suffix}", dpi=300,
                            bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--save", type=Path, metavar="DIR",
                        help="also save the figures as PNG and PDF to DIR")
    main(parser.parse_args().save)

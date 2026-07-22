# Moenig-2026-zebrafish-adultob

This repository serves as the digital appendix and user guide for the adult zebrafish olfactory bulb dataset associated with our [**publication**](https://www.biorxiv.org/content/10.64898/2026.07.13.738197v1). 

The complete volume, segmentations, and curated states are hosted publicly in Google Cloud Storage at **`gs://adultob-public`**.

---

## 1. Extended Documentation & Neuron Class Catalog

To complement the main manuscript, this repository provides extended supplementary documentation detailing the anatomical and morphological classifications of reconstructed neuron classes:

* [**Download/View Full Neuron Class Documentation (PDF)**](./detailed_neuron_description.pdf)) 
* [**Download Master Reconstructed Cells Inventory (CSV)**](./FR_neuron_information.csv) 
---

## 2. Dataset Overview & Cloud Volume Access

The data inside `gs://adultob-public` is stored in **Neuroglancer Precomputed** format. The multi-resolution chunked files are designed for programmatic access and chunk readers.

### Bucket Layout

| Path / Bucket Folder | Description |
| :--- | :--- |
| `gs://adultob-public/raw` | Electron Microscopy (EM) image volume |
| `gs://adultob-public/seg_260626_final_revision_nila/` | Proofread segmentation |
| `gs://adultob-public/info/FR_neuron_information.csv` | Metadata, coordinates, and cell classifications |
| `gs://adultob-public/states/` | Saved Neuroglancer JSON state configurations |

---

### Python Access via `cloud-volume`

You can stream and download raw image or segmentation subcubes directly into Python using [`cloud-volume`](https://github.com/seung-lab/cloud-volume).

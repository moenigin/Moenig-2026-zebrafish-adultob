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

---

## 3. Selected Views
Below are curated Neuroglancer views corresponding to specific cell classes discussed in the manuscript. Clicking a link will launch the interactive 3D viewer.
****
| Description | Link |
| :--- | :--- |
| Overview of all fully reconstructed neurons| [Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/all_fully_reconstructed_neurons.json) |
| Organisation of principal neurons in discrete glomeruli. Both fully and coarsely reconstructed neurons are selected | [Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/glomeruli.json)|
| All reconstructed principal neurons. Each layer holds examples for a different principal neuron subclass| [Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/principal_neurons.json) |
| All reconstructed examples of GLIN1s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/GLIN1.json)|
| All reconstructed examples of GLIN2s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/GLIN2.json)|
| All reconstructed examples of GLIN3s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/GLIN3.json)|
| All reconstructed examples of GLIN4s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/GLIN4.json)|
| All reconstructed examples of PLIN1s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/PLIN1.json)|
| All reconstructed examples of PLIN2s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/PLIN2.json)|
| All reconstructed examples of PLIN3s. Each layer holds examples for a different principal neuron subclass |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/PLIN3.json)|
| All reconstructed examples of PLIN4s. examples of different variants are shown in individual neuroglancer layers |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/PLIN4.json)|
| All reconstructed examples of DLIN1s. Each layer holds examples for a different principal neuron subclass |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/DLIN1.json)|
| All reconstructed examples of DLIN2s. Each layer holds examples for a different principal neuron subclass |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/DLIN2.json)|
| All reconstructed examples of DLIN3s |[Launch View](https://neuroglancer-demo.appspot.com/#!gs://adultob-public/states/DLIN3.json)|
****

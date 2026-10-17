# Moenig-2026-zebrafish-adultob

This repository serves as the digital appendix and user guide for the adult zebrafish olfactory bulb dataset associated with our [**publication**](https://elifesciences.org/reviewed-preprints/112715). 

The complete volume, segmentations, and curated states are hosted publicly in Google Cloud Storage at **`gs://adultob-public`**.

---

## 1. Extended Documentation & Neuron Class Catalog

To complement the main manuscript, this repository provides extended supplementary documentation detailing the anatomical and morphological classifications of reconstructed neuron classes:

* [**Download/View Full Neuron Class Documentation (PDF)**](./detailed_neuron_description.pdf)) 
* [**Download Reconstructed Cells Inventory (CSV)**](./FR_neuron_information.csv) 
---

## 2. Dataset Overview & Cloud Volume Access

The data is stored in Neuroglancer precomputed format, a chunked format for large volumes. It cannot be browsed like a folder or opened directly in a web browser. There are two ways to access it:

1. Interactive viewing (no installation): open one of the Neuroglancer links in the “Selected Views” section below.
2. Programmatic access: read volumes with cloud-volume (see the code example below). No Google account or credentials are required.

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
Example snippet to download a central subvolume:
```
import numpy as np
import matplotlib.pyplot as plt
from cloudvolume import CloudVolume, Bbox


EM_PATH  = "precomputed://gs://adultob-public/raw"
SEG_PATH = "precomputed://gs://adultob-public/seg_260626_final_revision_nila"

em  = CloudVolume(EM_PATH,  use_https=True, progress=True, fill_missing=True)
seg = CloudVolume(SEG_PATH, use_https=True, progress=True, fill_missing=True)

print("available mips:", em.available_mips)
print("resolution (nm), mip 0:", em.scales[0]["resolution"])
print("bounds (voxels), mip 0:", em.bounds)

# download central subvolume
mip = 0
size = (256, 256, 64)  # x, y, z in voxels
center = (em.bounds.minpt + em.bounds.maxpt) // 2
start = center - [s // 2 for s in size]
bbox = Bbox(start, start + size)

em_crop  = em.download(bbox, mip=mip)    # shape: (x, y, z, channel)
seg_crop = seg.download(bbox, mip=mip)

# plot overlay of first crop section
em_sl  = np.squeeze(em_crop[:, :, 0, 0])
seg_sl = np.squeeze(seg_crop[:, :, 0])

rng = np.random.default_rng(0)
ids = np.unique(seg_sl[seg_sl > 0])
colors = {i: rng.random(3) for i in ids}
overlay = np.zeros((*seg_sl.shape, 4))
for i in ids:
    overlay[seg_sl == i] = (*colors[i], 0.5)

plt.imshow(em_sl, cmap="gray")
plt.imshow(overlay)
plt.axis("off")
plt.show()
```
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

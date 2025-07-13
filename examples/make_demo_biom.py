#!/usr/bin/env python
"""
Generate a tiny demo BIOM (v2 HDF5) table that can be imported into QIIME 2.
"""

import numpy as np
import biom
from biom.util import biom_open   # thin h5py wrapper

samples = [f"S{i}" for i in range(1, 8)] + [f"N{i}" for i in range(1, 7)]
features = ["ASV1", "ASV2", "ASV3"]

rng = np.random.default_rng(42)
data = rng.integers(low=0, high=10, size=(len(features), len(samples)))
table = biom.Table(
    data,
    observation_ids=features,
    sample_ids=samples,
    table_id="demo-counts"
)

with biom_open("examples/data/table.biom", "w") as fh:
    table.to_hdf5(fh, generated_by="make_demo_biom.py")

print("✓ BIOM written to examples/data/table.biom")

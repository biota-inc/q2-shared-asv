#!/usr/bin/env python
"""
Generate a tiny demo BIOM (v2 HDF5) table that can be imported into QIIME 2.
"""

import numpy as np
import biom
from biom.util import biom_open   # thin h5py wrapper

samples  = ["S1", "S2", "N1", "N2"]
features = ["ASV1", "ASV2", "ASV3"]

data = np.array([
    [10,  0,  5,  2],
    [ 0,  8,  1,  0],
    [ 3,  3,  0,  7],
])

table = biom.Table(
    data,
    observation_ids=features,
    sample_ids=samples,
    table_id="demo-counts"
)

with biom_open("examples/data/table.biom", "w") as fh:
    table.to_hdf5(fh, generated_by="make_demo_biom.py")

print("✓ BIOM written to examples/data/table.biom")

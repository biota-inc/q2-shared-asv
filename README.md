# q2-shared-asv

**q2-shared-asv** is a [QIIME 2](https://qiime2.org) plugin that identifies *shared amplicon sequence variants (ASVs)* between two samples and returns a filtered `FeatureTable[RelativeFrequency]`.

## Installation

```bash
# 1 Activate the QIIME 2 conda environment
conda activate qiime2

# 2 Install the plugin directly from GitHub
pip install "git+https://github.com/biota-inc/q2-shared_asv.git"

# 3 Refresh the QIIME 2 plugin cache (required for dev-installed plugins)
qiime dev refresh-cache
````

You can confirm that the command is registered with:

```bash
qiime shared-asv --help
```

## Quick Start

The `qiime shared-asv compute` command identifies shared ASVs (Amplicon Sequence Variants) between two specific samples from a feature table. It filters based on a minimum relative frequency threshold and produces a new table containing only the ASVs shared by both samples.

### Use Case

This tool is useful for comparing microbial compositions between two samples to identify common taxa while excluding low-abundance noise.

### Example

```bash
qiime shared-asv compute \
  --i-table table.qza \
  --p-sample-a Sample1 \
  --p-sample-b Sample2 \
  --m-metadata-file metadata.tsv \
  --p-percentage 0.01 \
  --o-shared-asvs shared-asv-table.qza
```

This command computes shared ASVs between `Sample1` and `Sample2` that each have a relative frequency of at least 1%.

## Command Parameters Summary

| **Type**      | **Option**          | **Description**                                                                    | **Required** |
| ------------- | ------------------- | ---------------------------------------------------------------------------------- | ------------ |
| **Input**     | `--i-table`         | Feature table containing relative frequencies (`FeatureTable[RelativeFrequency]`). | ✅ Yes        |
| **Parameter** | `--p-sample-a`      | Sample ID for the first sample to compare.                                         | ✅ Yes        |
| **Parameter** | `--p-sample-b`      | Sample ID for the second sample to compare.                                        | ✅ Yes        |
| **Parameter** | `--m-metadata-file` | Sample metadata file (must contain `sample-id` column).                            | ✅ Yes        |
| **Parameter** | `--p-percentage`    | Minimum relative frequency threshold (float between 0 and 1).                      | ✅ Yes        |
| **Output**    | `--o-shared-asvs`   | Output feature table containing shared ASVs (`FeatureTable[RelativeFrequency]`).   | ✅ Yes        |

Would you like a Japanese translation or a visualization of the shared ASVs workflow next?

## End-to-end example

### 1 Generate a relative-frequency table

```bash
# Compute relative frequencies
qiime feature-table relative-frequency \
  --i-table analysis/table-no-unassigned-feature-filtered.qza \
  --o-relative-frequency-table analysis/relative_frequency.qza

# Summarize
qiime feature-table summarize \
  --i-table analysis/relative_frequency.qza \
  --o-visualization analysis/relative_frequency.qzv
```

### 2 Prepare a *pair map*

Create a **tab-delimited** text file called `shared_asv.txt`:

| Pair A | Pair B | Pair ID |
| ------ | ------ | ------- |
| S1     | N1     | 1       |
| S2     | N2     | 2       |
| S3     | N3     | 3       |
| S4     | N4     | 4       |
| S5     | N5     | 5       |

> **Tip:** End the file with a newline so that the last record is read correctly by `tail`.

### 3 Run the plugin for every pair

```bash
tail -n +2 shared_asv.txt | while IFS=$'\t' read -r pairA pairB pairID; do
  qiime shared-asv compute \
    --i-table analysis/relative_frequency.qza \
    --m-metadata-file metadata/sample-data.txt \
    --p-sample-a "$pairA" \
    --p-sample-b "$pairB" \
    --p-percentage 0.0001 \
    --o-shared-asvs "analysis/shared-asvs_${pairID}.qza"
done
```

### 4 (Optional) Filter each shared table by metadata

```bash
for i in $(seq 1 5); do
  qiime feature-table filter-samples \
    --i-table "analysis/shared-asvs_${i}.qza" \
    --m-metadata-file metadata/sample-data_skin.txt \
    --o-filtered-table "analysis/shared-asvs_${i}_skin.qza"
done
```

### 5 Merge the filtered tables

```bash
# Seed the merge with the first table
cp analysis/shared-asvs_1_skin.qza analysis/merged-table.qza

for i in $(seq 2 5); do
  qiime feature-table merge \
    --i-tables analysis/merged-table.qza \
    --i-tables "analysis/shared-asvs_${i}_skin.qza" \
    --o-merged-table analysis/tmp.qza
  mv analysis/tmp.qza analysis/merged-table.qza
done
```

### 6 Summarize and export

```bash
# Summarize
qiime feature-table summarize \
  --i-table analysis/merged-table.qza \
  --o-visualization analysis/merged-table.qzv

# Export to BIOM
qiime tools export \
  --input-path analysis/merged-table.qza \
  --output-path analysis/merged-table

# Convert BIOM → TSV
biom convert \
  -i analysis/merged-table/feature-table.biom \
  -o analysis/merged-table/feature-table.tsv \
  --to-tsv
```

## License

`q2-shared-asv` is distributed under the **BSD-3-Clause** license.
See [`LICENSE`](LICENSE) for the full text.

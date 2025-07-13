#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# examples/run_demo.sh
#
# End-to-end demonstration of the q2-shared-asv plugin using the tiny example
# data in examples/data/.  It:
#   0) Creates a toy BIOM table (if needed)
#   1) Imports it into QIIME 2
#   2) Converts counts → relative frequency
#   3) Computes shared ASVs for each pair listed in shared_asv.txt
#   4) (Optional) Filters those tables by a metadata subset ("skin")
#   5) Merges the filtered tables
#   6) Summarizes and exports the final merged table
#
# Requires an activated qiime2 conda env and the q2-shared-asv plugin.
# ---------------------------------------------------------------------------
set -euo pipefail

# -----------------------------  Paths & helpers  ----------------------------
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DATA_DIR="$SCRIPT_DIR/data"
OUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUT_DIR"

BIOM_FILE="$DATA_DIR/table.biom"
FMT_QZA="$DATA_DIR/table.qza"
REL_QZA="$DATA_DIR/relative_frequency.qza"

PAIR_MAP="$DATA_DIR/sample_shared_asv.txt"
META_ALL="$DATA_DIR/sample_metadata.tsv"
META_SKIN="$DATA_DIR/sample_metadata_skin_only.tsv"

# -----------------------------  Step 0  -------------------------------------
echo -e "\nStep 0 - Generate a demo BIOM (if absent)"
if [[ ! -f "$BIOM_FILE" ]]; then
  python "$SCRIPT_DIR/make_demo_biom.py"
else
  echo "✓ $BIOM_FILE already exists - skipping generation"
fi

# -----------------------------  Step 1  -------------------------------------
echo -e "\nStep 1 - Import to QIIME 2"
qiime tools import \
  --type 'FeatureTable[Frequency]' \
  --input-path "$BIOM_FILE" \
  --input-format BIOMV210Format \
  --output-path "$FMT_QZA"

# -----------------------------  Step 2  -------------------------------------
echo -e "\nStep 2 - Convert to relative frequency"
qiime feature-table relative-frequency \
  --i-table "$FMT_QZA" \
  --o-relative-frequency-table "$REL_QZA"

# -----------------------------  Step 3  -------------------------------------
echo -e "\nStep 3 - Compute shared ASVs for each pair"
while IFS=$'\t' read -r pairA pairB pairID || [[ -n "$pairA" ]]; do
  out_file="$OUT_DIR/shared_asvs_${pairID}.qza"
  echo "  • Pair $pairID: $pairA vs $pairB → $(basename "$out_file")"
  qiime shared-asv compute \
    --i-table "$REL_QZA" \
    --m-metadata-file "$META_ALL" \
    --p-sample-a "$pairA" \
    --p-sample-b "$pairB" \
    --p-percentage 0.0001 \
    --o-shared-asvs "$out_file"
done < <(tail -n +2 "$PAIR_MAP")   # skip header

# -----------------------------  Step 4  -------------------------------------
echo -e "\nStep 4 - Filter each shared table by metadata subset (skin)"
i_max=$(tail -n +2 "$PAIR_MAP" | wc -l | tr -d ' ')
for i in $(seq 1 "$i_max"); do
  qiime feature-table filter-samples \
    --i-table "$OUT_DIR/shared_asvs_${i}.qza" \
    --m-metadata-file "$META_SKIN" \
    --o-filtered-table "$OUT_DIR/shared_asvs_${i}_skin.qza"
done

# -----------------------------  Step 5  -------------------------------------
echo -e "\nStep 5 - Merge the filtered tables"
cp "$OUT_DIR/shared_asvs_1_skin.qza" "$OUT_DIR/merged_table.qza"
for i in $(seq 2 "$i_max"); do
  qiime feature-table merge \
    --i-tables "$OUT_DIR/merged_table.qza" \
    --i-tables "$OUT_DIR/shared_asvs_${i}_skin.qza" \
    --o-merged-table "$OUT_DIR/tmp_merged_table.qza"
  mv "$OUT_DIR/tmp_merged_table.qza" "$OUT_DIR/merged_table.qza"
done

# -----------------------------  Step 6  -------------------------------------
echo -e "\nStep 6 - Summarize and export"
qiime feature-table summarize \
  --i-table "$OUT_DIR/merged_table.qza" \
  --o-visualization "$OUT_DIR/merged_table.qzv"

qiime tools export \
  --input-path "$OUT_DIR/merged_table.qza" \
  --output-path "$OUT_DIR/merged_table_exported"

biom convert \
  -i "$OUT_DIR/merged_table_exported/feature-table.biom" \
  -o "$OUT_DIR/feature_table.tsv" \
  --to-tsv

echo -e "\nDemo completed!  Results are in $OUT_DIR"

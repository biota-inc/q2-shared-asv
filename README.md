# q2-shared_asv
## Installation
```bash
# Activate your qiime2
conda activate qiime2-2023.2
pip install git+https://github.com/biota-inc/q2-shared_asv.git
qiime dev refresh-cache
qiime --help
```

## Basic usage
```bash
qiime shared-asv compute --help

Inputs:
  --i-table ARTIFACT FeatureTable[RelativeFrequency]
                       The feature table containing the samples for which
                       shared ASVs should be computed.              [required]
Parameters:
  --p-sample-a TEXT    The first sample for which shared ASVs should be
                       computed.                                    [required]
  --p-sample-b TEXT    The second sample for which shared ASVs should be
                       computed.                                    [required]
  --m-metadata-file METADATA...
    (multiple          The sample metadata for sample-id
     arguments will    
     be merged)                                                     [required]
  --p-percentage PROPORTION Range(0, 1, inclusive_end=True)
                       The threshold for filtering shared ASVs based on
                       relative frequency.                          [required]
Outputs:
  --o-shared-asvs ARTIFACT FeatureTable[RelativeFrequency]
                       The resulting feature table containing the shared ASVs
                       between the two samples.                     [required]
```

## Example to run shared-asv plugin

For 16S rRNA amplicon sequencing, use `biota-inc/16S_pipeline` on Github and create `analysis/table-no-unassigned-feature-filtered.qza`.

1. Make a relative frequency table

```bash
# Compute the relative frequency of the features
qiime feature-table relative-frequency \
--i-table analysis/table-no-unassigned-feature-filtered.qza \
--o-relative-frequency-table analysis/relative_frequency.qza

# Summarize the relative frequency table
qiime feature-table summarize \                                   
--i-table  analysis/relative_frequency.qza \ 
--o-visualization  analysis/relative_frequency.qzv
```

2. Make a table like below and name it as shared_asv.txt (tab-demilited format txt file).
**Note: An empty last line is required!**

| Pair A | Pair B | Pair ID |
|--------|--------|---------|
| S1     | N1     | 1       |
| S2     | N2     | 2       |
| S3     | N3     | 3       |
| S4     | N4     | 4       |
| S5     | N5     | 5       |
|        |        |         |

3. Run the command below. This step generates the shared ASV table of each pair.  


```bash
#  If tab delimiters are not recognized well, enclose `$line` and `$PairA(B)` with Quotation Marks (for example, `$(echo "$line" |`)

tail -n +2 metadata/shared_asv.txt | while read line; do
    PairA=$(echo $line | awk -F'\t' '{print $1}' | tr -d '[:space:]')
    PairB=$(echo $line | awk -F'\t' '{print $2}' | tr -d '[:space:]')
    ID=$(echo $line | awk -F'\t' '{print $3}' | tr -d '[:space:]')

    qiime shared-asv compute \
        --i-table relative_frequency.qza \
        --m-metadata-file metadata/sample-data.txt \
        --p-sample-a $PairA \
        --p-sample-b $PairB \
        --p-percentage 0.0001 \
        --o-shared-asvs analysis/shared-asvs_$ID.qza
done
```

4. Filter samples for each shared-asvs file
```bash
# For example, filtering samples by using sample-data_skin.txt extracting only skin label of sample_type (if not, create this kind of file)

for i in {1..39}; do
qiime feature-table filter-samples \
  --i-table analysis/shared-asvs_${i}.qza \
  --m-metadata-file metadata/sample-data_skin.txt \
  --o-filtered-table analysis/shared-asvs_${i}_skin.qza
done
```

5. Merge the table files into one!
```bash
# Initialize the merged table with the first shared-asvs skin file
cp  analysis/shared-asvs_1_skin.qza  analysis/merged-table.qza

# Merge all shared-asvs skin files
for i in {2..39}; do
    qiime feature-table merge \
        --i-tables  analysis/merged-table.qza \
        --i-tables  analysis/shared-asvs_${i}_skin.qza \
        --o-merged-table  analysis/temp_merged-table.qza

     mv  analysis/temp_merged-table.qza  analysis/merged-table.qza
done
```

6. Final steps
```bash
# Summarize the merged table
qiime feature-table summarize \
        --i-table  analysis/merged-table.qza \
        --o-visualization  analysis/merged-table.qzv

# Export the merged table as a .biom file
qiime tools export \
  --input-path  analysis/merged-table.qza \
  --output-path  analysis/merged-table
  
# Convert the .biom file to a TSV format
biom convert \
  -i  analysis/merged-table/feature-table.biom \
-o  analysis/merged-table/table_biom.txt \
--to-tsv
```

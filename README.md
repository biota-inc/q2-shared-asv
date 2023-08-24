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
1. Make a table like below and name it as shared_asv.txt (tab-demilited format txt file).
**Note: An empty last line is required!**

| Pair A | Pair B | Pair ID |
|--------|--------|---------|
| S1     | N1     | 1       |
| S2     | N2     | 2       |
| S3     | N3     | 3       |
| S4     | N4     | 4       |
| S5     | N5     | 5       |
|        |        |         |

2. Run the command below. This step generates the shared ASV table of each pair.
```bash
tail -n +2 shared_asv.txt | while read line; do
    PairA=$(echo $line | awk -F'\t' '{print $1}' | tr -d '[:space:]')
    PairB=$(echo $line | awk -F'\t' '{print $2}' | tr -d '[:space:]')
    ID=$(echo $line | awk -F'\t' '{print $3}' | tr -d '[:space:]')

    qiime shared-asv compute \
        --i-table relative_frequency.qza \
        --m-metadata-file metadata/sample-data.txt \
        --p-sample-a $PairA \
        --p-sample-b $PairB \
        --p-percentage 0.0001 \
        --o-shared-asvs shared-asvs_$ID.qza
done
```
3. Merge the table files into one!
```bash
cp shared-asvs_1_skin.qza merged-table.qza

for i in {2..5}; do
    qiime feature-table merge \
        --i-tables merged-table.qza \
        --i-tables shared-asvs_${i}.qza \
        --o-merged-table temp_merged-table.qza

     mv temp_merged-table.qza merged-table.qza
done
```

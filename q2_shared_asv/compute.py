import biom
import qiime2
from q2_feature_table import (
    filter_features,
    filter_features_conditionally,
    filter_samples,
    merge,
)


def compute(
    table: biom.Table,
    sample_a: str,
    sample_b: str,
    metadata: qiime2.Metadata,
    percentage: float = 0.0001,
) -> biom.Table:
    """
    Return a feature table that contains only ASVs shared by *both* samples
    and whose relative frequency is at least *percentage* in each sample.

    Parameters
    ----------
    table : biom.Table
        Input feature table.
    sample_a : str
        Sample ID of the first sample.
    sample_b : str
        Sample ID of the second sample.
    metadata : qiime2.Metadata
        Sample metadata (required by `filter_samples` when SQL-style
        filtering is used).
    percentage : float, optional
        Minimum relative frequency (0.0 - 1.0) required in every sample
        to retain an ASV. Default is ``0.0001``.

    Returns
    -------
    biom.Table
        The filtered table of shared ASVs. If no ASVs meet the criteria,
        an explicitly empty table with the same sample IDs is returned.

    Raises
    ------
    ValueError
        When either ``sample_a`` or ``sample_b`` is not found in *table*.
    """

    # Subset the original table to the two samples of interest.
    table_a = filter_samples(table, ids=[sample_a])
    table_b = filter_samples(table, ids=[sample_b])

    # Combine the two one‐column tables into a 2-column table.
    merged = merge(
        tables=[table_a, table_b],
        overlap_method="error_on_overlapping_sample",
    )

    # Retain ASVs that are above the abundance threshold in *all* samples.
    shared_asvs = filter_features_conditionally(
        table=merged,
        abundance=percentage,
        prevalence=1,     # 100 % of samples (2/2)
    )

    # Preserve existing contract: return an empty table object (same samples)
    # when no ASVs survive the filters.
    if shared_asvs.shape[0] == 0:
        return filter_features(table=table_a, min_frequency=10)

    return shared_asvs

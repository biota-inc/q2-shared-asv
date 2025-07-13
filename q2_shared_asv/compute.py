import biom
import qiime2
from q2_feature_table import (
    filter_features, filter_features_conditionally, filter_samples, merge
)


def compute(table: biom.Table,
            sample_a: str,
            sample_b: str,
            metadata: qiime2.Metadata,
            percentage: float = 0.0001) -> biom.Table:
    """
    Compute the shared ASVs between two input samples.

    Parameters
    ----------
    table : biom.Table
        The feature table containing the data.
    sample_a : str
        The sample ID of the first sample to include in the analysis.
    sample_b : str
        The sample ID of the second sample to include in the analysis.
    metadata : qiime2.Metadata
        The metadata associated with the feature table.
    percentage : float, optional (default = 0.0001)
        Minimum relative frequency a feature must have (in each sample) to be
        retained.

    Returns
    -------
    shared_asvs : biom.Table
        A new feature table containing only the ASVs that are shared between
        the two input samples, and have a relative frequency greater than or
        equal to the input percentage.

    Raises
    ------
    ValueError
        If either of the input sample IDs are not present in the feature table.

    Notes
    -----
    The function first filters the input feature table to include only
    the two input samples, based on their sample IDs. It then merges
    the two filtered tables into a single table of shared ASVs, and filters
    this table to include only the ASVs with a relative frequency greater than
    or equal to the input percentage. If no ASVs meet this criteria, an empty
    feature table is returned.
    """

    table_a1 = table.copy()
    table_b1 = table.copy()

    # Filter samples based on the input sample IDs
    table_a = filter_samples(
        table_a1, where=f'\"sample-id\" IN ("{sample_a}")', metadata=metadata
    )
    table_b = filter_samples(
        table_b1, where=f'\"sample-id\" IN ("{sample_b}")', metadata=metadata
    )

    # Merge the filtered feature tables of sample A and sample B
    shared_asvs = merge(
        tables=[table_a, table_b],
        overlap_method='error_on_overlapping_sample'
    )

    # Filter features based on the input percentage
    shared_asvs = filter_features_conditionally(
        table=shared_asvs,
        abundance=percentage,
        prevalence=1
    )

    filtered_features_sample = shared_asvs.shape[0]

    if filtered_features_sample == 0:
        # Create an empty table with the same number of features as
        # the original table
        empty_table = filter_features(table=table_a, min_frequency=10)
        return empty_table
    else:
        return shared_asvs

from qiime2.plugin import Plugin, Str, Range, Float, Metadata
from q2_types.feature_table import FeatureTable, RelativeFrequency
from q2_shared_asv.compute import compute

plugin = Plugin(
    name='shared-asv',
    version='0.2.0',
    website='https://github.com/biota-inc/q2-shared_asv',
    package='q2_shared_asv',
    description='A QIIME 2 plugin for shared ASV analysis',
    short_description='Plugin for computing shared ASV.'
)

plugin.methods.register_function(
    function=compute,
    inputs={
        'table': FeatureTable[RelativeFrequency],
    },
    parameters={
        'sample_a': Str,
        'sample_b': Str,
        'metadata': Metadata,
        'percentage': Float % Range(
            0, 1, inclusive_start=True, inclusive_end=True
        ),
    },
    outputs=[
        ('shared_asvs', FeatureTable[RelativeFrequency])
    ],
    input_descriptions={
        'table': (
            'The feature table containing the samples for which shared '
            'ASVs should be computed.'
        )
    },
    parameter_descriptions={
        'sample_a': (
            'The first sample for which shared ASVs should be computed.'
        ),
        'sample_b': (
            'The second sample for which shared ASVs should be computed.'
        ),
        'metadata': 'The sample metadata for sample-id',
        'percentage': (
            'The threshold for filtering shared ASVs. Recommendation: 0.0001'
        )
    },
    output_descriptions={
        'shared_asvs': (
            'The resulting feature table containing the shared ASVs '
            'between the two samples.'
        )
    },
    name='Compute Shared ASVs',
    description=(
        'Compute the Shared ASVs between two samples within a FeatureTable'
    )
)

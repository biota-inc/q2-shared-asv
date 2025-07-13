from qiime2.plugin import Plugin, Str, Range, Float, Metadata
from q2_types.feature_table import FeatureTable, RelativeFrequency
from q2_shared_asv.compute import compute

plugin = Plugin(
    name='shared-asv',
    version='0.2.0',
    website=(
        'https://github.com/biota-inc/q2-shared-asv'
    ),
    package='q2_shared_asv',
    description='A QIIME 2 plugin for shared ASV analysis.',
    short_description='Plugin for computing shared ASVs.'
)

# Input, parameter, output type definitions
inputs = {
    'table': FeatureTable[RelativeFrequency],
}

parameters = {
    'sample_a': Str,
    'sample_b': Str,
    'metadata': Metadata,
    'percentage': Float % Range(
        0, 1,
        inclusive_start=True,
        inclusive_end=True,
    ),
}

outputs = [
    ('shared_asvs', FeatureTable[RelativeFrequency]),
]

# Descriptions
input_descriptions = {
    'table': (
        'Feature table containing the samples for which shared ASVs '
        'will be computed.'
    )
}

parameter_descriptions = {
    'sample_a': 'ID of the first sample.',
    'sample_b': 'ID of the second sample.',
    'metadata': 'Sample metadata containing the sample IDs.',
    'percentage': (
        'Minimum relative frequency threshold (default 0.0001).'
    ),
}

output_descriptions = {
    'shared_asvs': (
        'A feature table containing only the ASVs shared between the '
        'two samples.'
    )
}

# Register the method
plugin.methods.register_function(
    function=compute,
    inputs=inputs,
    parameters=parameters,
    outputs=outputs,
    input_descriptions=input_descriptions,
    parameter_descriptions=parameter_descriptions,
    output_descriptions=output_descriptions,
    name='Compute shared ASVs',
    description='Computes ASVs shared between two samples within a '
                'feature table.'
)

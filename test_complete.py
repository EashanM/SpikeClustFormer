import sys
import os
sys.path.append('cus_sort')

from cus_sort.custom_sorter import *
import spikeinterface.extractors as se
import spikeinterface.sorters as ss

print("Available sorters:", ss.available_sorters())

if 'myspikesorter' in ss.available_sorters():
    recording, _ = se.toy_example(duration=5, num_channels=4)
    sorting = ss.run_sorter(
        sorter_name='myspikesorter',
        recording=recording,
        output_folder='test_output',
        remove_existing_folder=True,
        verbose=True
    )
    print(f"✓ Success! Found {len(sorting.get_unit_ids())} units")

import spikeinterface.extractors as se
from spikeinterface.sorters import BaseSorter
import numpy as np
import json
from pathlib import Path

# Check if myspikesorter is available
try:
    import myspikesorter
    HAVE_MSS = True
    print(f"✓ myspikesorter package imported: {myspikesorter.__version__}")
except ImportError as e:
    HAVE_MSS = False
    print(f"✗ Failed to import myspikesorter: {e}")

class MySpikeSorter(BaseSorter):
    sorter_name = 'myspikesorter'
    installed = HAVE_MSS
    
    _default_params = {
        'detect_threshold': 5.0,
        'freq_min': 300,
        'freq_max': 6000,
        'num_workers': None,
        'clustering_method': 'kmeans'
    }
    
    _params_description = {
        'detect_threshold': 'Threshold for spike detection',
        'freq_min': 'High-pass filter cutoff',
        'freq_max': 'Low-pass filter cutoff',
        'num_workers': 'Number of workers',
        'clustering_method': 'Clustering method'
    }
    
    installation_mesg = "pip install myspikesorter"
    
    @classmethod
    def is_installed(cls):
        return HAVE_MSS
    
    @classmethod
    def get_sorter_version(cls):
        if HAVE_MSS:
            return myspikesorter.__version__
        return "unknown"
    
    @classmethod
    def _setup_recording(cls, recording, output_folder, params, verbose):
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        recording_file = output_folder / 'recording.dat'
        traces = recording.get_traces()
        traces_int16 = (traces * 1000).astype(np.int16)
        traces_int16.tofile(recording_file)
        
        params_file = output_folder / 'params.json'
        sorter_params = {
            'data_file': str(recording_file),
            'sampling_rate': recording.get_sampling_frequency(),
            'num_channels': recording.get_num_channels(),
            'detect_threshold': params['detect_threshold'],
            'freq_min': params['freq_min'],
            'freq_max': params['freq_max'],
            'clustering_method': params['clustering_method']
        }
        with open(params_file, 'w') as f:
            json.dump(sorter_params, f, indent=2)
    
    @classmethod
    def _run_from_folder(cls, output_folder, params, verbose):
        output_folder = Path(output_folder)
        params_file = output_folder / 'params.json'
        
        with open(params_file, 'r') as f:
            sorter_params = json.load(f)
        
        sorting_result = myspikesorter.run_sorting(
            data_file=sorter_params['data_file'],
            sampling_rate=sorter_params['sampling_rate'],
            detect_threshold=sorter_params['detect_threshold'],
            output_folder=str(output_folder),
            verbose=verbose
        )
        
        spike_times_file = output_folder / 'spike_times.npy'
        spike_clusters_file = output_folder / 'spike_clusters.npy'
        np.save(spike_times_file, sorting_result['spike_times'])
        np.save(spike_clusters_file, sorting_result['spike_clusters'])
    
    @classmethod
    def _get_result_from_folder(cls, output_folder):
        output_folder = Path(output_folder)
        
        spike_times = np.load(output_folder / 'spike_times.npy')
        spike_clusters = np.load(output_folder / 'spike_clusters.npy')
        
        with open(output_folder / 'params.json', 'r') as f:
            params = json.load(f)
        sampling_rate = params['sampling_rate']
        
        # Create NumpySorting using from_times_labels
        sorting = se.NumpySorting.from_times_labels(
            times_list=spike_times,
            labels_list=spike_clusters,
            sampling_frequency=sampling_rate
        )
        
        return sorting

# Register the sorter
from spikeinterface.sorters import sorter_dict
sorter_dict['myspikesorter'] = MySpikeSorter

print(f"Registered myspikesorter. Installed: {HAVE_MSS}")

# Verify registration
import spikeinterface.sorters as ss
if 'myspikesorter' in ss.available_sorters():
    print("✓ myspikesorter successfully registered!")
else:
    print("✗ myspikesorter registration failed!")

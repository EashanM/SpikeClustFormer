import numpy as np
import os
import json

def run_sorting(data_file, sampling_rate, detect_threshold=5.0, output_folder=None, verbose=False):
    """
    Simple threshold-based spike detection and clustering.
    Each detected spike is assigned to the channel with the largest amplitude.
    The number of channels is read from the params.json file in the output folder.
    """
    # --- Get number of channels from params.json ---
    if output_folder is None:
        raise ValueError("output_folder must be provided to read params.json for channel count.")
    params_path = os.path.join(output_folder, "params.json")
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"Could not find params.json at {params_path}")
    with open(params_path, "r") as f:
        params = json.load(f)
    n_channels = int(params["num_channels"])  # Ensure it's an int

    dtype = np.int16

    # Get the file size and infer the number of samples
    n_bytes = os.path.getsize(data_file)
    n_samples = n_bytes // (np.dtype(dtype).itemsize * n_channels)
    data = np.memmap(data_file, dtype=dtype, mode='r', shape=(n_samples, n_channels))
    data = data.astype(np.float32) / 1000  # Convert back to microvolts

    # Simple threshold detection on all channels
    spike_times = []
    spike_clusters = []
    for ch in range(n_channels):
        channel_data = data[:, ch]
        threshold = detect_threshold * np.std(channel_data)
        crossings = np.where(channel_data < -threshold)[0]  # Negative peaks
        # Avoid double-counting spikes that are too close (refractory period)
        refractory = int(0.001 * sampling_rate)  # 1 ms refractory
        if len(crossings) > 0:
            keep = [crossings[0]]
            for idx in crossings[1:]:
                if idx - keep[-1] > refractory:
                    keep.append(idx)
            spike_times.extend(keep)
            spike_clusters.extend([ch] * len(keep))

    # Convert to arrays and sort by spike time
    spike_times = np.array(spike_times)
    spike_clusters = np.array(spike_clusters)
    sort_idx = np.argsort(spike_times)
    spike_times = spike_times[sort_idx]
    spike_clusters = spike_clusters[sort_idx]

    if verbose:
        print(f"Detected {len(spike_times)} spikes across {n_channels} channels (clusters).")

    return {'spike_times': spike_times, 'spike_clusters': spike_clusters}

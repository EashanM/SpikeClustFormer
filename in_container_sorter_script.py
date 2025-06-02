
import json
from pathlib import Path
from spikeinterface import load
from spikeinterface.sorters import run_sorter_local

if __name__ == '__main__':
    # this __name__ protection help in some case with multiprocessing (for instance HS2)
    # load recording in container
    json_rec = Path('/Users/eashanmonga/PycharmProjects/STATS320_FinalProject/in_container_recording.json')
    pickle_rec = Path('/Users/eashanmonga/PycharmProjects/STATS320_FinalProject/in_container_recording.pickle')
    if json_rec.exists():
        recording = load(json_rec)
    else:
        recording = load(pickle_rec)

    # load params in container
    with open('/Users/eashanmonga/PycharmProjects/STATS320_FinalProject/in_container_params.json', encoding='utf8', mode='r') as f:
        sorter_params = json.load(f)

    # run in container
    output_folder = '/Users/eashanmonga/PycharmProjects/STATS320_FinalProject/mountainsort5_output'
    sorting = run_sorter_local(
        'mountainsort5', recording, output_folder=output_folder,
        remove_existing_folder=False, delete_output_folder=False,
        verbose=False, raise_error=True, with_output=True, **sorter_params
    )
    sorting.save(folder='/Users/eashanmonga/PycharmProjects/STATS320_FinalProject/mountainsort5_output/in_container_sorting')

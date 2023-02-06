import sys
from pathlib import Path

module_path = str(Path.cwd().parents[0] / "network_models/soundstream_models_and_utils")
if module_path not in sys.path:
    sys.path.append(module_path)

sys.path.insert(0, "/home/ckwdani/Programming/Projects/masterarbeit/Jupyter/mainProject")
import network_models.soundsream_models_and_utils.ss_encoded_dataset as ssed

dataset = ssed.ss_encoded_dataset_full(
    directory_cafe="/home/ckwdani/Music/emotionDatasets/converted_mono/cafe",
    directory_tess="/home/ckwdani/Music/emotionDatasets/converted_mono/tess",
     directory_ravdess="/home/ckwdani/Music/emotionDatasets/converted_mono/RAVDESS Audio_Speech_Actors_01-24",
     directory_mesd="/home/ckwdani/Music/emotionDatasets/converted_mono/mesd",
    device="cuda",
    sound_stream_path="../notebooks/content/soundstream/vers0.7.4/01_Soundstream_7_x_new_libri_full/5_3250/soundstream.3250.pt")
dataset.saveEncoding("../notebooks/content/data/allEncodings.pkl")
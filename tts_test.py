# from TTS.api import TTS
import os
from TTS.utils.manage import ModelManager
from TTS.utils.generic_utils import get_user_data_dir

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts



model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
ModelManager().download_model(model_name)

model_path = os.path.join(get_user_data_dir("tts"), model_name.replace("/", "--"))
print("XTTS downloaded")
print(f"MODEL PATH: {model_path}")

config = XttsConfig()
config.load_json(os.path.join(model_path, "config.json"))

model = Xtts.init_from_config(config)
model.load_checkpoint(
    config,
    checkpoint_path=os.path.join(model_path, "model.pth"),
    vocab_path=os.path.join(model_path, "vocab.json"),
    speaker_file_path=os.path.join(model_path, "speakers_xtts.pth"),
    eval=True,
    use_deepspeed=True,
)
print('model loaded')
# model_path="tts_models/multilingual/multi-dataset/xtts_v2"
# model = TTS(model_path)
# config = XttsConfig("./models/XTTS-v2/config.json")
# print(f"CONFIG: {config}")
# model = Xtts.init_from_config(config)
# model.load_checkpoint(config, checkpoint_dir=f"./models/XTTS-v2", use_deepspeed=False) #if set to true requires CUDA_HOME variable, doesn't seem to work on CPU but deepspeed alone can be used with it. To be explored.
print(type(model))
print(model.__dict__.keys())

print()
print("TEST RUN")
print()

model.test_run()
import io
import time

import pyaudio
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

print("Loading model...")
config = XttsConfig()
config.load_json("../XTTS-v2/config.json")
model = Xtts.init_from_config(config)
# model.load_checkpoint(config~, checkpoint_dir="../XTTS-v2/", use_deepspeed=True)
model.load_checkpoint(config, checkpoint_dir="../XTTS-v2/")
model.cuda()

print("Computing speaker latents...")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["../XTTS-v2/samples/en_sample.wav"])

print("Inference...")
t0 = time.time()
chunks = model.inference_stream(
    "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind "
    "texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean.",
    "en",
    gpt_cond_latent,
    speaker_embedding,
    stream_chunk_size=1024,
)

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=24000,
    output=True,
)

wav_chuncks = []
for i, chunk in enumerate(chunks):
    if i == 0:
        print(f"Time to first chunk: {time.time() - t0}")
    buff = io.BytesIO()
    torchaudio.save(buff, torch.cat([chunk]).squeeze().unsqueeze(0).cpu(), sample_rate=24000, format='wav')
    stream.write(buff.getvalue())
    print(f"Received chunk {i} of audio length {chunk.shape[-1]}")
    wav_chuncks.append(chunk)
wav = torch.cat(wav_chuncks, dim=0)
buff = io.BytesIO()
torchaudio.save(buff, wav.squeeze().unsqueeze(0).cpu(), 24000, format='wav')
stream.write(buff.getvalue())

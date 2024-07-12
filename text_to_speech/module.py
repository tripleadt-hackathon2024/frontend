import torch
from TTS.api import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"


def text_to_speach(text: str) -> str:
    tts = TTS("tts_models/en/ljspeech/vits").to(device)
    return tts.tts_to_file(text=text, file_path='./temp/output.wav')

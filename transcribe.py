from faster_whisper import WhisperModel
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model_size = "large-v3"

model = WhisperModel(model_size, device="cuda", compute_type="float16")


def transcribe_text(file_path: str):
    segments, info = model.transcribe(file_path, beam_size=5)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    result = [["%.2f" % segment.start, "%.2f" % segment.end, segment.text + "."] for segment in segments]
    return result

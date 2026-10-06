import os
import subprocess
import sys
import warnings
warnings.filterwarnings("ignore")  # many warnings loading kokoro

SPEED: float = 1.3
VOICE: str = "am_echo"  
# US-female (af): af_sarah, af_bella,   af_nicole, af_alloy, af_nova, af_sky
# US-male   (am): am_adam,  am_michael, am_fenrir, am_echo,  am_onyx, am_puck

MODEL_CACHE_PATH: str = 'model_files/tts_cache'
TEMP_AUDIO_FILE: str = 'model_files/tts_cahce/temp_out.wav'


os.environ["HF_HOME"] = MODEL_CACHE_PATH

from kokoro import KPipeline  # type: ignore
import soundfile as sf

pipeline: KPipeline
PIPELINE_LOADED: bool = False


def load_pipeline():
    global pipeline
    global PIPELINE_LOADED

    pipeline = KPipeline(lang_code=VOICE[0], repo_id='hexgrad/Kokoro-82M') 
    PIPELINE_LOADED = True


def _gen_tts(text: str, voice: str = VOICE, speed: float = SPEED):
    if not PIPELINE_LOADED:
        load_pipeline()

    generator = pipeline(  # type: ignore
        text,
        voice=voice,
        speed=speed
    )

    for _, (_, _, audio) in enumerate(generator):
        sf.write(TEMP_AUDIO_FILE, audio, 24000)


def _play_audio(file):
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(file, winsound.SND_FILENAME)
    elif sys.platform == "darwin":  # macOS
        subprocess.run(["afplay", file])
    elif sys.platform.startswith("linux"):  # Linux
        subprocess.run(["aplay", file])
    else:
        print('No fitting audio player found :(')


def gen_and_play_tts(text):
    _gen_tts(text)
    _play_audio(TEMP_AUDIO_FILE)
    os.remove(TEMP_AUDIO_FILE)



if __name__ == '__main__':
    text = "Hello everybody, how are you doing?"
    gen_and_play_tts(text)
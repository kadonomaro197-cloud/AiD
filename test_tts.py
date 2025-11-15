from TTS.api import TTS

# Pick a model (downloads automatically first time)
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")

# Generate speech
tts.tts_to_file(
    text="Hello, I am AID. Testing my offline voice.",
    file_path="test.wav"
)

print("✅ Saved test.wav with AID's voice")

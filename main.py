import openai
import speech_recognition as sr
import pyaudio
import wave
import base64
import json

# di laptop speech to perintah open ai
openai.api_key = "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"

# Record Audio
def record_audio(duration=5, filename="output.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Convert Audio to Text
def speech_to_text(filename):
    r = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)

    return text

# Generate Response from OpenAI API
def generate_response(prompt):
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text

# Convert Text to Audio
def text_to_speech(text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Please convert this text to speech: {text}",
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )

    audio_base64 = response.choices[0].audio

    return audio_base64

# Play Audio
def play_audio(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    wf = wave.open("response.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(audio_bytes)
    wf.close()

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, output=True)

    data = audio_bytes

    print("Playing...")

    while len(data) > 0:
        stream.write(data[:CHUNK])
        data = data[CHUNK:]

    print("Finished playing.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

# Main Loop
while True:
    record_audio()
    text = speech_to_text("output.wav")
    response = generate_response(text)
    audio_base64 = text_to_speech(response)
    play_audio(audio_base64)

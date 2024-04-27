import pyaudio
import wave
import numpy as np
import sys
from openai import OpenAI
import json
import control_device

client = OpenAI()
assistant = client.beta.assistants.retrieve("asst_JlEVub4O37OjgB8LxmVXPrSv")
thread = client.beta.threads.create()


def main():
    audio_file = "output/captured_audio.wav"
    text_file = "output/output_text.txt"
    
    list_audio_devices()
    DEVICE_INDEX = choose_input_device()
    while True:
        # capture
        capture_audio(audio_file, DEVICE_INDEX)
        # run speech to text
        text = speech_to_text(audio_file, text_file)
        # classify text
        # with open(text_file, "r") as f:
        #     text = f.read()
        ad_confidence = classify_text(text)
        # action (if needed)
        control_device.take_action(ad_confidence)
        
def classify_text(text):
    print("Classifying text: ", text)
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="classify the text and return a confidence value in json {confidence: [0,1]} format",
    )
    print("Run status: ", run.status)
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(messages)
        # pares the response to get the confidence value
        json_str = messages.data[0].content[0].text.value
        confidence = json.loads(json_str)["confidence"]
        print("Confidence: ", confidence)
        return confidence
    else:
        print(run.status)
    
def speech_to_text(audio_file, text_file):
    # open AI speech to text
    audio_file= open(audio_file, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
    print("Text result: ", transcription.text)
    # save to file for debugging
    with open(text_file, "w") as f:
        f.write(transcription.text)
    return transcription.text
    
def list_audio_devices():
    """
    List available audio devices.
    """
    p = pyaudio.PyAudio()
    num_devices = p.get_device_count()
    print("Available audio devices:")
    for i in range(num_devices):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}: {device_info}) \n")
    p.terminate()

def choose_input_device():
    """
    Prompt the user to choose the input device.
    """
    device_index = -1
    while device_index < 0:
        try:
            device_index = int(input("Enter the index of the input device to record from: "))
            p = pyaudio.PyAudio()
            device_info = p.get_device_info_by_index(device_index)
            if device_info['maxInputChannels'] == 0:
                print("Selected device does not support input. Please choose another device.")
                device_index = -1
            p.terminate()
        except ValueError:
            print("Invalid input. Please enter a valid device index.")
    return device_index    

def capture_audio(output_file, device_index):    
    # Set parameters for audio recording
    
    CHANNELS = 1  # Number of audio channels (2 for stereo)
    RATE = 44100  # Sample rate (samples per second)
    DURATION = 10  # Duration of recording (in seconds)
    chunk_size=1024
    format=pyaudio.paInt16
    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open a stream to capture audio from the specified input device
    stream = audio.open(format=format,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=chunk_size)

    print("Recording...")

    frames = []

    # Record audio data in chunks and store it in frames
    for _ in range(int(RATE / chunk_size * DURATION)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Recording stopped.")

    # Close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the captured audio to a WAV file
    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    print(f"Audio saved as '{output_file}'.")

if __name__ == "__main__":
    main()
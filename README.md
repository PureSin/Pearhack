# OpenAIHack

conda activate hack

To run: 

python main.py

then select your input audio (0 most of the time)
## How it works

This uses 2 OpenAI API

Step 1: Capture Audio -> get transcript
Using pyaudio

Captures the device's audio input as a wav file.

Step 2: transcript -> classification [0,1] value

The wav file gets send to openAI speech to text to get the transcript.

The transcript text is passed to openAI assitant instructed to provide a single confidence on if the text is an ad read. 

Step 3: control the device

if ad read then decrease volume and birghtness. Bring it back once the ad is over. 

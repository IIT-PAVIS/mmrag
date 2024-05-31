"""
Transcribe audio file to text with chunking.
Author: Pavis
Date: 25/03/2024
"""

import argparse
import speech_recognition as sr
from pydub import AudioSegment
import io

def chunk_audio(audio, chunk_length_ms=60000):
    """
    Splits the audio file into chunks of a specified length.
    """
    chunk_length = len(audio)
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, chunk_length, chunk_length_ms)]
    return chunks

def transcribe_audio_chunk(chunk, recognizer, language="it-IT"):
    """
    Transcribes a single chunk of audio.
    """
    with io.BytesIO() as raw_audio_data:
        chunk.export(raw_audio_data, format="wav")
        raw_audio_data.seek(0)
        with sr.AudioFile(raw_audio_data) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=language)
                return text
            except sr.UnknownValueError:
                return "Google Web Speech API could not understand audio"
            except sr.RequestError as e:
                return f"Could not request results from Google Web Speech API; {e}"

def chunk_and_transcribe(input_file, output_file, language="it-IT", chunk_length_ms=60000):
    """
    Splits the input audio file into chunks and transcribes each chunk.
    """
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(input_file)
    chunks = chunk_audio(audio, chunk_length_ms)

    transcribed_text = []
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        text = transcribe_audio_chunk(chunk, recognizer, language)
        # append timestamp to the transcribed text
        text = f"##[{i*chunk_length_ms} - {(i+1)*chunk_length_ms}]: {text}"
        transcribed_text.append(text)

    with open(output_file, 'w') as f:
        for text in transcribed_text:
            f.write(text + '\n')

    print(f"Transcription saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio file to text with chunking.")
    parser.add_argument("input_file", type=str, help="Path to the input audio file.")
    parser.add_argument("output_file", type=str, help="Path to the output text file.")
    parser.add_argument("--chunk-length-ms", type=int, default=20000, help="Length of each audio chunk in milliseconds.")
    
    args = parser.parse_args()

    chunk_and_transcribe(args.input_file, args.output_file, chunk_length_ms=args.chunk_length_ms)

if __name__ == "__main__":
    main()

"""
Parallel Audio Transcription Script

This script transcribes multiple audio files to text in parallel, using the speech_recognition library and the Google Web Speech API. It is designed to process WAV audio files concurrently, improving efficiency for bulk transcription tasks.

Requirements:
- An internet connection.
- speech_recognition library installed (use `pip install SpeechRecognition`).

Usage:
python parallel_transcribe_audio.py path/to/audio1.wav path/to/audio2.wav ...

Note:
- The accuracy of transcription depends on the clarity of the audio. Use high-quality, noise-free audio files for best results.
- The script currently handles WAV files. Additional formats may require conversion or extra handling not provided in this script.
"""

import concurrent.futures
import datetime
import os
import speech_recognition as sr
from speech_recognition import Recognizer
import sys

def transcribe_audio(audio_path):
    recognizer: Recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            output_text_path = audio_path[:-3] + 'txt'
            with open(output_text_path, "w") as f:
                f.write(text)
                print(f"PID:{os.getpid()} {datetime.datetime.now()} Transcription saved to {output_text_path}")
            return audio_path, text
    except FileNotFoundError:
        return audio_path, "Error: Audio file not found."
    except sr.UnknownValueError:
        return audio_path, "Error: Could not understand audio."
    except sr.RequestError as e:
        return audio_path, f"Error: Could not request results; {e}"

def process(audio_path):
    if audio_path[-3:] == 'wav':
        transcription = transcribe_audio(audio_path)
    # print(f"\nFile: {audio_path}\nTranscribed Text: {transcription}")
        return transcription

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parallel_transcribe_audio.py path/to/audio1.wav path/to/audio2.wav ...")
    else:
        audio_paths = sys.argv[1:]
        process(audio_paths)

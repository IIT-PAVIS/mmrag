
"""
Extract WAV files from video files using ffmpeg
Usage:
    python extract_audio.py --input <input_folder> --output <output_folder>
Author: Pavis
Date: 25/03/2024
"""

import os
import argparse
import subprocess

def extract_wav(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over files in input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + ".wav")

            # Invoke ffmpeg command
            subprocess.run(["ffmpeg", "-i", input_file, "-acodec", "pcm_s16le", "-ar", "16000", output_file])

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract WAV files from video files using ffmpeg")
    parser.add_argument("--input", default="input", help="Input folder path (default: 'input')")
    parser.add_argument("--output", default="output", help="Output folder path (default: 'output')")
    args = parser.parse_args()

    # Extract WAV files
    extract_wav(args.input, args.output)
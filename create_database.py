"""
Create a database of embeddings from a set of documents, storing it on faiss or chromaDB.
usage: create_database.py [-h] [--documents DOCUMENTS] [--target TARGET] [--extraction
EXTRACTION] [--transcription TRANSCRIPTION] [--description DESCRIPTION] [--concat
CONCAT] [--frequency FREQUENCY]

arguments:
    --documents DOCUMENTS
                            Path to the documents files
    --target TARGET       Path to the target files
    --extraction EXTRACTION
                            Extract sound from video for transcription
    --transcription TRANSCRIPTION
                            Transcribe the WAV file
    --description DESCRIPTION
                            Describe frames of video files
    --concat CONCAT       Concatenate transcription and description files
    --frequency FREQUENCY
                            frequency of the chunks (used in openai/postgresql approach only)

Author: Pavis
Date: 25/03/2024
"""
import argparse
#import argparse
#import subprocess
import os
import time

def main():
    parser = argparse.ArgumentParser(
        description='Process queries using console.py as command line')
    parser.add_argument('--documents', type=str,
                        help='Path to the documents files')
    parser.add_argument('--target', type=str, help='Path to the target files')
    parser.add_argument('--extraction', type=bool, default=True,
                        help='Extract sound from video for transcription')
    parser.add_argument('--transcription', type=bool,
                        default=True, help='Transcribe the WAV file')
    parser.add_argument('--description', type=bool,
                        default=True, help='Describe frames of video files')
    parser.add_argument('--concat', type=bool, default=True,
                        help='Concatenate transcription and description files')
    parser.add_argument('--frequency', type=int, default=20000,
                        help='frequency of the chunks (used in openai/postgresql approach only)')

    args = parser.parse_args()

    print("MMRAG creator", flush=True)

    start_time = time.time()

    # Get the list of documents in the folder
    documents_folder = args.documents
    documents = os.listdir(documents_folder)

    target_folder = args.target
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)


    # Iterate over each document and execute the command
    for document in documents:
        query = f"Document: {document}"

        # if document extension is not mp4, skip
        if document[-4:] != ".mp4":
            continue

        # extract sound from video for transcription
        # Remove the file extension
        document_name = os.path.splitext(document)[0]

        print(f"Processing {document}...", flush=True)

        # there is a text file with the same name of the video but txt extension, use it to put in concat command
        # change the extension from mp4 to txt, removing mp4 and adding txt
        header = document.replace(".mp4", ".txt")

        if args.extraction:
            print(f"Extracting sound from {document}...", flush=True)

            # Create the command to extract sound from video for transcription
            command = f"ffmpeg -i {documents_folder}/{document} -y -acodec pcm_s16le -ar 16000 {target_folder}/{document_name}.wav"

            print(command, flush=True)
            os.system(command)

            print(f"Sound extracted from {document}.", flush=True)
            print(
                f"Sound saved to {target_folder}/{document_name}.wav", flush=True)

        if args.transcription:
            print(f"Transcribing {document_name}.wav...", flush=True)

            # Transcribe the WAV file
            transcription_file = f"{target_folder}/{document_name}_transcription.txt"
            transcribe_command = f"python3 video2txt/transcribe.py --chunk-length-ms {args.frequency} {target_folder}/{document_name}.wav {transcription_file}"
            print(transcribe_command, flush=True)

            os.system(transcribe_command)

            print(f"Transcription saved to {transcription_file}", flush=True)
            print(
                f"Transcribing {document_name}.wav completed successfully.", flush=True)

        if args.description:
            print(f"Describing frames of {document}...", flush=True)

            # Describe frames of video files
            describe_command = f"python3 video2txt/video2desc.py --frequency {args.frequency} --video_file {documents_folder}/{document} | tee {target_folder}/{document_name}_descriptions.txt"
            print(describe_command, flush=True)

            os.system(describe_command)

            print(
                f"Descriptions saved to {target_folder}/{document_name}_descriptions.txt", flush=True)
            print(
                f"Describing frames of {document} completed successfully.", flush=True)

        if args.concat:
            print(f"Concatenating transcription and description files...", flush=True)

            # Concatenate transcription and description files
            concat_command = f"python3 video2txt/concat.py --description {target_folder}/{document_name}_descriptions.txt --transcription {target_folder}/{document_name}_transcription.txt --header {documents_folder}/{header} --output {target_folder}/{document_name}_merged.txt"
            print(concat_command, flush=True)

            os.system(concat_command)

            print(f"Concatenation completed successfully.", flush=True)

    print("All documents processed successfully.", flush=True)

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Overall processing time: {processing_time} seconds")


if __name__ == "__main__":
    main()

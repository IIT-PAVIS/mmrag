## video2txt 

Convert multimedia files in txt or pdf to be analyzed with RAG

# Toolchain

Given a video file:

ffmpeg -i input.mp4 -acodec pcm_s16le -ar 16000 output.wav

python3 extract_audio.py --input /home/dexmac/Downloads/videos/ --output /home/dexmac/Downloads/audios

python3 transcribe.py /home/dexmac/Pictures/illustrations/input/output.wav ./transcription_ts.txt

python3 video2desc.py --video_file /home/dexmac/Pictures/illustrations/input/video.mp4 | tee descriptions_ts.txt

python3 concat.py --description descriptions_ts.txt --description transcription_ts.txt --output merged_output.txt

python3 ./console/benchmark.py video2txt/merged_output.pdf | tee benchmark.md

python3 ./console/console.py --documents ./video2txt/merged_output.txt --queries "can you give me the summary ?"

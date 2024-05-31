"""
This script is used to scrape videos from the Italian Chamber of Deputies website.
It uses the get_video function from get_video.py to scrape videos from the website.
The script takes the following arguments:
    --begin: Start of the range
    --stop: Stop of the range
    --output_folder: Output folder path
    --base_url: Base URL of the video page
The script creates a folder if it does not exist and scrapes videos from the website.
The videos are saved in the output folder.

Author: Pavis 
Date: 25/03/2024
"""

import argparse
from get_video import get_video
import os

def main():
    parser = argparse.ArgumentParser(
        description='Scrape videos using get_video function')

    parser.add_argument('--begin', type=int, default=24495,
                        help='Start of the range')
    parser.add_argument('--stop', type=int, default=24497,
                        help='Stop of the range')
    parser.add_argument('--output_folder', default='.',
                        help='Output folder path')
    parser.add_argument('--base_url', type=str,
                        default='https://webtv.camera.it/evento', help='Base URL of the video page')

    args = parser.parse_args()

    # Create folder if it does not exist
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Scrape videos
    for video_id in range(args.begin, args.stop):
        url = f"{args.base_url}/{video_id}"
        get_video(url, args.output_folder)

# example usage: python scrape.py --begin 24495 --stop 24497 --output_folder ./videos

if __name__ == '__main__':
    main()

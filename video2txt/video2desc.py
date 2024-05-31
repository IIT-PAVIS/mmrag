"""
This script reads a video file and sends frames to a Gradio server for inference.
The server returns a description of the scene in the frame, which is displayed on the frame.
The script also calculates the percentage of motion between frames and displays it on the frame.
Author: Pavis
Date: 25/03/2024
"""

from moellava import MoeLLava
import argparse
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

#import httpcore
#setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')
from googletrans import Translator, LANGUAGES

def putTextWithAccents(img, text, position, font, fontSize, color):
    """
    Draws text with accents on an OpenCV image using Pillow.

    :param img: OpenCV image
    :param text: Text to draw
    :param position: Tuple (x, y) where the text starts
    :param font: Path to the .ttf font file
    :param fontSize: Size of the font
    :param color: Text color in RGB
    """
    # Convert the OpenCV image to an RGB image
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # Create a drawing context
    draw = ImageDraw.Draw(img_pil)

    # Define the font
    font = ImageFont.truetype(font, fontSize)

    # Draw the text
    draw.text(position, text, font=font, fill=color)

    # Convert back to OpenCV image
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    return img_cv


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description='Open and display a video file')

    # Add an argument for the video file path
    parser.add_argument('--video_file', type=str,
                        help='Path to the video file')

    parser.add_argument("--url", type=str, default="http://10.245.83.46:7860",
                        help="URL of the Gradio predict endpoint")

    parser.add_argument("--question", type=str,
                        default="can you describe deeply the scene?", help="Question about the image")

    parser.add_argument('--translate', action='store_true', default=True,
                        help='translator service activate')

    parser.add_argument('--language', type=str, default="it",
                        help='translator service language')

    parser.add_argument('--frequency', type=int, default=20000,
                        help='get a frame only ever frequency milliseconds')

    parser.add_argument('--motion_threshold', type=int, default=50,
                        help='motion threshold for the motion percentage evaluation')

    parser.add_argument('--output', type=str, default="output.mp4",
                        help='output video file')
    
    parser.add_argument('--show', type=bool, default=False,
                        help='show the video')
    
    parser.add_argument('--record', type=bool, default=False,
                        help='record the video')

    # Parse the command-line arguments
    args = parser.parse_args()

    client = MoeLLava(args.url)

    if args.translate:
        print("Translator service activate")
        google_translator = Translator()

    # Open the video file
    cap = cv2.VideoCapture(args.video_file)

    # Check if the video file was successfully opened
    if not cap.isOpened():
        print('Error opening video file')
        return

    # Open video recording file
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    stream = cv2.VideoWriter(args.output, fourcc, 30.0,
                             (int(cap.get(3)), int(cap.get(4))))

    previous_frame = None
    inference = "No inference now, wait for the first frame to be processed."
    percentage = 0
    old_timestamp = 0

    # Read and display frames from the video file
    while True:
        ret, frame = cap.read()

        # Check if a frame was successfully read
        if not ret:
            break

        # evaluate motion from a frame to another using image difference and print a percentage of motion
        if previous_frame is not None:
            difference = cv2.absdiff(frame, previous_frame)
            percentage = (difference > 50).sum() / \
                (difference.shape[0] * difference.shape[1]) * 100

        frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)

        # get a frame only every args.frequency seconds or at the first frame
        if (timestamp - old_timestamp) > args.frequency or previous_frame is None:
            client.send_hash()

            client.set_image(frame)
            client.send_request(args.question)

            inference = client.get_response()

            print("##[{0} - {1}]:".format(
                int(old_timestamp/1000)*1000, int(timestamp/1000)*1000), flush=True)

            if args.translate:
                response = google_translator.translate(
                    inference, src="en", dest=args.language)
                inference = response.text

            print(inference, flush=True)

            old_timestamp = timestamp

        # Display the frame with text overlay multiline splittihg the text every 100 character in lines and using little font
        lines = [inference[i:i+100] for i in range(0, len(inference), 100)]
        for i, line in enumerate(lines):
           frame = putTextWithAccents(frame, line, (50, 50 + 50 * i), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8, (255, 255, 255))

        if args.show or args.record:
            # Display percentage of motion, timestamp and frame number on the bottom left corner
            cv2.putText(frame, "Motion: {0:.2f}%".format(
                percentage), (50, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Frame: {0}".format(int(frame_number)), (
                50, frame.shape[0] - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Timestamp: {0}".format(int(timestamp)), (
                50, frame.shape[0] - 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Display the frame
        if args.show:
            cv2.imshow('Video', frame)

             # Wait for the 'q' key to be pressed to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        previous_frame = frame

        # Write the frame to the output video file
        if args.record:
            stream.write(frame)

    # Release the video file and close the window
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()


"""
This script allows you to interact with the OpenAI ChatGPT API for vision tasks.
The script can be used to send images to the API and receive descriptions of the images.
The script uses the requests library to communicate with the API.
The script uses the base64 library to encode and decode images.
The script uses the argparse library to parse command line arguments.
The script defines a ChatGPTVision class that contains methods to send images to the API.
The script also includes asynchronous methods to send images in a non-blocking manner.
The script can be used to send multiple images to the API.

Usage:
    python chatgpt_vision.py --api_key <api_key> --images_path <images_path> --message <message> --max_tokens <max_tokens>
Author: Pavis
Date: 25/03/2024
"""
import base64
import requests
import argparse
import os
import sys
import cv2
import threading
import time

class ChatGPTVision:
    def __init__(self, api_key):
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.response = ""

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def encode_frame(self, frame):
        # encode the frame to jpeg format
        ret, buffer = cv2.imencode('.jpg', frame)

        if ret:
            # encode the jpeg frame to base64 format
            return base64.b64encode(buffer).decode('utf-8')
        else:
            raise Exception("Could not encode frame")

    def analyze_frame(self, frame, message, max_tokens):
        base64_image = self.encode_frame(frame)

        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }

        text = {
            "type": "text",
            "text": message
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [image, text]
                }
            ],
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        # print(response.json())

        return response.json()['choices'][0]['message']['content']

    def analyze_frames(self, frames, message, max_tokens):

        content = []

        # adding frames
        for frame in frames:

            base64_image = self.encode_frame(frame)

            image = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }

            content.append(image)

        text = {
            "type": "text",
            "text": message
        }

        content.append(text)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        # print(response.json())

        return response.json()['choices'][0]['message']['content']

    def async_analyze_frame(self, frame, message, max_tokens):
        base64_image = self.encode_frame(frame)

        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }

        text = {
            "type": "text",
            "text": message
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [image, text]
                }
            ],
            "max_tokens": max_tokens
        }

        # because requests.post is blocking we need to use a different thread
        # to send the request to the OpenAI API

        thread = threading.Thread(target=self.async_request, args=(payload,))
        thread.start()

    def async_analyze_frames(self, frames, message, max_tokens):

        content = []

        # adding frames
        for frame in frames:

            base64_image = self.encode_frame(frame)

            image = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }

            content.append(image)

        text = {
            "type": "text",
            "text": message
        }

        content.append(text)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens
        }

        # because requests.post is blocking we need to use a different thread
        # to send the request to the OpenAI API

        thread = threading.Thread(target=self.async_request, args=(payload,))
        thread.start()

    def async_request(self, payload):
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        self.response = response.json()['choices'][0]['message']['content']

    def analyze_image(self, image_path, message, max_tokens):

        base64_image = self.encode_image(image_path)

        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }

        text = {
            "type": "text",
            "text": message
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [image, text]
                }
            ],
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        return response.json()['choices'][0]['message']['content']

    def async_analyze_image(self, image_path, message, max_tokens):
            
            base64_image = self.encode_image(image_path)
    
            image = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
    
            text = {
                "type": "text",
                "text": message
            }
    
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [image, text]
                    }
                ],
                "max_tokens": max_tokens
            }
    
            # because requests.post is blocking we need to use a different thread
            # to send the request to the OpenAI API
    
            thread = threading.Thread(target=self.async_request, args=(payload,))
            thread.start()

    def analyze_images(self, images, message, max_tokens):

        content = []

        # adding images
        for image in images:

            base64_image = self.encode_image(image)

            image = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }

            content.append(image)

        text = {
            "type": "text",
            "text": message
        }

        content.append(text)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        print(response.json())

        return response.json()['choices'][0]['message']['content']

    def async_analyze_images(self, images, message, max_tokens):

        content = []

        # adding images
        for image in images:

            base64_image = self.encode_image(image)

            image = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }

            content.append(image)

        text = {
            "type": "text",
            "text": message
        }

        content.append(text)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens
        }

        # because requests.post is blocking we need to use a different thread
        # to send the request to the OpenAI API

        thread = threading.Thread(target=self.async_request, args=(payload,))
        thread.start()

    def get_latest_response(self):
        return self.response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat with GPT-4 Vision API')

    # adding arguments

    parser.add_argument('--api_key', type=str,
                        default="",
                        help='OpenAI API Key')

    parser.add_argument('--images_path', type=str, required=True,
                        help='Path to image')
    
    parser.add_argument('--message', type=str, default='can you describe the image ? if a bus, this is in genoa',
                        help='Message to send to the API')

    parser.add_argument('--max_tokens', type=int, default=300,
                        help='Maximum number of tokens to generate')

    # parsing arguments
    args = parser.parse_args()

    if "," in args.images_path:
        images = args.images_path.split(",")
    else:
        images = [args.images_path]

    # checking if image is present or not
    for image in images:
        print(f'Checking {image}')
        if not os.path.exists(image):
            print(f'{image} not found')
            sys.exit()

    chatbot = ChatGPTVision(args.api_key)

    chatbot.async_analyze_images(images, args.message, args.max_tokens)

    # wait for the response to be ready
    while chatbot.get_latest_response() == "":
        time.sleep(1)

    print(chatbot.get_latest_response())
